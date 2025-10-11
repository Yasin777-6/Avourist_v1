import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings
from reportlab.lib import colors

logger = logging.getLogger(__name__)


def rubles_to_text(amount: int) -> str:
    """Return amount like '12 000 (двенадцать тысяч) руб.' with graceful fallback."""
    words = None
    try:
        from num2words import num2words  # type: ignore

        words = num2words(int(amount), lang="ru")
    except Exception:
        words = str(amount)
    formatted = f"{int(amount):,}".replace(",", " ")
    # If words fallback looks numeric, avoid redundant parentheses
    try:
        if str(words).strip().isdigit():
            return f"{formatted} руб."
    except Exception:
        pass
    return f"{formatted} ({words}) руб."


class ContractPDFGenerator:
    """
    Template-aware PDF filler using overlay drawing with ReportLab + PyPDF2.
    - Supports multiple PDF templates via lightweight layout introspection + defaults.
    - Draws: contract number/date (page 0), pricing block (default page 2), client fields (last page).
    - Coordinates are conservative defaults; can be extended with per-template overrides.
    """

    def __init__(self) -> None:
        # Optional per-template filename overrides (basename -> layout dict)
        # Extend as you calibrate coordinates for specific PDFs.
        self.overrides: Dict[str, Dict] = {
            # Calibrated for WITHOUT_POA, instance 2 based on HTML coordinates
            "Договор_без_представления_интересов_БЕЗ_ДОВЕРЕННОСТИ_на_2_инстанции.pdf": {
                "first_page": {
                    "contract_number": {"x": 280, "y": 740},  # After "Договор № "
                    "contract_date": {"x": 490, "y": 714},  # top:128px from bottom = ~714
                    "client_name_page1": {"x": 53, "y": 690},  # top:152px, red field
                },
                "pricing": {
                    "enabled": True,
                    "page_index": 1,  # Page 2 in HTML = index 1
                    "mode": "blanks",
                    # HTML coordinates converted: A4 height=842pt, y = 842 - top_px*0.75
                    "blanks": {
                        "total_amount": {"x": 590, "y": 31, "size": 11, "format": "digits"},  # top:1081
                        "prepayment": {"x": 466, "y": 15, "size": 11, "format": "digits"},  # top:1102
                    },
                },
                "pricing_page3": {
                    "enabled": True,
                    "page_index": 2,  # Page 3 in HTML = index 2
                    "mode": "blanks",
                    "blanks": {
                        "success_fee": {"x": 53, "y": 770, "size": 11, "format": "text"},  # top:33 on page 3
                        "docs_prep_fee": {"x": 53, "y": 747, "size": 11, "format": "text"},  # top:95
                    },
                },
                "client": {
                    "page_index": 4,  # Page 5 in HTML = index 4
                    "base_x": 481,
                    "start_y": 788,  # top:54px from bottom
                    "step": 16,
                    "max_width": 350,
                    "fields": {
                        "client_full_name": 0,
                        "birth_date": -1,
                        "birth_place": -2,
                        "passport": -3,
                        "registration_address": -5,
                        "phone": -10,
                        "email": -12,
                        "client_signature": -17,
                    },
                    "field_offsets": {
                        "client_full_name": 0,
                        "birth_date": 0,
                        "birth_place": 0,
                        "passport": 0,
                        "registration_address": 0,
                        "phone": 0,
                        "email": 0,
                        "client_signature": 0,
                    },
                },
            }
        }

        # Default font names (will be registered on demand)
        self.font_regular = "PDF_Arial"
        self.font_bold = "PDF_Arial_Bold"

    def _register_fonts(self) -> None:
        """Register a Cyrillic-capable TrueType font for ReportLab.
        Priority:
          1) settings.PDF_FONT_PATH / settings.PDF_FONT_BOLD_PATH
          2) Windows Arial (C:\\Windows\\Fonts)
          3) Fallback to Helvetica (may not render Cyrillic correctly)
        """
        registered = pdfmetrics.getRegisteredFontNames()
        if self.font_regular in registered and self.font_bold in registered:
            return

        # 1) Custom paths from settings
        custom_regular = getattr(settings, "PDF_FONT_PATH", None)
        custom_bold = getattr(settings, "PDF_FONT_BOLD_PATH", None)
        try:
            if custom_regular and Path(custom_regular).exists():
                pdfmetrics.registerFont(TTFont(self.font_regular, custom_regular))
            if custom_bold and Path(custom_bold).exists():
                pdfmetrics.registerFont(TTFont(self.font_bold, custom_bold))
        except Exception:
            logger.warning("Failed to register custom PDF fonts from settings; trying system fonts.")

        # 2) Windows Arial
        try:
            win_font_dir = Path("C:/Windows/Fonts")
            arial = win_font_dir / "arial.ttf"
            arial_bold = win_font_dir / "arialbd.ttf"
            if self.font_regular not in pdfmetrics.getRegisteredFontNames() and arial.exists():
                pdfmetrics.registerFont(TTFont(self.font_regular, str(arial)))
            if self.font_bold not in pdfmetrics.getRegisteredFontNames() and arial_bold.exists():
                pdfmetrics.registerFont(TTFont(self.font_bold, str(arial_bold)))
        except Exception:
            logger.warning("Failed to register Windows Arial fonts; falling back to Helvetica.")

        # 3) Final fallback: map to Helvetica names if TTF registration failed
        if self.font_regular not in pdfmetrics.getRegisteredFontNames():
            self.font_regular = "Helvetica"
        if self.font_bold not in pdfmetrics.getRegisteredFontNames():
            self.font_bold = "Helvetica-Bold"

    def _layout_for(self, template_path: str, num_pages: int) -> Dict:
        name = Path(template_path).name
        last_page_index = max(0, num_pages - 1)

        # Defaults tuned for our typical templates (A4 portrait):
        layout = {
            "first_page": {
                "contract_number": {"x": 280, "y": 740},
                "contract_date": {"x": 490, "y": 714},
                "client_name_page1": {"x": 53, "y": 690},
            },
            "pricing": {  # page index where pricing paragraph resides
                "enabled": False,
                "page_index": 2 if num_pages > 2 else 0,
                "base_x": 80,
                "base_y": 480,
                "line_h": 18,
            },
            "client": {  # last page
                "page_index": last_page_index,
                "base_x": 150,
                "start_y": 240,
                "step": 20,
                "fields": {
                    "client_full_name": 7,  # start_y + step * n
                    "birth_date": 6,
                    "birth_place": 5,
                    # passport series+number will be on one line
                    "passport": 4,
                    "registration_address": 3,
                    "phone": 2,
                    "email": 1,
                    "client_signature": 0,  # just text placeholder
                },
                # Optional per-field x offsets (dx) relative to base_x
                "field_offsets": {
                    "client_full_name": 0,
                    "birth_date": 0,
                    "birth_place": 0,
                    "passport": 0,
                    "registration_address": 0,
                    "phone": 0,
                    "email": 0,
                    "client_signature": 0,
                },
                # Optional signature image placement
                "signature": {
                    "max_w": 140,
                    "dx": 0,
                    "dy": -40,
                },
                # Contract date (some templates need it also on last page header)
                "last_page_date_xy": None,
            },
        }

        # Apply overrides if exist
        if name in self.overrides:
            for k, v in self.overrides[name].items():
                if isinstance(v, dict) and k in layout:
                    layout[k].update(v)  # shallow merge nested dicts
                else:
                    layout[k] = v

        return layout

    def _draw_pricing(self, can: canvas.Canvas, layout: Dict, data: Dict) -> None:
        price_cfg = layout["pricing"]
        mode = price_cfg.get("mode", "paragraph")

        # Optional debug grid for calibration
        if data.get("_debug_grid") or price_cfg.get("debug_grid"):
            self._draw_debug_grid(can)

        total_amount = data.get("total_amount")
        prepayment = data.get("prepayment")
        success_fee = data.get("success_fee")
        docs_prep_fee = data.get("docs_prep_fee")

        if total_amount is None and any(v is not None for v in (prepayment, success_fee, docs_prep_fee)):
            total_amount = sum([v or 0 for v in (prepayment, success_fee, docs_prep_fee)]) or 0

        can.setFont(self.font_regular, 11)

        if mode == "blanks":
            blanks = price_cfg.get("blanks", {})
            def fmt(value, style):
                if value is None:
                    return None
                try:
                    iv = int(value)
                except Exception:
                    return str(value)
                if style == "digits":
                    return f"{iv:,}".replace(",", " ")
                return rubles_to_text(iv)

            for key, value in {
                "total_amount": total_amount,
                "prepayment": prepayment,
                "success_fee": success_fee,
                "docs_prep_fee": docs_prep_fee,
            }.items():
                cfg = blanks.get(key)
                if not cfg:
                    continue
                text = fmt(value, cfg.get("format", "text"))
                if not text:
                    continue
                size = cfg.get("size", 11)
                try:
                    can.setFont(self.font_regular, size)
                except Exception:
                    pass
                can.drawString(cfg.get("x", 0), cfg.get("y", 0), text)
        else:
            # Paragraph mode (default, not used for overlapping templates)
            x = price_cfg.get("base_x", 80)
            y = price_cfg.get("base_y", 480)
            lh = price_cfg.get("line_h", 18)
            if total_amount is not None:
                can.drawString(x, y, "Стоимость услуг по договору в соответствии с п.1.1 настоящего Договора составляет")
                can.drawString(x + 10, y - lh, rubles_to_text(int(total_amount)))
                y -= lh * 3
                can.drawString(x, y, "Оплата производится в следующем порядке:")
                y -= lh
                if prepayment is not None:
                    can.drawString(x + 10, y, f"Предоплата: {rubles_to_text(int(prepayment))} — не позднее одного дня с даты подписания.")
                    y -= lh
                if success_fee is not None:
                    can.drawString(x + 10, y, f"Вознаграждение при положительном результате: {rubles_to_text(int(success_fee))}.")
                    y -= lh
                if docs_prep_fee is not None:
                    can.drawString(x + 10, y, f"5.1.1 Подготовка документов составляет: {rubles_to_text(int(docs_prep_fee))}.")
                    y -= lh
                can.drawString(x, y, "5.2. Заказчик компенсирует расходы Исполнителя на почтовые и курьерские услуги на основании выставленных счетов.")

    def _draw_client_fields(self, can: canvas.Canvas, layout: Dict, data: Dict) -> None:
        cfg = layout["client"]
        base_x = cfg["base_x"]
        start_y = cfg["start_y"]
        step = cfg["step"]
        field_dx = cfg.get("field_offsets", {})
        max_width = cfg.get("max_width")

        # Optional debug grid for calibration
        if data.get("_debug_grid") or cfg.get("debug_grid"):
            self._draw_debug_grid(can)

        def _fit_text(text: str) -> str:
            if not text or not max_width:
                return text
            try:
                width = pdfmetrics.stringWidth(text, self.font_regular, 11)
                if width <= max_width:
                    return text
                # truncate with ellipsis
                ell = "…"
                for i in range(len(text), 0, -1):
                    t = text[:i] + ell
                    if pdfmetrics.stringWidth(t, self.font_regular, 11) <= max_width:
                        return t
            except Exception:
                pass
            return text

        def draw_line(label_key: str, value: str) -> None:
            pos_mult = cfg["fields"].get(label_key)
            if pos_mult is not None:
                x = base_x + int(field_dx.get(label_key, 0))
                y = start_y + step * pos_mult
                can.drawString(x, y, _fit_text(value))

        can.setFont(self.font_regular, 11)
        draw_line("client_full_name", data.get("client_full_name", ""))
        draw_line("birth_date", data.get("birth_date", ""))
        draw_line("birth_place", data.get("birth_place", ""))
        passport_line = "{} {}".format(
            data.get("client_passport_series", ""), data.get("client_passport_number", "")
        ).strip()
        draw_line("passport", passport_line)
        draw_line("registration_address", data.get("client_address", ""))
        draw_line("phone", data.get("client_phone", ""))
        draw_line("email", data.get("email", ""))
        # signature text placeholder if provided
        draw_line("client_signature", data.get("client_signature", ""))

        # Optional signature image
        sig_path = data.get("signature_image")
        if sig_path:
            try:
                from PIL import Image  # type: ignore

                sig = Image.open(sig_path)
                sig_w, sig_h = sig.size
                max_w = cfg.get("signature", {}).get("max_w", 140)
                scale = max_w / float(sig_w or 1)
                draw_w = int(sig_w * scale)
                draw_h = int(sig_h * scale)
                sig_x = base_x + cfg.get("signature", {}).get("dx", 0)
                sig_y = start_y + cfg.get("signature", {}).get("dy", -40)
                can.drawImage(str(sig_path), sig_x, sig_y, width=draw_w, height=draw_h, mask='auto')
            except Exception:
                logger.warning("Signature image could not be drawn; skipping.")

    def _draw_first_page_header(self, can: canvas.Canvas, layout: Dict, data: Dict) -> None:
        cnf = layout["first_page"]
        contract_number = data.get("contract_number")
        contract_date = data.get("contract_date", datetime.now().strftime("%d.%m.%Y"))
        
        # Contract number and date
        can.setFont(self.font_bold, 12)
        if contract_number:
            can.drawString(cnf["contract_number"]["x"], cnf["contract_number"]["y"], f"{contract_number}")
        can.drawString(cnf["contract_date"]["x"], cnf["contract_date"]["y"], contract_date)
        
        # Client name on page 1 (red field)
        if "client_name_page1" in cnf:
            client_name = data.get("client_full_name", "")
            if client_name:
                can.setFont(self.font_regular, 12)
                can.setFillColor(colors.red)
                can.drawString(cnf["client_name_page1"]["x"], cnf["client_name_page1"]["y"], client_name)
                can.setFillColor(colors.black)

    def _normalize(self, data: Dict) -> Dict:
        """Normalize incoming keys to the expected names, accepting multiple aliases."""
        def first(*keys):
            for k in keys:
                v = data.get(k)
                if v not in (None, ""):
                    return v
            return None

        norm = dict(data)
        norm.setdefault("client_full_name", first("client_full_name", "full_name", "fio", "client_name") or "")
        norm.setdefault("client_passport_series", first("client_passport_series", "passport_series", "series") or "")
        norm.setdefault("client_passport_number", first("client_passport_number", "passport_number", "number") or "")
        norm.setdefault("client_address", first("client_address", "registration_address", "address") or "")
        norm.setdefault("client_phone", first("client_phone", "phone", "tel") or "")
        norm.setdefault("email", first("email") or "")
        norm.setdefault("birth_date", first("birth_date", "dob") or "")
        norm.setdefault("birth_place", first("birth_place", "pob") or "")
        norm.setdefault("client_signature", first("client_signature", "signature_text") or "")
        norm.setdefault("signature_image", first("signature_image", "signature_path"))

        # Pricing aliases
        ta = first("total_amount", "total_fee", "amount", "price", "total")
        if ta is not None:
            try:
                norm["total_amount"] = int(ta)
            except Exception:
                pass
        for dst, srcs in {
            "prepayment": ("prepayment", "advance", "deposit"),
            "success_fee": ("success_fee", "success_payment", "result_fee", "success"),
            "docs_prep_fee": ("docs_prep_fee", "docs_fee", "documents_fee"),
        }.items():
            v = first(*srcs)
            if v is not None:
                try:
                    norm[dst] = int(v)
                except Exception:
                    norm[dst] = v

        # Dates
        if not norm.get("contract_date"):
            norm["contract_date"] = datetime.now().strftime("%d.%m.%Y")

        return norm

    def generate(self, template_path: str, data: Dict, contract_number: Optional[str] = None) -> bytes:
        """
        Generate a filled PDF and return bytes.
        Expects data to include typical fields; missing ones are simply left blank.
        """
        # Read template
        existing_pdf = PdfReader(open(template_path, "rb"))
        num_pages = len(existing_pdf.pages)

        # Enrich and normalize data
        data = dict(data or {})
        if contract_number:
            data["contract_number"] = contract_number
        data = self._normalize(data)

        layout = self._layout_for(template_path, num_pages)

        # Ensure fonts are available for Cyrillic
        self._register_fonts()

        # Prepare overlays
        overlays = {}

        # First page overlay
        packet_first = io.BytesIO()
        can_first = canvas.Canvas(packet_first, pagesize=A4)
        self._draw_first_page_header(can_first, layout, data)
        can_first.save()
        packet_first.seek(0)
        overlays[0] = PdfReader(packet_first).pages[0]

        # Pricing overlay (if page within bounds)
        price_cfg = layout.get("pricing", {})
        price_page_index = price_cfg.get("page_index", 0)
        if price_cfg.get("enabled", True) and 0 <= price_page_index < num_pages:
            packet_price = io.BytesIO()
            can_price = canvas.Canvas(packet_price, pagesize=A4)
            self._draw_pricing(can_price, layout, data)
            can_price.save()
            packet_price.seek(0)
            overlays[price_page_index] = PdfReader(packet_price).pages[0]
        
        # Pricing page 3 overlay (for templates with split pricing)
        price_cfg3 = layout.get("pricing_page3", {})
        price_page3_index = price_cfg3.get("page_index", -1)
        if price_cfg3.get("enabled", False) and 0 <= price_page3_index < num_pages:
            packet_price3 = io.BytesIO()
            can_price3 = canvas.Canvas(packet_price3, pagesize=A4)
            self._draw_pricing_page3(can_price3, layout, data)
            can_price3.save()
            packet_price3.seek(0)
            overlays[price_page3_index] = PdfReader(packet_price3).pages[0]

        # Client overlay (last page)
        client_page_index = layout["client"]["page_index"]
        if 0 <= client_page_index < num_pages:
            packet_client = io.BytesIO()
            can_client = canvas.Canvas(packet_client, pagesize=A4)
            self._draw_client_fields(can_client, layout, data)
            can_client.save()
            packet_client.seek(0)
            overlays[client_page_index] = PdfReader(packet_client).pages[0]

        # Merge and output
        out = PdfWriter()
        for idx, page in enumerate(existing_pdf.pages):
            if idx in overlays:
                try:
                    page.merge_page(overlays[idx])
                except Exception:
                    logger.exception("Failed to merge overlay on page %s", idx)
            out.add_page(page)

        output_stream = io.BytesIO()
        out.write(output_stream)
        output_stream.seek(0)
        return output_stream.read()

    def _draw_pricing_page3(self, can: canvas.Canvas, layout: Dict, data: Dict) -> None:
        """Draw pricing fields that appear on page 3 (success_fee, docs_prep_fee)"""
        price_cfg = layout.get("pricing_page3", {})
        mode = price_cfg.get("mode", "blanks")
        
        if data.get("_debug_grid") or price_cfg.get("debug_grid"):
            self._draw_debug_grid(can)
        
        success_fee = data.get("success_fee")
        docs_prep_fee = data.get("docs_prep_fee")
        
        can.setFont(self.font_regular, 11)
        can.setFillColor(colors.red)
        
        if mode == "blanks":
            blanks = price_cfg.get("blanks", {})
            def fmt(value, style):
                if value is None:
                    return None
                try:
                    iv = int(value)
                except Exception:
                    return str(value)
                if style == "digits":
                    return f"{iv:,}".replace(",", " ")
                return rubles_to_text(iv)
            
            for key, value in {
                "success_fee": success_fee,
                "docs_prep_fee": docs_prep_fee,
            }.items():
                cfg = blanks.get(key)
                if not cfg:
                    continue
                text = fmt(value, cfg.get("format", "text"))
                if not text:
                    continue
                size = cfg.get("size", 11)
                try:
                    can.setFont(self.font_regular, size)
                except Exception:
                    pass
                can.drawString(cfg.get("x", 0), cfg.get("y", 0), text)
        
        can.setFillColor(colors.black)

    # ---------- Debug helpers ----------
    def _draw_debug_grid(self, can: canvas.Canvas, step: int = 25) -> None:
        """Draw a light coordinate grid to help calibrate x/y positions."""
        try:
            width, height = A4
            can.saveState()
            can.setStrokeColor(colors.lightgrey)
            can.setFillColor(colors.lightgrey)
            can.setLineWidth(0.25)
            can.setFont(self.font_regular, 6)
            # Vertical lines with x labels
            x = 0
            while x <= width:
                can.line(x, 0, x, height)
                can.drawString(x + 1, height - 10, str(int(x)))
                x += step
            # Horizontal lines with y labels
            y = 0
            while y <= height:
                can.line(0, y, width, y)
                can.drawString(1, y + 1, str(int(y)))
                y += step
            can.restoreState()
        except Exception:
            # Non-fatal if grid fails
            pass

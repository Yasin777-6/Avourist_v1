"""
HTML-based contract filler that directly modifies HTML templates and converts to PDF.
This approach is more reliable than PDF overlay as it works with the source HTML.
"""
import logging
import re
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from .reportlab_html_renderer import ReportLabHTMLRenderer

logger = logging.getLogger(__name__)


def rubles_to_text(amount: int) -> str:
    """Return amount like '12 000 (двенадцать тысяч) руб.' with graceful fallback."""
    words = None
    try:
        from num2words import num2words
        words = num2words(int(amount), lang="ru")
    except Exception:
        words = str(amount)
    formatted = f"{int(amount):,}".replace(",", " ")
    try:
        if str(words).strip().isdigit():
            return f"{formatted} руб."
    except Exception:
        pass
    return f"{formatted} ({words}) руб."


class HTMLContractFiller:
    """
    Fills HTML contract templates by replacing red-colored fields (class ft13, ft23, ft31, ft56, ft510)
    with actual data, then converts to PDF using wkhtmltopdf or weasyprint.
    """

    def __init__(self):
        self.red_classes = ["ft13", "ft14", "ft23", "ft31", "ft56", "ft510", "ft511"]
        self.reportlab_renderer = ReportLabHTMLRenderer()

    def fill_template(self, html_path: str, data: Dict) -> str:
        """
        Fill HTML template with data and return filled HTML string.
        
        Args:
            html_path: Path to HTML template file
            data: Dictionary with contract data
            
        Returns:
            Filled HTML as string
        """
        # Read HTML
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Fix image paths to be absolute
        template_dir = Path(html_path).parent.resolve()
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and not src.startswith('http') and not src.startswith('data:') and not src.startswith('file:'):
                # Convert relative path to absolute file path
                img_path = (template_dir / src).resolve()
                if img_path.exists():
                    # Use absolute file:// URL with forward slashes
                    abs_path = str(img_path).replace('\\', '/')
                    img['src'] = f"file:///{abs_path}"
                    logger.info(f"Fixed image path: {src} -> {img['src']}")
                else:
                    logger.warning(f"Image not found: {img_path}")
        
        # Normalize data
        data = self._normalize_data(data)
        
        # Find all red-colored paragraphs (these are the fields to fill)
        for class_name in self.red_classes:
            red_paragraphs = soup.find_all('p', class_=class_name)
            
            for p in red_paragraphs:
                text = p.get_text()
                
                # Identify field by content pattern and replace
                filled_text = self._identify_and_fill_field(text, data)
                if filled_text != text:
                    # Replace the text content while preserving HTML structure
                    p.string = filled_text
                    logger.info(f"Filled field: {text[:50]}... -> {filled_text[:50]}...")
        
        return str(soup)

    def _identify_and_fill_field(self, text: str, data: Dict) -> str:
        """
        Identify what field this is based on surrounding text and fill it.
        """
        text_lower = text.lower().strip()
        
        # Contract date (line 31: "28 апреля 2024 г")
        if 'г' in text and any(month in text_lower for month in ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']):
            return data.get('contract_date', datetime.now().strftime('%d.%m.%Y')) + ' г'
        
        # Client full name (line 32: "Тытюк  Александр  Михайлович")
        if 'тытюк' in text_lower or ('александр' in text_lower and 'михайлович' in text_lower):
            return data.get('client_full_name', '')
        
        # Case description fields (line 37-38: "ходатайство на получение...")
        if 'ходатайство' in text_lower or 'получение' in text_lower:
            return data.get('case_description', text)
        
        # Pricing fields - Total amount (line 81: "____")
        if text.strip() == '____' or text.strip() == '____':
            # This is likely total amount
            total = data.get('total_amount')
            if total:
                return f"{int(total):,}".replace(",", " ")
            return text
        
        # Pricing fields - with parentheses (line 82: "(_______  тысяч)  рублей.")
        if '(_______' in text or '(______' in text:
            # Extract if it's prepayment, success_fee, or docs_prep_fee based on context
            if 'тысяч)' in text and 'рублей' in text:
                # Try to determine which field
                # For now, use prepayment as default
                amount = data.get('prepayment') or data.get('total_amount')
                if amount:
                    return rubles_to_text(int(amount))
            return text
        
        # Pricing with underscores and parentheses (line 84: "________  (_______  тысяч)")
        if '________' in text and '(_______' in text:
            amount = data.get('prepayment')
            if amount:
                formatted = f"{int(amount):,}".replace(",", " ")
                words = self._amount_to_words(int(amount))
                return f"{formatted} ({words} тысяч)"
            return text
        
        # Success fee (line 117: "тысяч)  рублей")
        if text.startswith('тысяч)') and 'рублей' in text:
            amount = data.get('success_fee')
            if amount:
                return rubles_to_text(int(amount))
            return text
        
        # Docs prep fee (line 120: "______(___________ тысяч) рублей")
        if '______(' in text and 'тысяч)' in text and 'рублей' in text:
            amount = data.get('docs_prep_fee')
            if amount:
                return rubles_to_text(int(amount))
            return text
        
        # Client details section (line 213: multi-line with passport, address, etc.)
        if 'ОБЯЗАТЕЛЬНО' in text or 'Дата/ месяц/ год рождения' in text:
            # Build the filled client details block
            client_info = f"""{data.get('client_full_name', '')} 
 
ОБЯЗАТЕЛЬНО !!!!!!!!!!!!!!!!!!!  
Дата/ месяц/ год рождения {data.get('birth_date', '')} 
Место рождения {data.get('birth_place', '')} 
Паспорт Серия {data.get('client_passport_series', '')}  Номер {data.get('client_passport_number', '')}  
 
Зарегистрирован: {data.get('client_address', '')} """
            return client_info
        
        # Phone field (line 215: "Тел. _________________________")
        if 'Тел.' in text and '_____' in text:
            return f"Тел. {data.get('client_phone', '')}"
        
        # Email field (line 217: "Е-mail______________________________")
        if 'Е-mail' in text and '_____' in text:
            return f"Е-mail {data.get('email', '')}"
        
        # Signature field (line 219: "_______________________________________")
        if text.count('_') > 20 and 'Фамилия' not in text:
            return data.get('client_signature', text)
        
        return text

    def _amount_to_words(self, amount: int) -> str:
        """Convert amount to Russian words (thousands only)."""
        try:
            from num2words import num2words
            return num2words(int(amount / 1000), lang="ru")
        except Exception:
            return str(int(amount / 1000))

    def _normalize_data(self, data: Dict) -> Dict:
        """Normalize incoming data keys."""
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
        
        # Dates
        if not norm.get("contract_date"):
            norm["contract_date"] = datetime.now().strftime("%d %B %Y").replace(
                'January', 'января').replace('February', 'февраля').replace('March', 'марта').replace(
                'April', 'апреля').replace('May', 'мая').replace('June', 'июня').replace(
                'July', 'июля').replace('August', 'августа').replace('September', 'сентября').replace(
                'October', 'октября').replace('November', 'ноября').replace('December', 'декабря')
        
        return norm

    def html_to_pdf(self, html_content: str, output_path: str, template_dir: Path = None) -> bytes:
        """
        Convert filled HTML to PDF using available converter.
        
        Args:
            html_content: Filled HTML string
            output_path: Path to save PDF
            template_dir: Directory containing template images
            
        Returns:
            PDF bytes
        """
        # Try ReportLab renderer first (best quality, full font and image support)
        if template_dir:
            try:
                pdf_bytes = self.reportlab_renderer.render_html_to_pdf(
                    html_content, output_path, template_dir
                )
                logger.info(f"Generated PDF using ReportLab renderer: {output_path}")
                return pdf_bytes
            except Exception as e:
                logger.warning(f"ReportLab renderer failed: {e}, falling back to xhtml2pdf...")
        
        try:
            # Try xhtml2pdf (pure Python, works on Windows)
            from xhtml2pdf import pisa
            from io import BytesIO
            
            # Add font-face CSS for Cyrillic support
            font_css = """
            <style>
            @font-face {
                font-family: 'Times';
                src: url('C:/Windows/Fonts/times.ttf');
            }
            @font-face {
                font-family: 'Times';
                src: url('C:/Windows/Fonts/timesbd.ttf');
                font-weight: bold;
            }
            body {
                font-family: 'Times', 'DejaVu Sans', sans-serif;
            }
            </style>
            """
            
            # Insert font CSS into HTML
            if '<head>' in html_content:
                html_content = html_content.replace('<head>', f'<head>{font_css}')
            else:
                html_content = f'<html><head>{font_css}</head><body>{html_content}</body></html>'
            
            result_file = BytesIO()
            pisa_status = pisa.CreatePDF(
                html_content.encode('utf-8'),
                dest=result_file,
                encoding='utf-8'
            )
            
            if not pisa_status.err:
                pdf_bytes = result_file.getvalue()
                
                # Save to file
                with open(output_path, 'wb') as f:
                    f.write(pdf_bytes)
                
                logger.info(f"Generated PDF using xhtml2pdf: {output_path}")
                return pdf_bytes
            else:
                raise Exception(f"xhtml2pdf error: {pisa_status.err}")
            
        except Exception as e:
            logger.warning(f"xhtml2pdf failed: {e}, trying weasyprint...")
            
            try:
                from weasyprint import HTML
                pdf_bytes = HTML(string=html_content).write_pdf()
                
                # Save to file
                with open(output_path, 'wb') as f:
                    f.write(pdf_bytes)
                
                logger.info(f"Generated PDF using WeasyPrint: {output_path}")
                return pdf_bytes
                
            except Exception as e2:
                logger.error(f"Failed to convert HTML to PDF: {e2}")
                # Fallback: save HTML only
                html_path = output_path.replace('.pdf', '.html')
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"Saved filled HTML (PDF conversion failed): {html_path}")
                return html_content.encode('utf-8')

    def generate(self, template_path: str, data: Dict, output_path: str) -> bytes:
        """
        Main method: fill HTML template and convert to PDF.
        
        Args:
            template_path: Path to HTML template
            data: Contract data dictionary
            output_path: Path to save generated PDF
            
        Returns:
            PDF bytes
        """
        # Fill HTML template
        filled_html = self.fill_template(template_path, data)
        
        # Get template directory for images
        template_dir = Path(template_path).parent
        
        # Convert to PDF
        pdf_bytes = self.html_to_pdf(filled_html, output_path, template_dir)
        
        return pdf_bytes

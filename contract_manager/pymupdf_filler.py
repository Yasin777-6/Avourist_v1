"""
Clean PyMuPDF-based PDF filler with precise coordinate mapping.
Fills PDF templates by inserting text at exact positions using PyMuPDF (fitz).
"""
import logging
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class PyMuPDFFiller:
    """
    Simple and accurate PDF filler using PyMuPDF with exact coordinate mapping.
    """
    
    def __init__(self):
        # Register font for Cyrillic support
        self.font_name = "helv"  # Helvetica (built-in, supports Cyrillic)
        self.font_size = 11
        self.red_color = (1, 0, 0)  # RGB red
        self.black_color = (0, 0, 0)  # RGB black
    
    def fill_pdf(self, template_path: str, data: Dict, output_path: str) -> bytes:
        """
        Fill PDF template with data at precise positions.
        
        Args:
            template_path: Path to PDF template
            data: Dictionary with contract data
            output_path: Path to save filled PDF
            
        Returns:
            PDF bytes
        """
        logger.info(f"Opening PDF template: {template_path}")
        
        # Normalize data
        data = self._normalize_data(data)
        
        # Open PDF with PyMuPDF
        doc = fitz.open(template_path)
        
        # Get template name to determine field positions
        template_name = Path(template_path).name
        
        # Fill fields based on template
        if "2_инстанции" in template_name or "2 инстанции" in template_name:
            self._fill_instance_2_template(doc, data)
        else:
            # Default filling for other templates
            self._fill_default_template(doc, data)
        
        # Save filled PDF
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()
        
        # Read and return bytes
        with open(output_path, 'rb') as f:
            pdf_bytes = f.read()
        
        logger.info(f"Filled PDF saved to: {output_path} ({len(pdf_bytes)} bytes)")
        return pdf_bytes
    
    def _fill_instance_2_template(self, doc: fitz.Document, data: Dict):
        """
        Fill the 2-instance template with precise coordinates.
        Template: Договор_без_представления_интересов_БЕЗ_ДОВЕРЕННОСТИ_на_2_инстанции.pdf
        """
        # Page 1 (index 0) - Contract header and client name
        if len(doc) > 0:
            page = doc[0]
            
            # Contract number - after "Договор № " at top
            # Position: approximately (280, 100) in PDF points
            contract_number = data.get('contract_number', '')
            if contract_number:
                self._insert_text_pdf_coords(page, 280, 100, contract_number, color=self.black_color, bold=True)
            
            # Contract date - top right: "28 апреля 2024 г"
            # HTML: top:128px, left:653px → PDF: (490, 714)
            contract_date = data.get('contract_date', '')
            if contract_date:
                self._insert_text_pdf_coords(page, 490, 714, contract_date, color=self.red_color)
            
            # Client full name - below date
            # HTML: top:152px, left:53px → PDF: (40, 690)
            client_name = data.get('client_full_name', '')
            if client_name:
                self._insert_text_pdf_coords(page, 40, 690, client_name, color=self.red_color)
        
        # Page 2 (index 1) - Pricing section
        if len(doc) > 1:
            page = doc[1]
            
            # Total amount - "Стоимость услуг по договору составляет"
            # HTML: top:1081px, left:785px → PDF: (590, 31)
            total_amount = data.get('total_amount')
            if total_amount:
                amount_text = f"{int(total_amount):,}".replace(",", " ")
                self._insert_text_pdf_coords(page, 590, 31, amount_text, color=self.red_color)
            
            # Prepayment - "Оплата производится в следующем порядке"
            # HTML: top:1102px, left:621px → PDF: (466, 15)
            prepayment = data.get('prepayment')
            if prepayment:
                prep_text = f"{int(prepayment):,}".replace(",", " ")
                self._insert_text_pdf_coords(page, 466, 15, prep_text, color=self.red_color)
        
        # Page 3 (index 2) - Success fee and docs prep fee
        if len(doc) > 2:
            page = doc[2]
            
            # Success fee at top of page
            # HTML: top:33px, left:53px → PDF: (40, 770)
            success_fee = data.get('success_fee')
            if success_fee:
                fee_text = self._format_amount_with_words(int(success_fee))
                self._insert_text_pdf_coords(page, 40, 770, fee_text, color=self.red_color)
            
            # Docs preparation fee
            # HTML: top:95px, left:53px → PDF: (40, 747)
            docs_fee = data.get('docs_prep_fee')
            if docs_fee:
                docs_text = self._format_amount_with_words(int(docs_fee))
                self._insert_text_pdf_coords(page, 40, 747, docs_text, color=self.red_color)
        
        # Page 5 (index 4) - Client details section
        if len(doc) > 4:
            page = doc[4]
            
            # Client information block - right side "Заказчик"
            # HTML: top:54px, left:481px → PDF: (360, 788)
            # This is a multi-line block
            
            y_start = 788
            line_height = 14
            x_pos = 360
            
            # Full name
            client_name = data.get('client_full_name', '')
            if client_name:
                self._insert_text_pdf_coords(page, x_pos, y_start, client_name, color=self.red_color)
            
            # Birth date
            birth_date = data.get('birth_date', '')
            if birth_date:
                self._insert_text_pdf_coords(page, x_pos, y_start - line_height * 3, 
                                            f"Дата рождения: {birth_date}", color=self.red_color)
            
            # Birth place
            birth_place = data.get('birth_place', '')
            if birth_place:
                self._insert_text_pdf_coords(page, x_pos, y_start - line_height * 4, 
                                            f"Место рождения: {birth_place}", color=self.red_color)
            
            # Passport
            passport_series = data.get('client_passport_series', '')
            passport_number = data.get('client_passport_number', '')
            if passport_series and passport_number:
                self._insert_text_pdf_coords(page, x_pos, y_start - line_height * 5, 
                                            f"Паспорт: {passport_series} {passport_number}", color=self.red_color)
            
            # Address
            address = data.get('client_address', '')
            if address:
                self._insert_text_pdf_coords(page, x_pos, y_start - line_height * 7, 
                                            f"Адрес: {address}", color=self.red_color, max_width=200)
            
            # Phone
            phone = data.get('client_phone', '')
            if phone:
                self._insert_text_pdf_coords(page, x_pos, y_start - line_height * 10, 
                                            f"Тел.: {phone}", color=self.red_color)
            
            # Email
            email = data.get('email', '')
            if email:
                self._insert_text_pdf_coords(page, x_pos, y_start - line_height * 12, 
                                            f"E-mail: {email}", color=self.red_color)
    
    def _fill_default_template(self, doc: fitz.Document, data: Dict):
        """Fill default template (fallback for other templates)."""
        # Basic filling for page 1
        if len(doc) > 0:
            page = doc[0]
            
            # Try to insert contract number and date at common positions
            contract_number = data.get('contract_number', '')
            if contract_number:
                self._insert_text_pdf_coords(page, 300, 100, f"№ {contract_number}", color=self.black_color)
            
            contract_date = data.get('contract_date', '')
            if contract_date:
                self._insert_text_pdf_coords(page, 450, 100, contract_date, color=self.red_color)
    
    def _insert_text_pdf_coords(self, page: fitz.Page, x: float, y: float, text: str, 
                                color: Tuple[float, float, float] = None, 
                                bold: bool = False, max_width: int = None):
        """
        Insert text at PDF coordinates (bottom-left origin).
        
        Args:
            page: PDF page object
            x: X coordinate in PDF points
            y: Y coordinate in PDF points (from bottom)
            text: Text to insert
            color: RGB color tuple (0-1 range)
            bold: Use bold font
            max_width: Maximum width for text wrapping
        """
        if not text:
            return
        
        if color is None:
            color = self.black_color
        
        font_name = "helv" if not bold else "hebo"  # Helvetica or Helvetica-Bold
        
        try:
            # Handle text wrapping if max_width specified
            if max_width:
                # Simple word wrapping
                words = text.split()
                lines = []
                current_line = []
                
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    # Rough estimate: 6 points per character
                    if len(test_line) * 6 < max_width:
                        current_line.append(word)
                    else:
                        if current_line:
                            lines.append(' '.join(current_line))
                        current_line = [word]
                
                if current_line:
                    lines.append(' '.join(current_line))
                
                # Insert each line
                for i, line in enumerate(lines):
                    page.insert_text(
                        (x, y - (i * self.font_size * 1.2)),
                        line,
                        fontsize=self.font_size,
                        fontname=font_name,
                        color=color
                    )
            else:
                # Single line
                page.insert_text(
                    (x, y),
                    text,
                    fontsize=self.font_size,
                    fontname=font_name,
                    color=color
                )
            
            logger.debug(f"Inserted text at ({x:.1f}, {y:.1f}): {text[:30]}...")
        
        except Exception as e:
            logger.warning(f"Failed to insert text at ({x:.1f}, {y:.1f}): {e}")
    
    def _format_amount_with_words(self, amount: int) -> str:
        """Format amount as '15 000 (пятнадцать тысяч) руб.'"""
        try:
            from num2words import num2words
            words = num2words(int(amount), lang="ru")
            formatted = f"{int(amount):,}".replace(",", " ")
            return f"{formatted} ({words}) руб."
        except Exception:
            formatted = f"{int(amount):,}".replace(",", " ")
            return f"{formatted} руб."
    
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
        
        # Dates
        if not norm.get("contract_date"):
            norm["contract_date"] = datetime.now().strftime("%d.%m.%Y")
        
        return norm

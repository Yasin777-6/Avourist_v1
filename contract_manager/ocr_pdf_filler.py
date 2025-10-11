"""
OCR-based PDF filler using pdfplumber to detect field positions and PyMuPDF to insert text.
Uses OCR to find red-colored text placeholders and replaces them with actual data.
"""
import logging
import fitz  # PyMuPDF
import pdfplumber
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class OCRPDFFiller:
    """
    Uses OCR to detect field positions in PDF templates and fills them with data.
    """
    
    def __init__(self, ocr_api_key: str = None):
        self.ocr_api_key = ocr_api_key
        # Font for Russian text
        self.font_name = "helv"  # Helvetica (built-in)
        
    def fill_pdf(self, template_path: str, data: Dict, output_path: str) -> bytes:
        """
        Fill PDF template with data using OCR detection and PyMuPDF insertion.
        
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
        
        # Open PDF with PyMuPDF for editing
        doc = fitz.open(template_path)
        
        # Detect fields using pdfplumber
        field_positions = self._detect_fields_with_pdfplumber(template_path)
        
        logger.info(f"Detected {len(field_positions)} field positions")
        
        # Fill each field
        for field_info in field_positions:
            page_num = field_info['page']
            bbox = field_info['bbox']  # (x0, y0, x1, y1)
            text_content = field_info['text']
            
            # Determine what data to fill based on text content
            fill_text = self._determine_fill_text(text_content, data)
            
            if fill_text:
                self._insert_text(doc, page_num, bbox, fill_text, is_red=True)
        
        # Also fill known positions directly (more reliable than OCR)
        self._fill_known_positions(doc, data)
        
        # Save filled PDF
        doc.save(output_path)
        doc.close()
        
        # Read and return bytes
        with open(output_path, 'rb') as f:
            pdf_bytes = f.read()
        
        logger.info(f"Filled PDF saved to: {output_path}")
        return pdf_bytes
    
    def _detect_fields_with_pdfplumber(self, pdf_path: str) -> List[Dict]:
        """
        Use pdfplumber to detect text positions, especially red-colored text.
        """
        fields = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract words with positions
                    words = page.extract_words(
                        x_tolerance=3,
                        y_tolerance=3,
                        keep_blank_chars=True,
                        use_text_flow=True
                    )
                    
                    for word in words:
                        text = word['text'].strip()
                        
                        # Look for placeholder patterns (underscores, dates, names, etc.)
                        if self._is_placeholder(text):
                            fields.append({
                                'page': page_num,
                                'bbox': (word['x0'], word['top'], word['x1'], word['bottom']),
                                'text': text
                            })
                            logger.debug(f"Found placeholder on page {page_num}: {text}")
        
        except Exception as e:
            logger.warning(f"pdfplumber detection failed: {e}")
        
        return fields
    
    def _is_placeholder(self, text: str) -> bool:
        """Check if text is a placeholder that needs filling."""
        # Patterns that indicate placeholders
        patterns = [
            r'_{3,}',  # Multiple underscores
            r'\d{2}\s+\w+\s+\d{4}',  # Date pattern like "28 апреля 2024"
            r'[А-Я][а-я]+\s+[А-Я][а-я]+\s+[А-Я][а-я]+',  # Full name pattern
            r'\(\s*_{2,}\s*\)',  # Parentheses with underscores
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def _determine_fill_text(self, placeholder: str, data: Dict) -> str:
        """Determine what text to fill based on placeholder content."""
        placeholder_lower = placeholder.lower()
        
        # Date fields
        if any(month in placeholder_lower for month in ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня']):
            return data.get('contract_date', '')
        
        # Name fields
        if any(name in placeholder_lower for name in ['тытюк', 'александр', 'михайлович']):
            return data.get('client_full_name', '')
        
        # Underscores typically mean fill with appropriate data
        if '___' in placeholder:
            # Try to determine context
            return ''  # Will be filled by known positions
        
        return ''
    
    def _fill_known_positions(self, doc: fitz.Document, data: Dict):
        """
        Fill known field positions directly (more reliable than OCR).
        Based on the HTML template analysis.
        """
        # Page 1 (index 0) - Contract header
        page = doc[0]
        page_height = page.rect.height
        
        # Contract date (top:128px, left:653px)
        contract_date = data.get('contract_date', datetime.now().strftime('%d.%m.%Y'))
        self._insert_text_at_position(page, 653, 128, contract_date, is_red=True)
        
        # Client name (top:152px, left:53px)
        client_name = data.get('client_full_name', '')
        self._insert_text_at_position(page, 53, 152, client_name, is_red=True)
        
        # Page 2 (index 1) - Pricing
        if len(doc) > 1:
            page = doc[1]
            
            # Total amount (top:1081px, left:785px)
            total_amount = data.get('total_amount')
            if total_amount:
                amount_text = f"{int(total_amount):,}".replace(",", " ")
                self._insert_text_at_position(page, 785, 1081, amount_text, is_red=True)
            
            # Prepayment (top:1102px, left:621px)
            prepayment = data.get('prepayment')
            if prepayment:
                prep_text = f"{int(prepayment):,}".replace(",", " ")
                self._insert_text_at_position(page, 621, 1102, prep_text, is_red=True)
        
        # Page 3 (index 2) - More pricing
        if len(doc) > 2:
            page = doc[2]
            
            # Success fee (top:33px, left:53px)
            success_fee = data.get('success_fee')
            if success_fee:
                fee_text = self._amount_to_text(int(success_fee))
                self._insert_text_at_position(page, 53, 33, fee_text, is_red=True)
            
            # Docs prep fee (top:95px, left:53px)
            docs_fee = data.get('docs_prep_fee')
            if docs_fee:
                docs_text = self._amount_to_text(int(docs_fee))
                self._insert_text_at_position(page, 53, 95, docs_text, is_red=True)
        
        # Page 5 (index 4) - Client details
        if len(doc) > 4:
            page = doc[4]
            
            # Client info block (top:54px, left:481px)
            client_info = self._build_client_info_block(data)
            self._insert_text_at_position(page, 481, 54, client_info, is_red=True, multiline=True)
    
    def _insert_text_at_position(self, page: fitz.Page, x: float, y: float, text: str, 
                                  is_red: bool = False, multiline: bool = False):
        """
        Insert text at specific position using HTML pixel coordinates.
        Converts HTML coordinates (top-left origin) to PDF coordinates (bottom-left origin).
        """
        # Convert HTML coordinates to PDF coordinates
        # HTML: 892x1262 pixels, PDF: A4 = 595x842 points
        scale_x = page.rect.width / 892
        scale_y = page.rect.height / 1262
        
        pdf_x = x * scale_x
        pdf_y = page.rect.height - (y * scale_y)  # Flip Y axis
        
        # Insert text
        color = (1, 0, 0) if is_red else (0, 0, 0)  # RGB: red or black
        font_size = 11
        
        try:
            if multiline:
                # Split and insert multiple lines
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        page.insert_text(
                            (pdf_x, pdf_y + (i * font_size * 1.2)),
                            line.strip(),
                            fontsize=font_size,
                            fontname=self.font_name,
                            color=color
                        )
            else:
                page.insert_text(
                    (pdf_x, pdf_y),
                    text,
                    fontsize=font_size,
                    fontname=self.font_name,
                    color=color
                )
            logger.debug(f"Inserted text at ({pdf_x:.1f}, {pdf_y:.1f}): {text[:30]}...")
        except Exception as e:
            logger.warning(f"Failed to insert text at ({pdf_x:.1f}, {pdf_y:.1f}): {e}")
    
    def _insert_text(self, doc: fitz.Document, page_num: int, bbox: Tuple, text: str, is_red: bool = False):
        """Insert text at bounding box position."""
        if page_num >= len(doc):
            return
        
        page = doc[page_num]
        x0, y0, x1, y1 = bbox
        
        # Convert coordinates (pdfplumber uses top-left origin)
        pdf_y = page.rect.height - y0
        
        color = (1, 0, 0) if is_red else (0, 0, 0)
        
        try:
            page.insert_text(
                (x0, pdf_y),
                text,
                fontsize=11,
                fontname=self.font_name,
                color=color
            )
        except Exception as e:
            logger.warning(f"Failed to insert text: {e}")
    
    def _build_client_info_block(self, data: Dict) -> str:
        """Build multi-line client information block."""
        lines = [
            data.get('client_full_name', ''),
            '',
            'ОБЯЗАТЕЛЬНО !!!!!!!!!!!!!!!!!!!',
            f"Дата/ месяц/ год рождения {data.get('birth_date', '')}",
            f"Место рождения {data.get('birth_place', '')}",
            f"Паспорт Серия {data.get('client_passport_series', '')} Номер {data.get('client_passport_number', '')}",
            '',
            f"Зарегистрирован: {data.get('client_address', '')}",
            '',
            f"Тел. {data.get('client_phone', '')}",
            '',
            f"Е-mail {data.get('email', '')}",
        ]
        return '\n'.join(lines)
    
    def _amount_to_text(self, amount: int) -> str:
        """Convert amount to text format."""
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

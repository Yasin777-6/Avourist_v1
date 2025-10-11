"""
ReportLab-based HTML renderer that properly handles Russian fonts and images.
Converts HTML template to PDF with full Cyrillic support.
"""
import logging
from pathlib import Path
from typing import Dict
from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ReportLabHTMLRenderer:
    """
    Renders HTML contract templates to PDF using ReportLab.
    Properly handles Russian fonts and background images.
    """
    
    def __init__(self):
        self.font_regular = "Arial"
        self.font_bold = "Arial-Bold"
        self._register_fonts()
    
    def _register_fonts(self):
        """Register Arial fonts for Cyrillic support."""
        try:
            registered = pdfmetrics.getRegisteredFontNames()
            
            if self.font_regular not in registered:
                arial_path = Path("C:/Windows/Fonts/arial.ttf")
                if arial_path.exists():
                    pdfmetrics.registerFont(TTFont(self.font_regular, str(arial_path)))
                    logger.info("Registered Arial font")
            
            if self.font_bold not in registered:
                arial_bold_path = Path("C:/Windows/Fonts/arialbd.ttf")
                if arial_bold_path.exists():
                    pdfmetrics.registerFont(TTFont(self.font_bold, str(arial_bold_path)))
                    logger.info("Registered Arial Bold font")
        except Exception as e:
            logger.warning(f"Font registration failed: {e}")
            self.font_regular = "Helvetica"
            self.font_bold = "Helvetica-Bold"
    
    def render_html_to_pdf(self, html_content: str, output_path: str, template_dir: Path) -> bytes:
        """
        Render HTML to PDF with proper font and image support.
        
        Args:
            html_content: HTML string with filled data
            output_path: Path to save PDF
            template_dir: Directory containing template images
            
        Returns:
            PDF bytes
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Create PDF
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        page_width, page_height = A4
        
        # Process each page div
        page_divs = soup.find_all('div', id=lambda x: x and x.startswith('page'))
        
        for page_div in page_divs:
            # Draw background image if exists
            img_tag = page_div.find('img')
            if img_tag and img_tag.get('src'):
                src = img_tag.get('src')
                # Extract filename from file:/// URL or relative path
                if 'file:///' in src:
                    img_path = src.replace('file:///', '').replace('/', '\\')
                else:
                    img_path = template_dir / src
                
                img_path = Path(img_path)
                if img_path.exists():
                    try:
                        # Draw image as background
                        # HTML dimensions: 892x1262 px, PDF: 595x842 pt (A4)
                        # Scale: 595/892 = 0.667
                        c.drawImage(
                            str(img_path), 
                            0, 0,
                            width=page_width,
                            height=page_height,
                            preserveAspectRatio=True,
                            mask='auto'
                        )
                        logger.info(f"Drew background image: {img_path.name}")
                    except Exception as e:
                        logger.warning(f"Failed to draw image {img_path}: {e}")
            
            # Draw text elements
            for p in page_div.find_all('p'):
                self._draw_paragraph(c, p, page_width, page_height)
            
            # Move to next page
            c.showPage()
        
        # Save PDF
        c.save()
        pdf_bytes = pdf_buffer.getvalue()
        
        # Write to file
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        logger.info(f"Generated PDF with ReportLab: {output_path}")
        return pdf_bytes
    
    def _draw_paragraph(self, c: canvas.Canvas, p, page_width: float, page_height: float):
        """Draw a paragraph element on the canvas."""
        style = p.get('style', '')
        class_name = p.get('class', [])
        
        # Get all text including from nested tags
        text = p.get_text(separator=' ', strip=True)
        
        if not text or len(text.strip()) == 0:
            return
        
        # Parse position from style
        position = self._parse_position(style)
        if not position:
            return
        
        x, y = position
        
        # Convert HTML coordinates to PDF coordinates
        # HTML: top-left origin, PDF: bottom-left origin
        # HTML width: 892px, height: 1262px
        # PDF: 595pt x 842pt (A4)
        scale_x = page_width / 892
        scale_y = page_height / 1262
        
        pdf_x = x * scale_x
        pdf_y = page_height - (y * scale_y)  # Flip Y axis
        
        # Determine font and color
        font_size = self._parse_font_size(style, class_name)
        is_bold = p.find('b') is not None
        font = self.font_bold if is_bold else self.font_regular
        
        # Determine color (red for filled fields)
        is_red = any(cls in ['ft13', 'ft14', 'ft23', 'ft31', 'ft56', 'ft510', 'ft511'] for cls in class_name)
        color = colors.red if is_red else colors.black
        
        # Parse line-height for multi-line text
        line_height = self._parse_line_height(style, class_name)
        if not line_height:
            line_height = font_size * 1.2
        
        # Draw text
        try:
            c.setFont(font, font_size)
            c.setFillColor(color)
            
            # Handle multi-line text (contains <br/>)
            if p.find('br'):
                # Split by <br/> tags
                lines = []
                for content in p.contents:
                    if hasattr(content, 'name') and content.name == 'br':
                        continue
                    text_part = str(content).strip()
                    if text_part and text_part != '<br/>':
                        lines.append(text_part)
                
                # Draw each line
                for i, line in enumerate(lines):
                    if line.strip():
                        c.drawString(pdf_x, pdf_y - (i * line_height), line.strip())
            else:
                # Single line text
                c.drawString(pdf_x, pdf_y, text)
        except Exception as e:
            logger.warning(f"Failed to draw text at ({pdf_x:.1f}, {pdf_y:.1f}): {e}")
    
    def _parse_position(self, style: str) -> tuple:
        """Parse top and left position from style string."""
        try:
            top = left = None
            for part in style.split(';'):
                if 'top:' in part:
                    top = float(part.split(':')[1].replace('px', '').strip())
                elif 'left:' in part:
                    left = float(part.split(':')[1].replace('px', '').strip())
            
            if top is not None and left is not None:
                return (left, top)
        except Exception:
            pass
        return None
    
    def _parse_font_size(self, style: str, class_name: list) -> float:
        """Parse font size from style or class."""
        # Default sizes based on class
        size_map = {
            'ft10': 10, 'ft11': 12, 'ft12': 12, 'ft13': 12,
            'ft14': 12, 'ft15': 12, 'ft16': 12, 'ft17': 12,
            'ft18': 12, 'ft20': 10, 'ft21': 12, 'ft22': 12,
            'ft23': 12, 'ft24': 12, 'ft30': 10, 'ft31': 12,
            'ft40': 10, 'ft50': 10, 'ft51': 11, 'ft52': 11,
            'ft53': 12, 'ft54': 12, 'ft55': 12, 'ft56': 12,
        }
        
        for cls in class_name:
            if cls in size_map:
                return size_map[cls]
        
        return 12  # default
    
    def _parse_line_height(self, style: str, class_name: list) -> float:
        """Parse line-height from style or class."""
        # Line heights based on class (from HTML CSS)
        line_height_map = {
            'ft15': 20, 'ft16': 16, 'ft17': 20, 'ft18': 24,
            'ft24': 20, 'ft25': 24, 'ft26': 16, 'ft27': 20,
            'ft35': 24, 'ft36': 20, 'ft37': 16, 'ft38': 24,
            'ft43': 20, 'ft44': 24, 'ft45': 16,
            'ft57': 19, 'ft58': 20, 'ft59': 24,
            'ft510': 16, 'ft511': 20, 'ft512': 20,
        }
        
        for cls in class_name:
            if cls in line_height_map:
                return line_height_map[cls]
        
        return None  # Use default calculation

"""
Document Generator Service
Generates .docx files for petitions and contracts
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

logger = logging.getLogger(__name__)


class DocumentGenerator:
    """Generate professional legal documents in .docx format"""
    
    def __init__(self):
        self.temp_dir = Path('temp_documents')
        self.temp_dir.mkdir(exist_ok=True)
    
    def generate_petition_docx(self, petition_text: str, client_name: str = None) -> str:
        """
        Generate a .docx file from petition text
        
        Args:
            petition_text: The petition content
            client_name: Client name for filename
            
        Returns:
            Path to generated .docx file
        """
        try:
            # Strip HTML tags from petition text
            import re
            petition_text = re.sub(r'<[^>]+>', '', petition_text)
            
            # Remove separator lines (────────)
            petition_text = re.sub(r'─+', '', petition_text)
            
            # Create document
            doc = Document()
            
            # Set margins (2.5cm all sides - standard for Russian legal docs)
            sections = doc.sections
            for section in sections:
                section.top_margin = Inches(1)
                section.bottom_margin = Inches(1)
                section.left_margin = Inches(1.2)
                section.right_margin = Inches(0.8)
            
            # Parse petition text
            lines = petition_text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect line type and format accordingly
                if 'ХОДАТАЙСТВО' in line.upper() and len(line) < 50:
                    # Title
                    p = doc.add_paragraph(line)
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p.runs[0].bold = True
                    p.runs[0].font.size = Pt(14)
                
                elif line.startswith('В ') and 'суд' in line.lower():
                    # Court address (right-aligned)
                    p = doc.add_paragraph(line)
                    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    p.runs[0].font.size = Pt(12)
                
                elif line.startswith('От:') or line.startswith('от '):
                    # From (right-aligned)
                    p = doc.add_paragraph(line)
                    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    p.runs[0].font.size = Pt(12)
                
                elif line.lower().startswith('адрес:'):
                    # Address (right-aligned)
                    p = doc.add_paragraph(line)
                    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    p.runs[0].font.size = Pt(12)
                
                elif line.startswith('ПРОШУ:'):
                    # Request section
                    p = doc.add_paragraph(line)
                    p.runs[0].bold = True
                    p.runs[0].font.size = Pt(12)
                
                elif line.startswith('Дата:') or line.startswith('Подпись:'):
                    # Signature block
                    p = doc.add_paragraph(line)
                    p.runs[0].font.size = Pt(12)
                
                elif line.startswith('Приложение:'):
                    # Attachments
                    p = doc.add_paragraph(line)
                    p.runs[0].font.size = Pt(11)
                
                else:
                    # Regular paragraph
                    p = doc.add_paragraph(line)
                    p.runs[0].font.size = Pt(12)
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if client_name:
                safe_name = "".join(c for c in client_name if c.isalnum() or c in (' ', '_')).strip()
                filename = f"Ходатайство_{safe_name}_{timestamp}.docx"
            else:
                filename = f"Ходатайство_{timestamp}.docx"
            
            filepath = self.temp_dir / filename
            
            # Save document
            doc.save(str(filepath))
            
            logger.info(f"Generated petition document: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating petition document: {e}")
            raise
    
    def generate_contract_docx(self, contract_text: str, client_name: str = None) -> str:
        """
        Generate a .docx file from contract text
        
        Args:
            contract_text: The contract content
            client_name: Client name for filename
            
        Returns:
            Path to generated .docx file
        """
        try:
            doc = Document()
            
            # Set margins
            sections = doc.sections
            for section in sections:
                section.top_margin = Inches(1)
                section.bottom_margin = Inches(1)
                section.left_margin = Inches(1.2)
                section.right_margin = Inches(0.8)
            
            # Parse contract text
            lines = contract_text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if 'ДОГОВОР' in line.upper() and len(line) < 100:
                    # Title
                    p = doc.add_paragraph(line)
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p.runs[0].bold = True
                    p.runs[0].font.size = Pt(14)
                
                elif line.endswith(':') and len(line) < 50:
                    # Section headers
                    p = doc.add_paragraph(line)
                    p.runs[0].bold = True
                    p.runs[0].font.size = Pt(12)
                
                else:
                    # Regular paragraph
                    p = doc.add_paragraph(line)
                    p.runs[0].font.size = Pt(12)
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if client_name:
                safe_name = "".join(c for c in client_name if c.isalnum() or c in (' ', '_')).strip()
                filename = f"Договор_{safe_name}_{timestamp}.docx"
            else:
                filename = f"Договор_{timestamp}.docx"
            
            filepath = self.temp_dir / filename
            
            # Save document
            doc.save(str(filepath))
            
            logger.info(f"Generated contract document: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating contract document: {e}")
            raise
    
    def cleanup_old_documents(self, days: int = 1):
        """Delete documents older than specified days"""
        try:
            import time
            now = time.time()
            cutoff = now - (days * 86400)
            
            for file in self.temp_dir.glob('*.docx'):
                if file.stat().st_mtime < cutoff:
                    file.unlink()
                    logger.info(f"Deleted old document: {file}")
        except Exception as e:
            logger.error(f"Error cleaning up documents: {e}")

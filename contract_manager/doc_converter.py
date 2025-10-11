"""
Convert old .doc files to .docx format using win32com (Windows only).
"""
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def convert_doc_to_docx(doc_path: str, docx_path: str = None) -> str:
    """
    Convert .doc file to .docx format.
    
    Args:
        doc_path: Path to .doc file
        docx_path: Path to save .docx file (optional)
        
    Returns:
        Path to converted .docx file
    """
    try:
        import win32com.client
    except ImportError:
        logger.error("pywin32 not installed. Cannot convert .doc files.")
        return None
    
    # Get absolute paths
    doc_path = Path(doc_path).resolve()
    
    if docx_path is None:
        docx_path = doc_path.with_suffix('.docx')
    else:
        docx_path = Path(docx_path).resolve()
    
    # Skip if already converted
    if docx_path.exists():
        logger.info(f"DOCX already exists: {docx_path}")
        return str(docx_path)
    
    logger.info(f"Converting {doc_path.name} to DOCX...")
    
    try:
        # Create Word application
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        
        # Open the .doc file
        doc = word.Documents.Open(str(doc_path))
        
        # Save as .docx (format 16 = wdFormatXMLDocument)
        doc.SaveAs(str(docx_path), FileFormat=16)
        
        # Close document and Word
        doc.Close()
        word.Quit()
        
        logger.info(f"Converted to: {docx_path}")
        return str(docx_path)
        
    except Exception as e:
        logger.error(f"Failed to convert {doc_path}: {e}")
        try:
            word.Quit()
        except:
            pass
        return None


def convert_all_doc_templates(contracts_dir: str):
    """Convert all .doc templates in contracts directory to .docx."""
    contracts_path = Path(contracts_dir)
    doc_files = list(contracts_path.glob("*.doc"))
    
    logger.info(f"Found {len(doc_files)} .doc files to convert")
    
    converted = []
    for doc_file in doc_files:
        docx_file = convert_doc_to_docx(str(doc_file))
        if docx_file:
            converted.append(docx_file)
    
    logger.info(f"Converted {len(converted)} files")
    return converted

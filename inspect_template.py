"""
Inspect template to see exact text patterns
"""
from docx import Document
import subprocess
import sys

# Convert DOC to DOCX first
template_path = r"C:\Users\Administrator\autouristv1\contracts\Договор_без_представления_интересов_БЕЗ_ДОВЕРЕННОСТИ_на_3_инстанции.doc"

print("Converting DOC to DOCX...")
cmd = [
    "soffice",
    "--headless",
    "--convert-to", "docx",
    "--outdir", r"C:\Users\Administrator\autouristv1\contracts",
    template_path
]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
if result.returncode != 0:
    print(f"Conversion failed: {result.stderr}")
    sys.exit(1)

# Open converted DOCX
docx_path = template_path.replace('.doc', '.docx')
print(f"\nOpening: {docx_path}")

doc = Document(docx_path)

print("\n" + "="*80)
print("SEARCHING FOR PASSPORT AND SUCCESS FEE PATTERNS")
print("="*80)

for i, paragraph in enumerate(doc.paragraphs):
    text = paragraph.text
    
    # Look for passport patterns
    if "Паспорт" in text or "Серия" in text:
        print(f"\nParagraph {i} (PASSPORT):")
        print(f"  Text: '{text}'")
        print(f"  Length: {len(text)}")
        print(f"  Repr: {repr(text)}")
    
    # Look for success fee patterns  
    if "исключительно при положительном решении" in text:
        print(f"\nParagraph {i} (SUCCESS FEE):")
        print(f"  Text: '{text}'")
        print(f"  Length: {len(text)}")
        print(f"  Repr: {repr(text)}")
        
        # Count underscores
        underscore_count = text.count('_')
        print(f"  Underscore count: {underscore_count}")

print("\n" + "="*80)
print("DONE")
print("="*80)

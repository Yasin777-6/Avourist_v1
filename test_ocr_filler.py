"""
Test script to verify OCR-based PDF filler is working correctly.
"""
import fitz  # PyMuPDF
from pathlib import Path

# Find the latest generated contract
contracts_dir = Path("media/contracts/generated")
pdf_files = sorted(contracts_dir.glob("contract_AV-*.pdf"), key=lambda x: x.stat().st_mtime, reverse=True)

if pdf_files:
    latest_pdf = pdf_files[0]
    print(f"📄 Checking latest contract: {latest_pdf.name}")
    print(f"   File size: {latest_pdf.stat().st_size:,} bytes")
    
    # Open with PyMuPDF
    doc = fitz.open(str(latest_pdf))
    
    print(f"\n📊 PDF Information:")
    print(f"   Pages: {len(doc)}")
    print(f"   Format: {doc.metadata.get('format', 'Unknown')}")
    
    # Check for text content on each page
    print(f"\n📝 Text Content Check:")
    
    test_fields = [
        "11.10.2025",  # Contract date
        "Иван Иванов",  # Client name (from test data)
        "35 000",  # Total amount
        "15 000",  # Prepayment
        "+7 900",  # Phone
    ]
    
    found_fields = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        # Check for test fields
        for field in test_fields:
            if field in text:
                found_fields.append(field)
                print(f"   ✓ Page {page_num + 1}: Found '{field}'")
        
        # Check for images
        images = page.get_images()
        if images:
            print(f"   🖼️  Page {page_num + 1}: {len(images)} image(s)")
    
    doc.close()
    
    print(f"\n✅ Summary:")
    print(f"   Found {len(found_fields)} out of {len(test_fields)} test fields")
    print(f"   Fields found: {', '.join(found_fields)}")
    
    if len(found_fields) >= 3:
        print(f"\n🎉 Contract generation is working! Fields are being filled.")
    else:
        print(f"\n⚠️  Some fields may be missing. Check the PDF manually.")
else:
    print("❌ No contract PDFs found in media/contracts/generated/")

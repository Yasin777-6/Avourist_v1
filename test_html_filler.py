"""
Test script to verify HTML contract filler is working correctly.
"""
from contract_manager.html_contract_filler import HTMLContractFiller
from pathlib import Path
from datetime import datetime

# Test data
test_data = {
    "contract_number": "TEST-123",
    "contract_date": "11 октября 2024",
    "client_full_name": "Иванов Иван Иванович",
    "birth_date": "01.01.1990",
    "birth_place": "г. Москва",
    "client_passport_series": "4510",
    "client_passport_number": "123456",
    "client_address": "г. Москва, ул. Тестовая, д. 1, кв. 1",
    "client_phone": "+7 (900) 123-45-67",
    "email": "test@example.com",
    "total_amount": 35000,
    "prepayment": 15000,
    "success_fee": 15000,
    "docs_prep_fee": 5000,
    "case_description": "Тестовое описание дела",
    "client_signature": "Иванов И.И."
}

# Initialize filler
filler = HTMLContractFiller()

# HTML template path
html_template = Path("contracts/input-html.html")

if html_template.exists():
    print(f"✓ Found HTML template: {html_template}")
    
    # Fill the template
    print("\n📝 Filling HTML template...")
    filled_html = filler.fill_template(str(html_template), test_data)
    
    # Save filled HTML for inspection
    output_html = Path("media/contracts/generated/test_filled.html")
    output_html.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(filled_html)
    
    print(f"✓ Saved filled HTML to: {output_html}")
    
    # Convert to PDF
    print("\n📄 Converting to PDF...")
    output_pdf = Path("media/contracts/generated/test_filled.pdf")
    
    try:
        pdf_bytes = filler.html_to_pdf(filled_html, str(output_pdf))
        print(f"✓ Generated PDF: {output_pdf} ({len(pdf_bytes)} bytes)")
    except Exception as e:
        print(f"✗ PDF generation failed: {e}")
    
    # Check what fields were filled
    print("\n🔍 Checking filled fields:")
    for key, value in test_data.items():
        if str(value) in filled_html:
            print(f"  ✓ {key}: {value}")
        else:
            print(f"  ✗ {key}: {value} (NOT FOUND)")
    
    print("\n✅ Test complete!")
else:
    print(f"✗ HTML template not found: {html_template}")

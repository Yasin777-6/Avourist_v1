# Contract Selection Guide

## Overview
The AI assistant now intelligently selects the correct contract template based on client needs by asking clarifying questions before generating contracts.

## Contract Template Structure

Templates are stored in: `contract_manager/contracts/`

### Template Naming Convention
```
Договор_без_представления_интересов_{REPRESENTATION}_{INSTANCE}.doc/docx
```

Where:
- **REPRESENTATION**: 
  - `БЕЗ_ДОВЕРЕННОСТИ` (WITHOUT_POA) - Client handles court themselves, lawyer prepares documents
  - `ПО_ДОВЕРЕННОСТИ` (WITH_POA) - Lawyer represents client in court with power of attorney

- **INSTANCE**:
  - `на_1_инстанцию` - 1st instance (initial court hearing)
  - `на_2_инстанции` - 2nd instance (appeal)
  - `на_3_инстанции` - 3rd instance (cassation)
  - `на_4_инстанции` - 4th instance (supervisory review)

### Available Templates

#### WITHOUT POA (БЕЗ_ДОВЕРЕННОСТИ)
- 1st instance: `Договор_без_представления_интересов_БЕЗ_ДОВЕРЕННОСТИ_на_1_инстанцию.docx`
- 2nd instance: `Договор_без_представления_интересов_БЕЗ_ДОВЕРЕННОСТИ_на_2_инстанции.docx`
- 3rd instance: `Договор_без_представления_интересов_БЕЗ_ДОВЕРЕННОСТИ_на_3_инстанции.docx`
- 4th instance: `Договор_без_представления_интересов_БЕЗ_ДОВЕРЕННОСТИ_на_4_инстанции.docx`

#### WITH POA (ПО_ДОВЕРЕННОСТИ)
- 1st instance: `Договор_без_представления_интересов_ПО_ДОВЕРЕННОСТИ_на_1_инстанцию.docx`
- 2nd instance: `Договор_без_представления_интересов_ПО_ДОВЕРЕННОСТИ_на_2_инстанции.docx`
- 3rd instance: `Договор_без_представления_интересов_ПО_ДОВЕРЕННОСТИ_на_3_инстанции.docx`
- 4th instance: `Договор_без_представления_интересов_ПО_ДОВЕРЕННОСТЬЮ_на_4_инстанции.docx`

## AI Conversation Flow

### Step 1: Case Analysis
AI analyzes the client's case and provides legal assessment.

### Step 2: Clarifying Questions (NEW)
Before collecting passport data, AI MUST ask:

**Question 1: Court Instance**
```
На какой стадии ваше дело?
• 1-я инстанция (первое рассмотрение)
• 2-я инстанция (апелляция)
• 3-я инстанция (кассация)
• 4-я инстанция (надзор)
```

**Question 2: Representation Type**
```
Вам нужно, чтобы я лично присутствовал в суде по доверенности?
• ДА — я буду представлять вас в суде (по доверенности)
• НЕТ — я подготовлю все документы, вы сами подадите их в суд
```

### Step 3: Collect Client Data
Only after receiving answers to both questions above, AI collects:
- Full name
- Birth date
- Passport series and number
- Registration address
- Phone
- Email
- Case article

### Step 4: Generate Contract
AI sends data in format:
```
[GENERATE_CONTRACT:ФИО, паспорт серия XXXX номер XXXXXX, адрес, телефон, email, 
инстанция: 1, представление: БЕЗ_ДОВЕРЕННОСТИ]
```

## Parsing Logic

File: `ai_engine/services/contracts_flow.py`

### Instance Detection
```python
# Explicit: "инстанция: 2"
# Keywords: "апелляция" → 2, "кассация" → 3, "надзор" → 4
# Default: 1
```

### Representation Type Detection
```python
# "по доверенности" or "ПО_ДОВЕРЕННОСТИ" → WITH_POA
# "без доверенности" or "БЕЗ_ДОВЕРЕННОСТИ" → WITHOUT_POA
# Default: WITHOUT_POA
```

## Template Selection Logic

File: `contract_manager/services.py`

1. **Determine parameters**:
   - `instance`: from parsed data (1-4)
   - `representation_type`: WITH_POA or WITHOUT_POA
   - `region`: MOSCOW or REGIONS (from lead.region)

2. **Select template file** from mappings

3. **Prefer .docx over .doc**:
   - If `.doc` exists, check for `.docx` version
   - Use `.docx` if available (no LibreOffice needed)
   - Fall back to `.doc` only if `.docx` missing (requires LibreOffice on server)

4. **Fill template** with client data using `DOCXFiller` or `DOCTextReplacer`

## Pricing Based on Selection

From `pricing.md`:

### Regions
| Instance | WITHOUT_POA | WITH_POA |
|----------|-------------|----------|
| 1st | 15,000₽ | 25,000₽ |
| 2nd | 35,000₽ | 45,000₽ |
| 3rd | 53,000₽ | 63,000₽ |
| 4th | 70,000₽ | 80,000₽ |

### Moscow
| Instance | WITHOUT_POA | WITH_POA |
|----------|-------------|----------|
| 1st | 30,000₽ | 40,000₽ |
| 2nd | 60-80,000₽ | 100,000₽ |
| 3rd | 90-120,000₽ | 140,000₽ |
| 4th | 120-160,000₽ | - |

## Error Handling

### Missing LibreOffice
If `.doc` template is selected but LibreOffice is not installed on server:
```
ValueError: LibreOffice (soffice) is not installed on the server. 
Convert your contract templates to .docx and place the .docx files 
in the same contracts folder, or install LibreOffice on the server.
```

### Missing Template
If no template found for combination:
```
ValueError: No template found for {case_type}, {instance}, 
{representation_type}, {region}
```

## Testing Checklist

- [ ] AI asks instance question before collecting passport data
- [ ] AI asks representation question before collecting passport data
- [ ] Instance 1 + WITHOUT_POA → correct template selected
- [ ] Instance 2 + WITH_POA → correct template selected
- [ ] Moscow region → correct pricing applied
- [ ] Regions → correct pricing applied
- [ ] .docx templates used (no LibreOffice errors)
- [ ] Contract generated with correct data filled
- [ ] Email verification code sent
- [ ] Contract signed after code verification

## Maintenance

### Adding New Templates
1. Place `.doc` or `.docx` file in `contract_manager/contracts/`
2. Follow naming convention
3. Update `_load_template_mappings()` in `contract_manager/services.py`
4. If adding `.doc`, convert to `.docx` using:
   ```powershell
   soffice --headless --convert-to docx --outdir contract_manager/contracts "file.doc"
   ```

### Converting Existing .doc to .docx
Run from project root:
```powershell
$libre = "$env:ProgramFiles\LibreOffice\program\soffice.exe"
if (!(Test-Path $libre)) { $libre = "$env:ProgramFiles(x86)\LibreOffice\program\soffice.exe" }
$dir = "contract_manager/contracts"
Get-ChildItem -Path $dir -Filter *.doc -File | ForEach-Object {
  & "$libre" --headless --convert-to docx --outdir $dir $_.FullName
}
```

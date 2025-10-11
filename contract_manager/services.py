import os
import json
import logging
import uuid
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from django.conf import settings
from django.core.files.base import ContentFile

from .models import ContractTemplate, Contract, SMSVerification
from .docx_filler import DOCXFiller
from .doc_text_replacer import DOCTextReplacer

logger = logging.getLogger(__name__)
from leads.models import Lead


class ContractTemplateService:
    """Service for managing contract templates and field extraction"""
    
    def __init__(self):
        self.contracts_dir = settings.CONTRACTS_DIR
        self.template_mappings = self._load_template_mappings()
    
    def _load_template_mappings(self) -> Dict:
        """Load contract template mappings from contracts directory"""
        mappings = {
            # Without Power of Attorney templates - using original DOC files with photos
            'WITHOUT_POA': {
                '1': {
                    'REGIONS': 'Договор_без_представления_интересов_БЕЗ_ДОВЕРЕННОСТИ_на_1_инстанцию.doc',
                    'MOSCOW': 'Договор_без_представления_интересов_БЕЗ_ДОВЕРЕННСОСТИ_на_1_инстанцию.doc'
                },
                '2': {
                    'REGIONS': 'Договор_без_представления_интересов_БЕЗ_ДОВЕРЕННОСТИ_на_2_инстанции (1).doc',
                    'MOSCOW': 'Договор_без_представления_интересов_БЕЗ_ДОВЕРЕННОСТИ_на_2_инстанции (2).doc'
                },
                '3': {
                    'REGIONS': 'Договор_без_представления_интересов_БЕЗ_ДОВЕРЕННОСТИ_на_3_инстанции.doc',
                    'MOSCOW': 'Договор_без_представления_интересов_БЕЗ_ДОВЕРЕННОСТИ_на_3_инстанции (1).doc'
                },
                '4': {
                    'REGIONS': 'Договор_без_представления_интересов_БЕЗ_ДОВЕРЕННОСТИ_на_4_инстанции.doc',
                    'MOSCOW': 'Договор_без_представления_интересов_БЕЗ_ДОВЕРЕННОСТИ_на_4_инстанции.doc'
                }
            },
            # With Power of Attorney templates - using original DOC files with photos
            'WITH_POA': {
                '1': {
                    'REGIONS': 'Договор_без_представления_интересов_ПО_ДОВЕРЕННОСТИ_на_1_инстанцию.doc',
                    'MOSCOW': 'Договор_без_представления_интересов_ПО_ДОВЕРЕННСОСТИ_на_1_инстанцию.doc'
                },
                '2': {
                    'REGIONS': 'Договор_без_представления_интересов_ПО_ДОВЕРЕННОСТИ_на_2_инстанции.doc',
                    'MOSCOW': 'Договор_без_представления_интересов_ПО_ДОВЕРЕННОСТИ_на_2_инстанции (1).doc'
                },
                '3': {
                    'REGIONS': 'Договор_без_представления_интересов_ПО_ДОВЕРЕННОСТИ_на_3_инстанции.doc',
                    'MOSCOW': 'Договор_без_представления_интересов_ПО_ДОВЕРЕННОСТИ_на_3_инстанции (1).doc'
                },
                '4': {
                    'REGIONS': 'Договор_без_представления_интересов_ПО_ДОВЕРЕННОСТЬЮ_на_4_инстанции.doc',
                    'MOSCOW': 'Договор_без_представления_интересов_ПО_ДОВЕРЕННОСТЬЮ_на_4_инстанции.doc'
                }
            }
        }
        return mappings
    
    def select_template(self, case_type: str, instance: str, 
                       representation_type: str, region: str) -> Optional[str]:
        """Select appropriate contract template based on case parameters"""
        try:
            template_file = self.template_mappings[representation_type][instance][region]
            template_path = self.contracts_dir / template_file
            
            if template_path.exists():
                return str(template_path)
            else:
                # Fallback to regions template if Moscow not found
                if region == 'MOSCOW':
                    fallback_file = self.template_mappings[representation_type][instance]['REGIONS']
                    fallback_path = self.contracts_dir / fallback_file
                    if fallback_path.exists():
                        return str(fallback_path)
                        
        except KeyError:
            pass
            
        return None
    
    def get_required_fields(self, template_type: str) -> List[str]:
        """Get list of required fields for contract template"""
        base_fields = [
            'client_full_name',
            'client_passport_series',
            'client_passport_number', 
            'client_passport_issued_by',
            'client_passport_issued_date',
            'client_address',
            'client_phone',
            'case_article',
            'case_description',
            'contract_date',
            'total_amount'
        ]
        
        # Add template-specific fields
        if 'WITH_POA' in template_type:
            base_fields.extend([
                'representative_full_name',
                'representative_passport_series',
                'representative_passport_number'
            ])
            
        return base_fields


class ContractGenerationService:
    """Service for generating filled PDF contracts"""
    
    def __init__(self, use_docx=True):
        self.template_service = ContractTemplateService()
        
        # DOC text replacer (LibreOffice + python-docx for .doc files)
        self.doc_replacer = DOCTextReplacer()
        
        # DOCX filler (for .docx files)
        self.docx_filler = DOCXFiller()
        self.use_docx = use_docx
    
    def generate_contract(self, lead: Lead, contract_data: Dict) -> Contract:
        """Generate a new contract for a lead"""
        
        # Determine contract parameters
        case_type = lead.case_type or 'OTHER'
        # Normalize region to supported keys for templates
        raw_region = lead.region or 'REGIONS'
        region = 'MOSCOW' if str(raw_region).upper() == 'MOSCOW' else 'REGIONS'
        instance = contract_data.get('instance', '1')
        representation_type = contract_data.get('representation_type', 'WITHOUT_POA')

        logger.info(f"Contract params -> case_type={case_type}, raw_region={raw_region}, normalized_region={region}, instance={instance}, representation_type={representation_type}")
        
        # Select template
        template_path = self.template_service.select_template(
            case_type, instance, representation_type, region
        )
        
        if not template_path:
            logger.error(f"No template found for case_type={case_type}, instance={instance}, representation_type={representation_type}, region={region}")
            raise ValueError(f"No template found for {case_type}, {instance}, {representation_type}, {region}")
        else:
            logger.info(f"Using template path: {template_path}")
        
        # Get or create template record
        template, created = ContractTemplate.objects.get_or_create(
            case_type=case_type,
            instance=instance,
            representation_type=representation_type,
            region=region,
            defaults={
                'name': f"Contract {case_type} - {instance} inst. - {region}",
                'template_file': template_path,
                'base_cost': self._calculate_base_cost(region, instance, representation_type),
                'required_fields': self.template_service.get_required_fields(representation_type)
            }
        )
        if created:
            logger.info(f"Created ContractTemplate record for {template}")
        else:
            logger.info(f"Using existing ContractTemplate id={template.id}")
        
        # Create contract
        contract = Contract.objects.create(
            lead=lead,
            template=template,
            contract_number=self._generate_contract_number(),
            client_data=contract_data
        )
        
        # Prepare merged data with automatic pricing calculation
        merged_data = dict(contract_data or {})
        merged_data.setdefault('contract_date', datetime.now().strftime('%d.%m.%Y'))
        
        # Calculate pricing if not provided
        total_amount = merged_data.get('total_amount') or int(template.base_cost)
        merged_data['total_amount'] = total_amount
        
        # Calculate prepayment based on custom percentage or default 50%
        if not merged_data.get('prepayment'):
            prepayment_percent = merged_data.get('prepayment_percent') or 50
            merged_data['prepayment'] = int(total_amount * (prepayment_percent / 100))
        
        # Calculate success fee based on custom percentage or remaining amount
        if not merged_data.get('success_fee'):
            success_fee_percent = merged_data.get('success_fee_percent')
            if success_fee_percent:
                merged_data['success_fee'] = int(total_amount * (success_fee_percent / 100))
            else:
                merged_data['success_fee'] = total_amount - merged_data['prepayment']
        
        # Docs preparation fee (default: 5000)
        merged_data.setdefault('docs_prep_fee', 5000)
        
        # Add payment terms description if provided
        if merged_data.get('payment_terms'):
            merged_data['payment_terms_description'] = merged_data['payment_terms']
        else:
            prepay_pct = int((merged_data['prepayment'] / total_amount) * 100)
            success_pct = int((merged_data['success_fee'] / total_amount) * 100)
            merged_data['payment_terms_description'] = f"{prepay_pct}% предоплата, {success_pct}% после положительного решения"
        
        merged_data['contract_number'] = contract.contract_number
        
        # Check if DOC/DOCX template exists (use the actual template from contracts folder)
        # The template_path already points to the correct template
        doc_template_path = Path(template_path)
        
        # Use DOC/DOCX filler if template has .doc or .docx extension
        if self.use_docx and doc_template_path.suffix.lower() in ['.doc', '.docx']:
            logger.info(f"Filling DOC/DOCX template: {doc_template_path.name}...")
            
            # Determine output extension - .doc files may be converted to .docx
            output_extension = doc_template_path.suffix
            output_doc_path = settings.MEDIA_ROOT / 'contracts' / 'generated' / f"contract_{contract.contract_number}{output_extension}"
            output_doc_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                # Use binary text replacer for .doc files, DOCX filler for .docx files
                if doc_template_path.suffix.lower() == '.doc':
                    logger.info("Using DOC text replacer for .doc file...")
                    filled_doc = self.doc_replacer.fill_doc(
                        template_path=str(doc_template_path),
                        data=merged_data,
                        output_path=str(output_doc_path)
                    )
                    # Check if output was converted to .docx
                    if not output_doc_path.exists():
                        # Try .docx extension
                        output_doc_path = output_doc_path.with_suffix('.docx')
                        output_extension = '.docx'
                        if output_doc_path.exists():
                            with open(output_doc_path, 'rb') as f:
                                filled_doc = f.read()
                            logger.info(f"DOC was converted to DOCX: {output_doc_path}")
                else:
                    logger.info("Using DOCX filler for .docx file...")
                    filled_doc = self.docx_filler.fill_docx(
                        template_path=str(doc_template_path),
                        data=merged_data,
                        output_path=str(output_doc_path)
                    )
                
                logger.info(f"Filled document bytes: {len(filled_doc)}")
                
                # Save as DOC/DOCX (not PDF)
                doc_filename = f"contract_{contract.contract_number}{output_extension}"
                contract.generated_pdf.save(
                    doc_filename,
                    ContentFile(filled_doc),
                    save=True
                )
                logger.info(f"Saved generated document as {doc_filename} for contract {contract.contract_number}")
                return contract
            except Exception as e:
                logger.error(f"DOC/DOCX filling failed: {e}")
                raise ValueError(f"Failed to generate contract: {e}")
        
        # If no DOC/DOCX template found, raise error
        raise ValueError(f"No DOC/DOCX template found at {template_path}")
    
    def _generate_contract_number(self) -> str:
        """Generate unique contract number"""
        date_str = datetime.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"AV-{date_str}-{unique_id}"
    
    def _calculate_base_cost(self, region: str, instance: str, representation_type: str) -> Decimal:
        """Calculate base cost based on pricing structure from payments.md"""
        
        pricing = {
            'REGIONS': {
                'WITHOUT_POA': {'1': 15000, '2': 35000, '3': 53000, '4': 70000},
                'WITH_POA': {'1': 25000, '2': 45000, '3': 63000, '4': 80000}
            },
            'MOSCOW': {
                'WITHOUT_POA': {'1': 30000, '2': 60000, '3': 90000, '4': 120000},
                'WITH_POA': {'1': 40000, '2': 80000, '3': 120000, '4': 150000}
            }
        }
        
        try:
            return Decimal(pricing[region][representation_type][instance])
        except KeyError:
            return Decimal('20000')  # Default fallback
    


class EmailVerificationService:
    """Service for handling email verification codes"""
    
    def generate_verification_code(self, contract: Contract) -> SMSVerification:
        """Generate and send email verification code"""
        
        # Generate 6-digit code
        import random
        code = f"{random.randint(100000, 999999)}"
        
        # Create verification record
        verification = SMSVerification.objects.create(
            contract=contract,
            telegram_id=contract.lead.telegram_id,
            verification_code=code
        )
        
        # Send code via email
        self._send_code_via_email(contract.lead.email, code, contract.contract_number)
        
        return verification
    
    def _send_code_via_email(self, email: str, code: str, contract_number: str):
        """Send verification code via email"""
        from django.core.mail import send_mail
        from django.conf import settings
        
        if not email:
            logger.warning(f"No email address for contract {contract_number}")
            return
        
        subject = f"Код подтверждения договора {contract_number}"
        message = f"""
Здравствуйте!

Ваш код подтверждения договора: {code}

Код действителен 10 минут.

Введите этот код в Telegram-боте для подписания договора.

---
С уважением,
Команда АвтоЮрист
        """.strip()
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            logger.info(f"Verification code sent to {email}")
        except Exception as e:
            logger.error(f"Failed to send email to {email}: {e}")
    
    def verify_code(self, contract: Contract, entered_code: str) -> bool:
        """Verify entered SMS code"""
        
        sms_verification = SMSVerification.objects.filter(
            contract=contract,
            verification_code=entered_code,
            is_used=False
        ).first()
        
        if sms_verification and not sms_verification.is_expired():
            sms_verification.is_used = True
            sms_verification.verified_at = datetime.now()
            sms_verification.save()
            
            # Update contract status
            contract.status = 'SIGNED'
            contract.signed_at = datetime.now()
            contract.save()
            
            # Update lead status
            contract.lead.status = 'CONVERTED'
            contract.lead.save()
            
            return True
            
        return False


# Backward compatibility alias
SMSVerificationService = EmailVerificationService

import logging
import re
from datetime import datetime
from typing import Dict

import requests
from django.conf import settings

from contract_manager.models import Contract
from contract_manager.services import ContractGenerationService, SMSVerificationService

logger = logging.getLogger(__name__)


class ContractFlow:
    """Handles contract generation and SMS verification flow"""

    def __init__(self):
        self.contract_service = ContractGenerationService()
        self.sms_service = SMSVerificationService()

    def handle_contract_generation(self, lead, client_data):
        try:
            if isinstance(client_data, str):
                data_str = client_data.strip()
                if not data_str or data_str.upper() in {"RESEND", "REPEAT", "SEND_AGAIN"}:
                    existing_contract = Contract.objects.filter(lead=lead).order_by("-created_at").first()
                    if existing_contract:
                        self._send_contract_to_telegram(lead.telegram_id, existing_contract)
                        return (
                            "  Я повторно отправил договор в этот чат. Проверьте файл и введите код из email для подписания."
                        )
                    return (
                        "У меня пока нет готового договора для отправки. Давайте оформим заново — пришлите ваши паспортные данные, адрес и телефон."
                    )
                parsed_data = self._parse_contract_data(lead, data_str)
            else:
                parsed_data = client_data if isinstance(client_data, dict) else None
            if not parsed_data:
                return (
                    "Не смог собрать данные для договора. Укажите ФИО, серию и номер паспорта, адрес и телефон одной строкой."
                )

            logger.info(
                f"Generating contract with data: {parsed_data} | lead.region={lead.region} | lead.case_type={lead.case_type}"
            )
            logger.info(
                f"Contract parameters: instance={parsed_data.get('instance', '1')}, "
                f"representation={parsed_data.get('representation_type', 'WITHOUT_POA')}, "
                f"region={lead.region or 'REGIONS'}"
            )
            contract = self.contract_service.generate_contract(lead, parsed_data)
            logger.info(f"Contract generated: {contract.contract_number}")

            self._send_contract_to_telegram(lead.telegram_id, contract)
            try:
                pdf_path = getattr(contract.generated_pdf, "path", None)
                logger.info(f"Contract PDF path: {pdf_path}")
            except Exception:
                logger.warning("Could not read contract PDF path")

            self.sms_service.generate_verification_code(contract)
            contract.status = "SMS_SENT"
            contract.save()

            return (
                f"""  Договор отправлен в чат!

            Номер: {contract.contract_number}
            Стоимость: {int(contract.template.base_cost):,} руб

            <b>Код подтверждения отправлен на вашу почту</b>

            Проверьте email и введите код для подписания договора."""
            )
        except Exception:
            logger.exception("Contract generation error")
            return "Ошибка при создании договора. Наш менеджер скоро свяжется с вами."

    def _send_contract_to_telegram(self, telegram_id: int, contract):
        try:
            file_field = contract.generated_pdf
            if file_field and getattr(file_field, "path", None):
                url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendDocument"
                with open(file_field.path, "rb") as file:
                    files = {"document": file}
                    data = {
                        "chat_id": telegram_id,
                        "caption": f"📄 Договор №{contract.contract_number}\n\nПроверьте данные и введите код из email для подписания.",
                        "parse_mode": "HTML",
                    }
                    response = requests.post(url, data=data, files=files, timeout=30)
                    response.raise_for_status()
                    logger.info(f"Contract sent to {telegram_id}")
            else:
                logger.error("No generated PDF available to send for this contract")
        except Exception as e:
            logger.error(f"Failed to send contract file: {str(e)}")

    def _parse_contract_data(self, lead, data_str: str) -> Dict:
        contract_data: Dict = {
            # Client basic info
            "client_full_name": f"{(lead.first_name or '').strip()} {(lead.last_name or '').strip()}".strip()
            or "Клиент",
            
            # Passport details
            "client_passport_series": "",
            "client_passport_number": "",
            "client_passport_issued_by": "",
            "client_passport_issued_date": "",
            
            # Personal details
            "birth_date": "",
            "birth_place": "",
            "client_address": "",
            "client_phone": "",
            "email": lead.email or "",
            
            # Case details
            "case_article": "",
            "case_description": (lead.case_description or "").strip(),
            
            # Pricing (will be calculated from template or parsed from AI)
            "total_amount": None,
            "prepayment": None,
            "prepayment_percent": None,  # e.g., 25 for 25%
            "success_fee": None,
            "success_fee_percent": None,  # e.g., 75 for 75%
            "docs_prep_fee": 5000,  # Default docs preparation fee
            "payment_terms": "",  # Custom payment terms description
            
            # Contract metadata
            "contract_date": datetime.now().strftime("%d.%m.%Y"),
            "instance": "1",
            "representation_type": "WITHOUT_POA",
            "director_name": "Шельмина Евгения Васильевича",  # Default director
        }

        # Parse phone number (multiple patterns)
        phone_match = re.search(r"(?:телефон|тел\.?|номер)[:\s-]*(\+?7[\s-]?\d[\d\s-]{8,})", data_str, re.IGNORECASE)
        if not phone_match:
            phone_match = re.search(r"(\+?7[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2})", data_str)
        if phone_match:
            contract_data["client_phone"] = re.sub(r"\s+", " ", phone_match.group(1)).strip()
        # Save phone to lead
        if contract_data["client_phone"] and not lead.phone_number:
            lead.phone_number = contract_data["client_phone"]
            lead.save()

        # Parse passport series and number (handles both orders)
        # Try "серия XXXX номер XXXXXX"
        pass_match = re.search(
            r"(?:серия\s*)(\d{4,6})[\s-]*(?:номер\s*)?(\d{4,6})", data_str, re.IGNORECASE
        )
        if pass_match:
            # Determine which is series (4 digits) and which is number (6 digits)
            first = pass_match.group(1)
            second = pass_match.group(2)
            if len(first) == 4 and len(second) == 6:
                contract_data["client_passport_series"] = first
                contract_data["client_passport_number"] = second
            elif len(first) == 6 and len(second) == 4:
                contract_data["client_passport_series"] = second
                contract_data["client_passport_number"] = first
        else:
            # Try "номер XXXXXX серия XXXX" (reversed)
            pass_match_rev = re.search(
                r"(?:номер\s*(?:пасспорта\s*)?)(\d{4,6})[\s-]*(?:серия\s*)?(\d{4,6})", data_str, re.IGNORECASE
            )
            if pass_match_rev:
                first = pass_match_rev.group(1)
                second = pass_match_rev.group(2)
                if len(first) == 6 and len(second) == 4:
                    contract_data["client_passport_number"] = first
                    contract_data["client_passport_series"] = second
                elif len(first) == 4 and len(second) == 6:
                    contract_data["client_passport_series"] = first
                    contract_data["client_passport_number"] = second

        # Parse birth date (DD.MM.YYYY or DD/MM/YYYY)
        birth_date_match = re.search(r"(\d{2}[./]\d{2}[./]\d{4})", data_str)
        if birth_date_match:
            contract_data["birth_date"] = birth_date_match.group(1).replace("/", ".")
        
        # Parse birth place
        birth_place_match = re.search(r"(?:место рождения|родился)[:\s-]*(г\.\s*[^\n,;]+|[А-ЯЁ][а-яё]+)", data_str, re.IGNORECASE)
        if birth_place_match:
            contract_data["birth_place"] = birth_place_match.group(1).strip()

        # Parse address
        addr_match = re.search(r"адрес[:\s-]*([^\n]+)", data_str, re.IGNORECASE)
        if addr_match:
            contract_data["client_address"] = addr_match.group(1).strip()
        else:
            msk_match = re.search(r"(г\.\s*Москва[^\n,;]*)", data_str, re.IGNORECASE)
            if msk_match:
                contract_data["client_address"] = msk_match.group(1).strip()

        # Parse full name
        name_match = re.search(
            r"([А-ЯA-ZЁ][а-яa-zё]+\s+[А-ЯA-ZЁ][а-яa-zё]+(?:\s+[А-ЯA-ZЁ][а-яa-zё]+)?)",
            data_str,
        )
        if name_match:
            contract_data["client_full_name"] = name_match.group(1).strip()
        
        # Parse email
        email_match = re.search(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", data_str)
        if email_match:
            email = email_match.group(1).strip()
            contract_data["email"] = email
            # Save email to lead for future use
            if not lead.email:
                lead.email = email
                lead.save()
        
        # Parse instance (1, 2, 3, or 4)
        instance_match = re.search(r"(?:инстанция|inst)[:\s-]*(\d)", data_str, re.IGNORECASE)
        if instance_match:
            contract_data["instance"] = instance_match.group(1)
        else:
            # Try to detect from keywords
            if re.search(r"апелляци", data_str, re.IGNORECASE):
                contract_data["instance"] = "2"
            elif re.search(r"кассаци", data_str, re.IGNORECASE):
                contract_data["instance"] = "3"
            elif re.search(r"надзор", data_str, re.IGNORECASE):
                contract_data["instance"] = "4"
        
        # Parse representation type (WITH_POA or WITHOUT_POA)
        if re.search(r"(?:по|с)\s*доверенност", data_str, re.IGNORECASE):
            contract_data["representation_type"] = "WITH_POA"
        elif re.search(r"без\s*доверенност", data_str, re.IGNORECASE):
            contract_data["representation_type"] = "WITHOUT_POA"
        # Also check for explicit markers from AI
        if "ПО_ДОВЕРЕННОСТИ" in data_str.upper():
            contract_data["representation_type"] = "WITH_POA"
        elif "БЕЗ_ДОВЕРЕННОСТИ" in data_str.upper():
            contract_data["representation_type"] = "WITHOUT_POA"
        
        # Parse custom payment terms (e.g., "25% сейчас, 75% после")
        payment_match = re.search(r"(\d+)%\s*(?:сейчас|предоплата)[,\s]+(\d+)%\s*(?:после|успех)", data_str, re.IGNORECASE)
        if payment_match:
            contract_data["prepayment_percent"] = int(payment_match.group(1))
            contract_data["success_fee_percent"] = int(payment_match.group(2))
            contract_data["payment_terms"] = f"{payment_match.group(1)}% предоплата, {payment_match.group(2)}% после положительного решения"

        # Try to extract article from conversation data first
        # Matches: "ч. 2 ст. 12.8 КоАП" or "ст. 12.8 КоАП"
        article_match = re.search(r"(?:ч\.\s*(\d+)\s+)?ст\.\s*(\d+\.?\d*)\s*КоАП", data_str, re.IGNORECASE)
        if article_match:
            part = article_match.group(1)  # Part number (e.g., "2")
            article = article_match.group(2)  # Article number (e.g., "12.8")
            if part:
                contract_data["case_article"] = f"ч.{part} ст. {article} КоАП РФ"
            else:
                contract_data["case_article"] = f"ст. {article} КоАП РФ"
        else:
            # Fallback to case_type mapping
            case_map = {
                "DUI": "ч.1 ст. 12.8 КоАП РФ",
                "SPEEDING": "ст. 12.9 КоАП РФ",
                "LICENSE_SUSPENSION": "ст. 12.7 КоАП РФ",
                "ACCIDENT": "ст. 12.27 КоАП РФ",
                "PARKING": "ст. 12.19 КоАП РФ",
                "OTHER": "КоАП РФ",
            }
            contract_data["case_article"] = case_map.get(getattr(lead, "case_type", "OTHER") or "OTHER", "КоАП РФ")

        if not contract_data["case_description"]:
            contract_data["case_description"] = data_str[:500]

        return contract_data

    def handle_email_code(self, lead):
        """Resend verification code via email"""
        try:
            contract = Contract.objects.filter(lead=lead).order_by("-created_at").first()
            if contract:
                self.sms_service.generate_verification_code(contract)
                contract.status = "SMS_SENT"
                contract.save()
                return "Код подтверждения отправлен повторно на вашу почту. Введите его для подписания договора."
            return "Не нашёл активный договор для отправки кода. Давайте оформим договор заново."
        except Exception as e:
            logger.error(f"Email code error: {str(e)}")
            return "Не удалось отправить код. Попробуйте ещё раз чуть позже."

    def handle_code_verification(self, lead, code: str) -> str:
        """Verify entered code"""
        try:
            contract = Contract.objects.filter(lead=lead).order_by("-created_at").first()
            if contract and self.sms_service.verify_code(contract, code):
                return (
                    "✅ Отлично! Договор подписан. Наш юрист скоро приступит к работе по вашему делу."
                )
            else:
                return "❌ Неверный код или код истек. Попробуйте еще раз или запросите новый код."
        except Exception as e:
            logger.error(f"Code verification error: {str(e)}")
            return "Ошибка при проверке кода. Обратитесь к менеджеру."
    
    # Backward compatibility aliases
    handle_sms_code = handle_email_code
    handle_sms_verification = handle_code_verification

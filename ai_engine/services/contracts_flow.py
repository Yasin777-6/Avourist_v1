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
            logger.info(f"=== CONTRACT GENERATION STARTED ===")
            logger.info(f"Lead ID: {lead.id}, Telegram ID: {lead.telegram_id}")
            logger.info(f"Lead region: {lead.region}, case_type: {lead.case_type}")
            logger.info(f"Client data type: {type(client_data).__name__}")
            
            if isinstance(client_data, str):
                data_str = client_data.strip()
                logger.info(f"Client data string (first 200 chars): {data_str[:200]}...")
                
                if not data_str or data_str.upper() in {"RESEND", "REPEAT", "SEND_AGAIN"}:
                    logger.info("Resending existing contract...")
                    existing_contract = Contract.objects.filter(lead=lead).order_by("-created_at").first()
                    if existing_contract:
                        logger.info(f"Found existing contract: {existing_contract.contract_number}")
                        self._send_contract_to_telegram(lead.telegram_id, existing_contract)
                        return (
                            "  Я повторно отправил договор в этот чат. Проверьте файл и введите код из email для подписания."
                        )
                    logger.warning("No existing contract found for resend")
                    return (
                        "У меня пока нет готового договора для отправки. Давайте оформим заново — пришлите ваши паспортные данные, адрес и телефон."
                    )
                
                # Try pipe-delimited format first (from AI command)
                if "|" in data_str:
                    logger.info("Parsing pipe-delimited format...")
                    parsed_data = self._parse_pipe_format(lead, data_str)
                else:
                    logger.info("Parsing natural language format...")
                    # Fallback to natural language parsing
                    parsed_data = self._parse_contract_data(lead, data_str)
            else:
                logger.info("Client data is dict or other type")
                parsed_data = client_data if isinstance(client_data, dict) else None
            
            if not parsed_data:
                logger.error("Failed to parse contract data")
                return (
                    "Не смог собрать данные для договора. Укажите ФИО, серию и номер паспорта, адрес и телефон одной строкой."
                )

            logger.info(f"=== PARSED CONTRACT DATA ===")
            logger.info(f"Client name: {parsed_data.get('client_full_name')}")
            logger.info(f"Passport: {parsed_data.get('client_passport_series')} / {parsed_data.get('client_passport_number')}")
            logger.info(f"Email: {parsed_data.get('email')}")
            logger.info(f"Phone: {parsed_data.get('client_phone')}")
            logger.info(f"Address: {parsed_data.get('client_address')}")
            logger.info(f"Case article: {parsed_data.get('case_article')}")
            logger.info(f"Instance: {parsed_data.get('instance', '1')}")
            logger.info(f"Representation: {parsed_data.get('representation_type', 'WITHOUT_POA')}")
            logger.info(f"Total amount: {parsed_data.get('total_amount')}")
            logger.info(f"Prepayment: {parsed_data.get('prepayment')}")
            logger.info(f"Success fee: {parsed_data.get('success_fee')}")
            logger.info(f"Lead region: {lead.region}, case_type: {lead.case_type}")
            
            logger.info(f"=== CALLING CONTRACT SERVICE ===")
            contract = self.contract_service.generate_contract(lead, parsed_data)
            logger.info(f"✅ Contract generated successfully: {contract.contract_number}")

            logger.info(f"=== SENDING CONTRACT TO TELEGRAM ===")
            self._send_contract_to_telegram(lead.telegram_id, contract)
            try:
                pdf_path = getattr(contract.generated_pdf, "path", None)
                logger.info(f"Contract file path: {pdf_path}")
            except Exception as e:
                logger.warning(f"Could not read contract file path: {e}")

            logger.info(f"=== GENERATING VERIFICATION CODE ===")
            self.sms_service.generate_verification_code(contract)
            contract.status = "SMS_SENT"
            contract.save()
            logger.info(f"Contract status updated to SMS_SENT")

            response_msg = f"""  Договор отправлен в чат!

            Номер: {contract.contract_number}
            Стоимость: {int(contract.template.base_cost):,} руб

            <b>Код подтверждения отправлен на вашу почту</b>

            Проверьте email и введите код для подписания договора."""
            
            logger.info(f"=== CONTRACT GENERATION COMPLETED SUCCESSFULLY ===")
            return response_msg
        except Exception as e:
            logger.error(f"=== CONTRACT GENERATION FAILED ===")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            logger.exception("Full contract generation error traceback:")
            return "Ошибка при создании договора. Наш менеджер скоро свяжется с вами."

    def _parse_pipe_format(self, lead, data_str: str) -> Dict:
        """
        Parse pipe-delimited format from AI command:
        ФИО|ДД.ММ.ГГГГ|серия ХХХХ номер ХХХХХХ|адрес|телефон|email|статья|инстанция|WITH_POA/WITHOUT_POA
        """
        try:
            logger.info(f"=== PARSING PIPE FORMAT ===")
            parts = [p.strip() for p in data_str.split("|")]
            logger.info(f"Split into {len(parts)} parts")
            
            if len(parts) < 9:
                logger.warning(f"Pipe format incomplete: {len(parts)} parts, expected 9")
                logger.warning(f"Parts: {parts}")
                return None
            
            # Parse passport (format: "серия 1234 номер 123456")
            passport_str = parts[2]
            series_match = re.search(r"серия\s*(\d{4})", passport_str, re.IGNORECASE)
            number_match = re.search(r"номер\s*(\d{6})", passport_str, re.IGNORECASE)
            
            passport_series = series_match.group(1) if series_match else ""
            passport_number = number_match.group(1) if number_match else ""
            
            contract_data = {
                "client_full_name": parts[0],
                "birth_date": parts[1],
                "client_passport_series": passport_series,
                "client_passport_number": passport_number,
                "client_passport_issued_by": "",
                "client_passport_issued_date": "",
                "birth_place": "",
                "client_address": parts[3],
                "client_phone": parts[4],
                "email": parts[5],
                "case_article": parts[6],
                "case_description": lead.case_description or "",
                "total_amount": None,
                "prepayment": None,
                "prepayment_percent": None,
                "success_fee": None,
                "success_fee_percent": None,
                "docs_prep_fee": 5000,
                "payment_terms": "",
                "contract_date": datetime.now().strftime("%d.%m.%Y"),
                "instance": parts[7],
                "representation_type": parts[8].upper(),
                "director_name": "Шельмина Евгения Васильевича",
            }
            
            # Save email to lead if not set
            if contract_data["email"] and not lead.email:
                logger.info(f"Saving email to lead: {contract_data['email']}")
                lead.email = contract_data["email"]
                lead.save()
            
            # Save phone to lead if not set
            if contract_data["client_phone"] and not lead.phone_number:
                logger.info(f"Saving phone to lead: {contract_data['client_phone']}")
                lead.phone_number = contract_data["client_phone"]
                lead.save()
            
            logger.info(f"✅ Parsed pipe format successfully")
            logger.info(f"Payment fields - total: {contract_data.get('total_amount')}, prepay: {contract_data.get('prepayment')}, success: {contract_data.get('success_fee')}")
            return contract_data
            
        except Exception as e:
            logger.error(f"❌ Failed to parse pipe format: {e}")
            logger.exception("Pipe format parsing error:")
            return None

    def _send_contract_to_telegram(self, telegram_id: int, contract):
        try:
            logger.info(f"Sending contract {contract.contract_number} to Telegram user {telegram_id}")
            file_field = contract.generated_pdf
            
            if file_field and getattr(file_field, "path", None):
                file_path = file_field.path
                logger.info(f"Contract file path: {file_path}")
                
                url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendDocument"
                with open(file_path, "rb") as file:
                    files = {"document": file}
                    data = {
                        "chat_id": telegram_id,
                        "caption": f"📄 Договор №{contract.contract_number}\n\nПроверьте данные и введите код из email для подписания.",
                        "parse_mode": "HTML",
                    }
                    logger.info(f"Posting to Telegram API...")
                    response = requests.post(url, data=data, files=files, timeout=30)
                    response.raise_for_status()
                    logger.info(f"✅ Contract sent successfully to {telegram_id}")
            else:
                logger.error(f"❌ No generated file available for contract {contract.contract_number}")
                logger.error(f"File field: {file_field}, has path: {hasattr(file_field, 'path') if file_field else 'N/A'}")
        except Exception as e:
            logger.error(f"❌ Failed to send contract file to {telegram_id}: {str(e)}")
            logger.exception("Telegram send error traceback:")

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

        # Parse passport series and number (handles multiple formats)
        # Try explicit "серия XXXX номер XXXXXX" format
        pass_match = re.search(
            r"(?:серия|series)[:\s]*(\d{4})[\s-]*(?:номер|number)[:\s]*(\d{6})", data_str, re.IGNORECASE
        )
        if pass_match:
            contract_data["client_passport_series"] = pass_match.group(1)
            contract_data["client_passport_number"] = pass_match.group(2)
        else:
            # Try "номер XXXXXX серия XXXX" (reversed)
            pass_match_rev = re.search(
                r"(?:номер|number)[:\s]*(\d{6})[\s-]*(?:серия|series)[:\s]*(\d{4})", data_str, re.IGNORECASE
            )
            if pass_match_rev:
                contract_data["client_passport_number"] = pass_match_rev.group(1)
                contract_data["client_passport_series"] = pass_match_rev.group(2)
            else:
                # Try standalone numbers (series 4 digits, number 6 digits)
                # Look for pattern like "2123 124214" or "номер 2123 серия 124214"
                numbers = re.findall(r"\b(\d{4,6})\b", data_str)
                if len(numbers) >= 2:
                    for i in range(len(numbers) - 1):
                        first = numbers[i]
                        second = numbers[i + 1]
                        # Series is 4 digits, number is 6 digits
                        if len(first) == 4 and len(second) == 6:
                            contract_data["client_passport_series"] = first
                            contract_data["client_passport_number"] = second
                            break
                        elif len(first) == 6 and len(second) == 4:
                            contract_data["client_passport_number"] = first
                            contract_data["client_passport_series"] = second
                            break

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

import random
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone

from leads.models import Lead
from contract_manager.services import ContractGenerationService


class Command(BaseCommand):
    help = "Generate a sample contract PDF for testing the PDF writer."

    def add_arguments(self, parser):
        parser.add_argument("--lead-id", type=int, default=None, help="Existing Lead ID to use")
        parser.add_argument("--region", type=str, default="REGIONS", help="Region: REGIONS or MOSCOW")
        parser.add_argument("--instance", type=str, default="2", help="Court instance: 1/2/3/4")
        parser.add_argument(
            "--representation",
            type=str,
            default="WITHOUT_POA",
            help="Representation type: WITHOUT_POA or WITH_POA",
        )
        parser.add_argument(
            "--debug-grid",
            action="store_true",
            help="Overlay coordinate grid to calibrate positions",
        )

    def handle(self, *args, **options):
        lead_id = options.get("lead_id")
        region = options.get("region")
        instance = options.get("instance")
        representation = options.get("representation")

        lead = None
        if lead_id:
            lead = Lead.objects.filter(id=lead_id).first()
            if not lead:
                self.stderr.write(self.style.ERROR(f"Lead with id={lead_id} not found"))
                return
        else:
            # Create a temporary test lead
            lead = Lead.objects.create(
                first_name="Иван",
                last_name="Иванов",
                telegram_id=random.randint(10_000_000, 99_999_999),
                region=region,
                case_type="DUI",
                case_description="Остановили ночью, алкотестер показал 0.14. Видео нет.",
                status="WARM",
            )

        self.stdout.write(self.style.NOTICE(f"Using Lead id={lead.id}, region={lead.region}"))

        service = ContractGenerationService()
        contract_data = {
            # Identity
            "client_full_name": f"{lead.first_name} {lead.last_name}",
            "client_passport_series": "1234",
            "client_passport_number": "567890",
            "client_address": "г. Москва, ул. Пример, д. 1",
            "client_phone": "+7 900 000-00-00",
            "email": "client@example.com",
            "birth_date": "12.03.1990",
            "birth_place": "г. Москва",
            # Case
            "case_article": "ч.1 ст. 12.8 КоАП РФ",
            "case_description": lead.case_description,
            # Money
            # total_amount will default to template.base_cost if omitted
            "prepayment": 10000,
            "success_fee": 15000,
            "docs_prep_fee": 5000,
            # Template params
            "instance": instance,
            "representation_type": representation,
            # Dates
            "contract_date": datetime.now().strftime("%d.%m.%Y"),
            # Debug overlay
            "_debug_grid": bool(options.get("debug_grid")),
        }

        contract = service.generate_contract(lead, contract_data)
        pdf_path = getattr(contract.generated_pdf, "path", None)
        if pdf_path:
            self.stdout.write(self.style.SUCCESS(f"Generated contract: {contract.contract_number}"))
            self.stdout.write(self.style.SUCCESS(f"PDF saved to: {pdf_path}"))
        else:
            self.stderr.write(self.style.ERROR("Contract PDF was not saved"))

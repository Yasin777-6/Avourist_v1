"""
Management command to generate all contract types with sample data.
This will create filled DOC/DOCX files for all contract templates.
"""
import random
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone

from leads.models import Lead
from contract_manager.services import ContractGenerationService


class Command(BaseCommand):
    help = "Generate all contract types with sample data for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--lead-id", 
            type=int, 
            default=None, 
            help="Existing Lead ID to use (optional)"
        )
        parser.add_argument(
            "--region",
            type=str,
            default="both",
            help="Region: REGIONS, MOSCOW, or both (default: both)"
        )

    def handle(self, *args, **options):
        lead_id = options.get("lead_id")
        region_filter = options.get("region", "both").upper()

        # Sample data based on user's provided fields
        sample_data = {
            # Identity
            "client_full_name": "Тытюк Александр Михайлович",
            "client_passport_series": "4567",
            "client_passport_number": "123456",
            "client_address": "г. Москва, ул. Примерная, д. 10, кв. 5",
            "client_phone": "+7 900 123-45-67",
            "email": "tytyuk@example.com",
            "birth_date": "15.06.1985",
            "birth_place": "г. Москва",
            # Case
            "case_article": "ч.1 ст. 12.8 КоАП РФ",
            "case_description": "провести правовой анализ документов (материалов дела), подготовка ответа на требование каршеринга, подготовка претензии, подготовка Отзыва на исковое заявления, ответ на претензию, заявление в соответствующие органы",
            # Money (will be calculated based on template)
            "prepayment": 15000,
            "success_fee": 10000,
            "docs_prep_fee": 5000,
            # Dates
            "contract_date": datetime.now().strftime("%d.%m.%Y"),
            # Director
            "director_name": "Шельмина Евгения Васильевича",
        }

        # Define all combinations
        regions = []
        if region_filter == "BOTH":
            regions = ["REGIONS", "MOSCOW"]
        else:
            regions = [region_filter]

        instances = ["1", "2", "3", "4"]
        representation_types = ["WITHOUT_POA", "WITH_POA"]

        total_contracts = len(regions) * len(instances) * len(representation_types)
        self.stdout.write(
            self.style.NOTICE(
                f"Generating {total_contracts} contracts ({len(regions)} regions × {len(instances)} instances × {len(representation_types)} types)"
            )
        )

        service = ContractGenerationService()
        generated = 0
        failed = 0

        for region in regions:
            for instance in instances:
                for rep_type in representation_types:
                    # Create or use lead
                    if lead_id:
                        lead = Lead.objects.filter(id=lead_id).first()
                        if not lead:
                            self.stderr.write(
                                self.style.ERROR(f"Lead with id={lead_id} not found")
                            )
                            return
                    else:
                        # Create a temporary test lead for each contract
                        lead = Lead.objects.create(
                            first_name="Александр",
                            last_name="Тытюк",
                            telegram_id=random.randint(10_000_000, 99_999_999),
                            region=region,
                            case_type="DUI",
                            case_description=sample_data["case_description"],
                            status="WARM",
                        )

                    # Prepare contract data
                    contract_data = dict(sample_data)
                    contract_data["instance"] = instance
                    contract_data["representation_type"] = rep_type

                    # Add representation clause based on type
                    if rep_type == "WITH_POA":
                        contract_data["representation_clause"] = (
                            "Исполнитель представляет интересы Заказчика в суде "
                            "и в иных органах по нотариальной доверенности без личного присутствия."
                        )
                    else:
                        contract_data["representation_clause"] = (
                            "Исполнитель не представляет интересы Заказчика в суде. "
                            "Заказчик участвует лично."
                        )

                    try:
                        # Generate contract
                        contract = service.generate_contract(lead, contract_data)
                        pdf_path = getattr(contract.generated_pdf, "path", None)

                        if pdf_path:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"✓ {region} | Instance {instance} | {rep_type} → {contract.contract_number}"
                                )
                            )
                            self.stdout.write(f"  File: {pdf_path}")
                            generated += 1
                        else:
                            self.stderr.write(
                                self.style.WARNING(
                                    f"⚠ {region} | Instance {instance} | {rep_type} → No file saved"
                                )
                            )
                            failed += 1

                    except Exception as e:
                        self.stderr.write(
                            self.style.ERROR(
                                f"✗ {region} | Instance {instance} | {rep_type} → {str(e)}"
                            )
                        )
                        failed += 1

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS(f"Generated: {generated}/{total_contracts}")
        )
        if failed > 0:
            self.stdout.write(self.style.ERROR(f"Failed: {failed}/{total_contracts}"))
        self.stdout.write("=" * 60)

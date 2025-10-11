from django.core.management.base import BaseCommand
from django.conf import settings
from contract_manager.models import ContractTemplate
from decimal import Decimal


class Command(BaseCommand):
    help = 'Set up initial contract templates from contracts directory'
    
    def handle(self, *args, **options):
        self.stdout.write('Setting up contract templates...')
        
        # Template configurations based on contracts directory
        templates = [
            # Without Power of Attorney - Regions
            {
                'name': 'Без представления БЕЗ доверенности - 1 инст. (Регионы)',
                'case_type': 'OTHER',
                'instance': '1',
                'representation_type': 'WITHOUT_POA',
                'region': 'REGIONS',
                'template_file': 'Договор_без_представления_интересов_БЕЗ_ДОВЕРЕННОСТИ_на_1_инстанцию.pdf',
                'base_cost': Decimal('15000'),
                'success_fee': Decimal('10000'),
            },
            {
                'name': 'Без представления БЕЗ доверенности - 2 инст. (Регионы)',
                'case_type': 'OTHER',
                'instance': '2',
                'representation_type': 'WITHOUT_POA',
                'region': 'REGIONS',
                'template_file': 'Договор_без_представления_интересов_БЕЗ_ДОВЕРЕННОСТИ_на_2_инстанции.pdf',
                'base_cost': Decimal('35000'),
                'success_fee': Decimal('15000'),
            },
            {
                'name': 'Без представления БЕЗ доверенности - 3 инст. (Регионы)',
                'case_type': 'OTHER',
                'instance': '3',
                'representation_type': 'WITHOUT_POA',
                'region': 'REGIONS',
                'template_file': 'Договор_без_представления_интересов_БЕЗ_ДОВЕРЕННОСТИ_на_3_инстанции.pdf.pdf',
                'base_cost': Decimal('53000'),
                'success_fee': Decimal('15000'),
            },
            {
                'name': 'Без представления БЕЗ доверенности - 4 инст. (Регионы)',
                'case_type': 'OTHER',
                'instance': '4',
                'representation_type': 'WITHOUT_POA',
                'region': 'REGIONS',
                'template_file': 'Договор_без_представления_интересов_БЕЗ_ДОВЕРЕННОСТИ_на_4_инстанции.pdf',
                'base_cost': Decimal('70000'),
                'success_fee': Decimal('15000'),
            },
            
            # With Power of Attorney - Regions
            {
                'name': 'Без представления ПО доверенности - 1 инст. (Регионы)',
                'case_type': 'OTHER',
                'instance': '1',
                'representation_type': 'WITH_POA',
                'region': 'REGIONS',
                'template_file': 'Договор_без_представления_интересов_ПО_ДОВЕРЕННОСТИ_на_1_инстанцию.pdf.pdf',
                'base_cost': Decimal('25000'),
                'success_fee': Decimal('10000'),
            },
            {
                'name': 'Без представления ПО доверенности - 2 инст. (Регионы)',
                'case_type': 'OTHER',
                'instance': '2',
                'representation_type': 'WITH_POA',
                'region': 'REGIONS',
                'template_file': 'Договор_без_представления_интересов_ПО_ДОВЕРЕННОСТИ_на_2_инстанции.pdf.pdf',
                'base_cost': Decimal('45000'),
                'success_fee': Decimal('10000'),
            },
            
            # Moscow templates
            {
                'name': 'Без представления БЕЗ доверенности - 2 инст. (Москва)',
                'case_type': 'OTHER',
                'instance': '2',
                'representation_type': 'WITHOUT_POA',
                'region': 'MOSCOW',
                'template_file': 'Договор_без_представления_интересов_БЕЗ_ДОВЕРЕННОСТИ_на_2_инстанции-_2_.pdf',
                'base_cost': Decimal('60000'),
                'success_fee': Decimal('20000'),
            },
            
            # Criminal case template (264.1 УК РФ)
            {
                'name': 'Уголовное дело 264.1 УК РФ - 1 инст.',
                'case_type': 'CRIMINAL',
                'instance': '1',
                'representation_type': 'WITHOUT_POA',
                'region': 'REGIONS',
                'template_file': 'Договор_без_представления_интересов_БЕЗ_ДОВЕРЕННОСТИ_на_1_инстанцию.pdf',
                'base_cost': Decimal('35000'),
                'success_fee': Decimal('20000'),
            },
        ]
        
        # Required fields for all templates
        required_fields = [
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
            'total_amount',
            'login_credentials',
            'password_credentials'
        ]
        
        created_count = 0
        updated_count = 0
        
        for template_data in templates:
            template_data['required_fields'] = required_fields
            
            template, created = ContractTemplate.objects.get_or_create(
                case_type=template_data['case_type'],
                instance=template_data['instance'],
                representation_type=template_data['representation_type'],
                region=template_data['region'],
                defaults=template_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created template: {template.name}')
                )
            else:
                # Update existing template
                for key, value in template_data.items():
                    setattr(template, key, value)
                template.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated template: {template.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Template setup complete! Created: {created_count}, Updated: {updated_count}'
            )
        )

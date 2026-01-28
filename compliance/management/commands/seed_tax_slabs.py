from django.core.management.base import BaseCommand
from compliance.models import TaxSlab
import datetime

class Command(BaseCommand):
    help = 'Seeds Tax Slabs from LOGICS.txt'

    def handle(self, *args, **options):
        # Current FY
        today = datetime.date.today()
        start_year = today.year if today.month >= 4 else today.year - 1
        fy = f"{start_year}-{start_year+1}"
        
        self.stdout.write(f"Seeding Tax Slabs for FY {fy}...")
        
        # Clear existing for this year to avoid dupes/confusion
        TaxSlab.objects.filter(financial_year=fy).delete()
        
        # NEW REGIME (FY 2023-24 / assumed current)
        print("Seeding NEW Regime Slabs...")
        slabs_new = [
            (0, 300000, 0),
            (300001, 600000, 5),
            (600001, 900000, 10),
            (900001, 1200000, 15),
            (1200001, 1500000, 20),
            (1500001, None, 30),
        ]
        
        for min_inc, max_inc, rate in slabs_new:
            TaxSlab.objects.create(
                regime=TaxSlab.Regime.NEW,
                financial_year=fy,
                min_income=min_inc,
                max_income=max_inc,
                tax_rate=rate,
                cess_percent=4.0
            )
            
        # OLD REGIME
        print("Seeding OLD Regime Slabs...")
        slabs_old = [
            (0, 250000, 0),
            (250001, 500000, 5),
            (500001, 1000000, 20),
            (1000001, None, 30),
        ]
        
        for min_inc, max_inc, rate in slabs_old:
            TaxSlab.objects.create(
                regime=TaxSlab.Regime.OLD,
                financial_year=fy,
                min_income=min_inc,
                max_income=max_inc,
                tax_rate=rate,
                cess_percent=4.0
            )
            
        self.stdout.write(self.style.SUCCESS('Successfully seeded Tax Slabs'))

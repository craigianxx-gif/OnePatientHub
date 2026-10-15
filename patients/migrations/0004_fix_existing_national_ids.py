import re
import random
from django.db import migrations

def fix_national_ids(apps, schema_editor):
    Patient = apps.get_model('patients', 'Patient')
    pattern = r'^\d{2}-\d{7}[A-Z]-\d{2}$'
    
    updated_count = 0
    for patient in Patient.objects.all():
        if not patient.national_id or not re.match(pattern, patient.national_id):
            district = f"{random.randint(10, 89):02d}"
            serial = f"{random.randint(1000000, 9999999)}"
            letter = random.choice("ABCDEFGHJKLMNPRSTUVWXY")
            suffix = f"{random.randint(10, 99):02d}"
            
            patient.national_id = f"{district}-{serial}{letter}-{suffix}"
            patient.save()
            updated_count += 1
            
    print(f"\nSuccessfully updated {updated_count} legacy patient National IDs to match the required format.")

class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0003_remove_externalpatientidentifier_facility_name_and_more'),
    ]

    operations = [
        migrations.RunPython(fix_national_ids),
    ]
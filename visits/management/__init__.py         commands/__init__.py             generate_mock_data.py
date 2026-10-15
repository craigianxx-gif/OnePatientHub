import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from patients.models import Patient
from visits.models import Visit
from referrals.models import Referral
from facilities.models import Facility

class Command(BaseCommand):
    help = 'Generates high-fidelity mock data for OnePatient Hub MVP presentation'

    def handle(self, *args, **kwargs):
        self.stdout.write("Initializing Mock Data Generation...")
        
        # 1. Generate Facilities
        self.stdout.write("Generating Facilities...")
        facility_data = [
            ("Harare Central Hospital", "Hospital", "HARARE", "Harare"),
            ("Mpilo Central Hospital", "Hospital", "BULAWAYO", "Bulawayo"),
            ("Epworth Polyclinic", "Clinic", "HARARE", "Epworth"),
            ("Mutare Provincial", "Hospital", "MANICALAND", "Mutare"),
            ("Plumtree District Hospital", "Health Centre", "MAT_SOUTH", "Plumtree")
        ]
        
        facilities = []
        for i, (name, f_type, prov, dist) in enumerate(facility_data):
            f, created = Facility.objects.get_or_create(
                facility_id=f"FAC-2026-{i+1:03d}",
                defaults={
                    'facility_name': name,
                    'facility_type': f_type,
                    'province': prov,
                    'district': dist,
                    'physical_address': f"123 Main St, {dist}",
                    'dhis2_code': f"OPH-{prov[:3]}-{i+1:03d}"
                }
            )
            facilities.append(f)

        # 2. Generate Patients
        self.stdout.write("Generating 150 Patients...")
        first_names_m = ['Takudzwa', 'Tinashe', 'Tendai', 'Farai', 'Kudzi', 'Tatenda', 'Nyasha']
        first_names_f = ['Chipo', 'Rutendo', 'Rumbidzai', 'Nyasha', 'Tariro', 'Munashe', 'Ruvarashe']
        last_names = ['Moyo', 'Sibanda', 'Ncube', 'Ndlovu', 'Mutasa', 'Chauke', 'Gumbo', 'Shumba']
        
        patients = []
        for i in range(150):
            gender = random.choice(['Male', 'Female'])
            fname = random.choice(first_names_m) if gender == 'Male' else random.choice(first_names_f)
            lname = random.choice(last_names)
            
            age_days = random.randint(5 * 365, 65 * 365)
            dob = timezone.now().date() - timedelta(days=age_days)
            
            # Assuming Patient model has these standard fields based on previous context
            p, created = Patient.objects.get_or_create(
                oph_id=f"OPH-{random.randint(10000, 99999)}",
                defaults={
                    'first_name': fname,
                    'last_name': lname,
                    'gender': gender,
                    'date_of_birth': dob,
                }
            )
            patients.append(p)

        # 3. Generate Visits (Structured DHIS2 Data)
        self.stdout.write("Generating 400 Clinical Visits...")
        diseases = ['Asthma', 'Anxiety', 'Diabetes', 'Hypertension', 'Cervix', 'Fever', 'Cough']
        
        for _ in range(400):
            patient = random.choice(patients)
            facility = random.choice(facilities)
            
            days_ago = random.randint(0, 90)
            visit_date = timezone.now().date() - timedelta(days=days_ago)
            
            v_type = random.choice(['OPD', 'OPD', 'OPD', 'ANC', 'DEL', 'PNC', 'Emergency'])
            t_type = random.choice(['NONE', 'NONE', 'HIV', 'TB', 'MALARIA'])
            
            if t_type == 'NONE':
                t_result = 'N/A'
            else:
                t_result = random.choice(['NEGATIVE', 'NEGATIVE', 'POSITIVE', 'PENDING'])
            
            Visit.objects.create(
                patient=patient,
                facility=facility,
                visit_date=visit_date,
                visit_type=v_type,
                test_type=t_type,
                test_result=t_result,
                diagnosis=random.choice(diseases) if t_type == 'NONE' else f"Screening for {t_type}",
                reason="Routine presentation",
                healthcare_provider="Dr. Sibanda"
            )

        # 4. Generate Referrals
        self.stdout.write("Generating 45 Referrals...")
        for _ in range(45):
            Referral.objects.create(
                patient=random.choice(patients),
                referred_from=random.choice(facilities),
                reason=random.choice(['Specialist Consult', 'X-Ray required', 'Severe Symptoms']),
                status=random.choice(['Pending', 'Accepted', 'Completed']),
                created_at=timezone.now() - timedelta(days=random.randint(0, 30))
            )

        self.stdout.write(self.style.SUCCESS('SUCCESS: OnePatient Hub MVP Data Generation Complete!'))
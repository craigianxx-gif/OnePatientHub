from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from patients.models import Patient

class FHIRPatientAPITests(APITestCase):
    def setUp(self):
        # Create a sample patient record for testing
        self.patient = Patient.objects.create(
            first_name="John",
            last_name="Doe",
            gender="Male",
            date_of_birth="1995-04-12",
            phone_number="+263771234567",
            address="Harare, Zimbabwe"
        )
        self.list_url = reverse('fhir_patient_list')
        self.detail_url = reverse('fhir_patient_detail', kwargs={'pk': self.patient.pk})

    def test_get_patient_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['resourceType'], 'Bundle')
        self.assertEqual(response.data['total'], 1)

    def test_get_patient_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['resourceType'], 'Patient')
        self.assertEqual(response.data['id'], str(self.patient.id))
        self.assertEqual(response.data['name'][0]['family'], 'Doe')
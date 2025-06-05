from django.test import TestCase
from django.urls import reverse
from datetime import datetime, timedelta
from api.models import Target, DomainCheck  # Adjust import if models are elsewhere

class DomainCheckTestCase(TestCase):
    def setUp(self):
        self.target = Target.objects.create(url="https://newvell.com")
        self.domain_check = DomainCheck.objects.create(
            target_url=self.target,
            expires_at=datetime.now() + timedelta(days=100),
            days_to_expiry=100,
        )

    def test_domain_check_str(self):
        """Test the string representation of the DomainCheck model"""
        self.assertIn(self.target.url, str(self.domain_check))

    def test_api_domain_checks(self):
        """Test the domain-checks API endpoint returns expected data"""
        url = reverse('domaincheck-list')  # This must match your URL name in urls.py
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data) > 0)
        self.assertIn('target_url', data[0])
        self.assertEqual(data[0]['target_url']['url'], self.target.url)  # ✅ correct


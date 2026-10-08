from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Lead

VALID = {
    "sector": "ozel-ders", "goal": "musteri", "budget": "100-250", "has_content": "yok",
    "timeline": "hemen", "city": "ankara", "name": "Ayşe Yılmaz", "company": "Yılmaz Fizik",
    "phone": "0541 000 00 00", "email": "ayse@example.com", "website": "@yilmazfizik",
    "message": "YKS fizik özel dersi veriyorum, online ve yüz yüze öğrenci arıyorum.",
    "kvkk": "on", "utm_source": "google", "source_page": "/sosyal-medya-ajansi/ankara/",
}


@override_settings(LEAD_NOTIFY_EMAILS=["owner@example.com"],
                   EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class LeadFlowTests(TestCase):
    def test_valid_lead_is_saved_scored_and_notified(self):
        resp = self.client.post(reverse("leads:submit"), VALID)
        self.assertRedirects(resp, reverse("leads:thanks"))
        lead = Lead.objects.get()
        self.assertEqual(lead.score, 90)
        self.assertEqual(lead.tier, "A")
        self.assertEqual(lead.utm_source, "google")
        self.assertTrue(lead.notified)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Ayşe Yılmaz", mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].reply_to, ["ayse@example.com"])
        self.assertEqual(lead.whatsapp_url, "https://wa.me/905410000000")

    def test_low_budget_is_saved_as_c_tier(self):
        self.client.post(reverse("leads:submit"), {**VALID, "budget": "lt50", "timeline": "arastiriyorum"})
        self.assertEqual(Lead.objects.get().tier, "C")

    def test_missing_consent_rejected(self):
        data = {k: v for k, v in VALID.items() if k != "kvkk"}
        resp = self.client.post(reverse("leads:submit"), data)
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(Lead.objects.exists())

    def test_honeypot_silently_drops(self):
        resp = self.client.post(reverse("leads:submit"), {**VALID, "fax": "spam"})
        self.assertRedirects(resp, reverse("leads:thanks"))
        self.assertFalse(Lead.objects.exists())

    @override_settings(LEAD_NOTIFY_EMAILS=[])
    def test_lead_saved_even_without_notify_config(self):
        self.client.post(reverse("leads:submit"), VALID)
        self.assertFalse(Lead.objects.get().notified)


class Ga4Tests(TestCase):
    def test_cookie_parsing(self):
        from .ga4 import parse_client_id, parse_session_id
        self.assertEqual(parse_client_id("GA1.1.123456789.1700000000"), "123456789.1700000000")
        self.assertEqual(parse_client_id(""), "")
        self.assertEqual(parse_session_id("GS1.1.1700000000.3.1.1700000100.0.0.0"), "1700000000")
        self.assertEqual(parse_session_id("GS2.1.s1700000000$o3$g1$t1700000100"), "1700000000")

    @override_settings(GA4_ID="G-TEST123", GA4_API_SECRET="secret", LEAD_NOTIFY_EMAILS=[])
    def test_cookies_captured_and_status_change_sends_mp_event(self):
        from unittest import mock
        self.client.cookies["_ga"] = "GA1.1.111.222"
        self.client.cookies["_ga_TEST123"] = "GS2.1.s1700000000$o1"
        self.client.post(reverse("leads:submit"), {**VALID, "gclid": "abc123"})
        lead = Lead.objects.get()
        self.assertEqual((lead.ga_client_id, lead.ga_session_id, lead.gclid), ("111.222", "1700000000", "abc123"))

        with mock.patch("apps.leads.ga4.requests.post") as post:
            post.return_value.raise_for_status.return_value = None
            lead.status = "won"
            lead.deal_value = 90000
            lead.save()
            lead.notes = "no status change"
            lead.save()
        self.assertEqual(post.call_count, 1)
        body = post.call_args.kwargs["json"]
        self.assertEqual(body["client_id"], "111.222")
        event = body["events"][0]
        self.assertEqual(event["name"], "close_convert_lead")
        self.assertEqual(event["params"]["value"], 90000)
        self.assertEqual(event["params"]["session_id"], "1700000000")

    def test_thanks_page_emits_generate_lead_payload_once(self):
        self.client.post(reverse("leads:submit"), VALID)
        first = self.client.get(reverse("leads:thanks"))
        self.assertContains(first, 'id="lead-event"')
        self.assertContains(first, '"value": 90000')
        second = self.client.get(reverse("leads:thanks"))
        self.assertNotContains(second, 'id="lead-event"')

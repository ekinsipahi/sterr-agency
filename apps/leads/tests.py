import hashlib

from django.core import mail
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from .ga4 import hashed_user_data
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


class HashedUserDataTests(SimpleTestCase):
    def test_turkish_numbers_become_e164_before_hashing(self):
        expected = hashlib.sha256(b"+905321234567").hexdigest()
        for raw in ("0532 123 45 67", "5321234567", "+90 532 123 45 67", "905321234567"):
            self.assertEqual(hashed_user_data("", raw, "90")["sha256_phone_number"], expected, raw)

    def test_email_normalised_and_unknown_country_phone_skipped(self):
        data = hashed_user_data(" Ali@Example.COM ", "0151 2345678")
        self.assertEqual(data, {"sha256_email_address": hashlib.sha256(b"ali@example.com").hexdigest()})
        self.assertIn("sha256_phone_number", hashed_user_data("", "+49 151 2345678"))


class PhoneBookTests(TestCase):
    """The admin page that lists every phone number the forms collected."""

    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth import get_user_model

        from apps.dental.models import DentalInquiry
        from apps.growth.models import AgencySubscription
        from apps.intl.models import IntlLead

        User = get_user_model()
        cls.admin = User.objects.create_superuser("boss", "boss@example.com", "x")
        cls.staff = User.objects.create_user("helper", "helper@example.com", "x", is_staff=True)
        cls.lead = Lead.objects.create(name="Ayşe Yılmaz", company="Yılmaz Fizik", phone="0541 000 00 00",
                                       email="ayse@example.com", sector="ozel-ders", goal="musteri", budget="100-250",
                                       has_content="yok", timeline="hemen", city="ankara")
        IntlLead.objects.create(lang="en", name="John Smith", email="john@example.com", phone="+44 20 7946 0958",
                                country="UK", interest="sosyal-medya-ajansi")
        DentalInquiry.objects.create(lang="de", name="Anna Müller", email="anna@example.com", phone="+49 151 2345678",
                                     country="Deutschland", treatment="implants")
        cls.sub = AgencySubscription.objects.create(email="creator@example.com", platform="tiktok", handle="creator.one",
                                                    plan="rising", amount="149.99", phone="+4915123456789")
        AgencySubscription.objects.create(email="old@example.com", handle="no.phone", plan="starter", amount="79.99")
        cls.url = reverse("admin:leads_phonebook_changelist")

    def test_lists_every_form_with_whose_number_and_why(self):
        self.client.force_login(self.admin)
        html = self.client.get(self.url).content.decode()
        for text in ("0541 000 00 00", "+44 20 7946 0958", "+49 151 2345678", "+4915123456789",   # the four numbers
                     "Ayşe Yılmaz", "John Smith", "Anna Müller", "@creator.one",                    # whose
                     "Influencer ile iletişimde kalmak", "Ajans başvurusuna telefonla",            # why
                     "https://wa.me/905410000000", "https://wa.me/4915123456789",
                     reverse("admin:growth_agencysubscription_change", args=[self.sub.pk]),
                     reverse("admin:leads_lead_change", args=[self.lead.pk])):
            self.assertIn(text, html)
        self.assertIn("<b>4</b> numara", html)
        self.assertNotIn("no.phone", html)   # a subscription from before the phone field has no row

    def test_search_and_form_filter(self):
        self.client.force_login(self.admin)
        html = self.client.get(self.url, {"q": "creator"}).content.decode()
        self.assertIn("@creator.one", html)
        self.assertNotIn("Ayşe Yılmaz", html)
        html = self.client.get(self.url, {"source": "dental"}).content.decode()
        self.assertIn("Anna Müller", html)
        self.assertNotIn("John Smith", html)
        self.assertIn("Ayşe Yılmaz", self.client.get(self.url, {"q": "0541 000"}).content.decode())   # by phone digits

    def test_only_staff_with_the_permission(self):
        self.assertEqual(self.client.get(self.url).status_code, 302)           # not signed in: to the admin login
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(self.url).status_code, 403)           # staff without the permission
        from django.contrib.auth.models import Permission

        self.staff.user_permissions.add(Permission.objects.get(codename="view_phonebook"))
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_shown_in_the_admin_index(self):
        self.client.force_login(self.admin)
        self.assertIn("Telefon rehberi (tüm formlar)", self.client.get(reverse("admin:index")).content.decode())

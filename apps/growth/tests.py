import json
import re
from types import SimpleNamespace
from unittest import mock

import stripe
from django.core import mail, signing
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils.html import escape

from apps.core.languages import LANGS

from .content import CONTENT, PAGES, alternates, page_path, routes
from .forms import clean_handle
from .models import GrowthSubscription, StripeEvent
from .views import MANAGE_SALT

WEBHOOK_SECRET = "whsec_test"
STRIPE_ON = dict(STRIPE_SECRET_KEY="sk_test_x", STRIPE_PRICE_ID="price_x", STRIPE_WEBHOOK_SECRET=WEBHOOK_SECRET,
                 LEAD_NOTIFY_EMAILS=["owner@example.com"], EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")


def shape(value):
    if isinstance(value, dict):
        return {k: shape(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [shape(v) for v in value]
    return type(value).__name__


class ContentTests(SimpleTestCase):
    def test_all_sixteen_languages_share_the_english_structure(self):
        self.assertEqual(set(CONTENT), {lang.code for lang in LANGS})
        reference = shape({k: v for k, v in CONTENT["en"].items() if k != "geo"})
        for code, data in CONTENT.items():
            with self.subTest(code=code):
                self.assertEqual(shape({k: v for k, v in data.items() if k != "geo"}), reference)

    def test_meta_lengths_unique_titles_and_organic_wording(self):
        titles = set()
        for code, data in CONTENT.items():
            for page in PAGES:
                p = data[page]
                with self.subTest(code=code, page=page):
                    self.assertLessEqual(len(p["title"]), 68)
                    self.assertLessEqual(len(p["description"]), 165)
                    self.assertRegex((p["title"] + p["description"]).lower(),
                                     r"organi|orgáni|طبيعي|органі|органи|orqanik")
                titles.add(p["title"])
        self.assertEqual(len(titles), len(CONTENT) * len(PAGES))

    def test_no_forbidden_claims(self):
        blob = json.dumps(CONTENT, ensure_ascii=False).lower()
        for word in ("guarantee", "garanti", "buzzoid", "passthevote", "stormlikes"):
            self.assertNotIn(word, blob)

    def test_alternates_cover_every_language(self):
        alts = dict(alternates("pricing"))
        self.assertEqual(len(alts), 17)
        self.assertEqual(alts["x-default"], alts["en"])
        self.assertEqual(alternates("geo:uk"), [])

    def test_handle_cleaning(self):
        for raw in ("@Brand.Name", "brand.name", "https://www.instagram.com/brand.name/?igsh=abc", "instagram.com/brand.name"):
            self.assertEqual(clean_handle(raw).lower(), "brand.name")


class PageTests(TestCase):
    def test_every_page_renders_with_hreflang(self):
        for route, code, page in routes():
            with self.subTest(route=route):
                html = self.client.get("/" + route).content.decode()
                self.assertIn(f'<html lang="{code}"', html)
                expected = 0 if page.startswith("geo:") else 17
                self.assertEqual(len(re.findall(r'<link rel="alternate" hreflang=', html)), expected)
                self.assertIn('data-growth-form', html)

    def test_sitemap_lists_growth_pages(self):
        body = self.client.get("/sitemap.xml").content.decode()
        self.assertIn(f"{page_path('de', 'main')}</loc>", body)
        self.assertIn(f"{page_path('en', 'geo:uk')}</loc>", body)


def post_form(client, **extra):
    data = {"lang": "en", "page": "main", "instagram": "@My.Brand", "location": "London, UK",
            "email": "Owner@Example.com", "consent": "on", **extra}
    return client.post(reverse("growth:checkout"), data)


@override_settings(STRIPE_SECRET_KEY="", STRIPE_PRICE_ID="", LEAD_NOTIFY_EMAILS=["owner@example.com"],
                   EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class CheckoutWithoutStripeTests(TestCase):
    def test_request_is_saved_and_team_notified(self):
        r = post_form(self.client)
        self.assertRedirects(r, f"{reverse('growth:success')}?lang=en&pending=1", fetch_redirect_response=False)
        sub = GrowthSubscription.objects.get()
        self.assertEqual((sub.instagram, sub.email, sub.status), ("my.brand", "owner@example.com", "pending"))
        self.assertIn("@my.brand", mail.outbox[0].subject)

    def test_invalid_handle_shows_error_in_page_language(self):
        r = post_form(self.client, lang="tr", instagram="not a handle!")
        self.assertEqual(r.status_code, 400)
        self.assertContains(r, escape(CONTENT["tr"]["ui"]["err_instagram"]), status_code=400)
        self.assertFalse(GrowthSubscription.objects.exists())


@override_settings(**STRIPE_ON)
class CheckoutWithStripeTests(TestCase):
    def test_redirects_to_stripe_checkout(self):
        session = SimpleNamespace(id="cs_test_1", url="https://checkout.stripe.com/c/pay/cs_test_1")
        with mock.patch("apps.growth.billing.create_checkout", return_value=session) as create:
            r = post_form(self.client)
        self.assertEqual(r.status_code, 303)
        self.assertEqual(r["Location"], session.url)
        sub = GrowthSubscription.objects.get()
        self.assertEqual(sub.stripe_checkout_session_id, "cs_test_1")
        success_url = create.call_args.args[1]
        self.assertIn("session_id={CHECKOUT_SESSION_ID}", success_url)

    def test_stripe_error_keeps_visitor_on_page(self):
        with mock.patch("apps.growth.billing.create_checkout", side_effect=stripe.APIConnectionError("down")):
            r = post_form(self.client)
        self.assertContains(r, escape(CONTENT["en"]["ui"]["err_payment"]), status_code=502)


def signed(payload):
    body = json.dumps(payload)
    return body, stripe.WebhookSignature.generate_signature_header(body, WEBHOOK_SECRET)


@override_settings(**STRIPE_ON)
class WebhookTests(TestCase):
    def setUp(self):
        self.sub = GrowthSubscription.objects.create(email="a@example.com", instagram="brand", location="Berlin", lang="de")

    def send(self, event_id, event_type, obj):
        body, header = signed({"id": event_id, "type": event_type, "data": {"object": obj}})
        return self.client.post(reverse("growth:webhook"), body, content_type="application/json",
                                HTTP_STRIPE_SIGNATURE=header)

    def test_bad_signature_rejected(self):
        r = self.client.post(reverse("growth:webhook"), "{}", content_type="application/json",
                             HTTP_STRIPE_SIGNATURE="t=1,v1=nope")
        self.assertEqual(r.status_code, 400)

    def test_checkout_completed_activates_and_welcomes_once(self):
        obj = {"id": "cs_1", "client_reference_id": str(self.sub.pk), "customer": "cus_1", "subscription": "sub_1",
               "payment_status": "paid"}
        self.assertEqual(self.send("evt_1", "checkout.session.completed", obj).status_code, 200)
        self.assertEqual(self.send("evt_1", "checkout.session.completed", obj).content, b"duplicate")
        self.sub.refresh_from_db()
        self.assertEqual((self.sub.status, self.sub.stripe_customer_id, self.sub.stripe_subscription_id),
                         ("active", "cus_1", "sub_1"))
        self.assertTrue(self.sub.welcomed)
        to = sorted(m.to[0] for m in mail.outbox)
        self.assertEqual(to, ["a@example.com", "owner@example.com"])
        welcome = next(m for m in mail.outbox if m.to == ["a@example.com"])
        self.assertIn("@brand", welcome.subject)  # German copy, handle filled in
        self.assertEqual(StripeEvent.objects.count(), 1)

    def test_cancellation_and_end(self):
        self.sub.stripe_subscription_id = "sub_1"
        self.sub.status = "active"
        self.sub.save()
        updated = {"id": "sub_1", "customer": "cus_1", "status": "active", "cancel_at_period_end": True,
                   "items": {"data": [{"current_period_end": 1893456000}]}}
        self.send("evt_2", "customer.subscription.updated", updated)
        self.sub.refresh_from_db()
        self.assertTrue(self.sub.cancel_at_period_end)
        self.assertEqual(self.sub.current_period_end.year, 2030)
        self.send("evt_3", "customer.subscription.deleted", {**updated, "status": "canceled"})
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.status, "canceled")
        self.assertEqual(len(mail.outbox), 2)  # cancel scheduled + ended, both to the team

    def test_failed_invoice_marks_past_due(self):
        self.sub.stripe_subscription_id = "sub_1"
        self.sub.save()
        invoice = {"id": "in_1", "customer": "cus_1", "parent": {"subscription_details": {"subscription": "sub_1"}}}
        self.send("evt_4", "invoice.payment_failed", invoice)
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.status, "past_due")
        self.send("evt_5", "invoice.paid", invoice)
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.status, "active")


@override_settings(**STRIPE_ON)
class ManageTests(TestCase):
    def test_same_answer_and_link_only_for_known_email(self):
        GrowthSubscription.objects.create(email="a@example.com", instagram="brand", location="Rome", lang="it",
                                          stripe_customer_id="cus_1")
        for email in ("a@example.com", "nobody@example.com"):
            r = self.client.post(reverse("growth:manage"), {"email": email, "lang": "it"})
            self.assertContains(r, escape(CONTENT["it"]["ui"]["manage_sent"]))
        self.assertEqual([m.to for m in mail.outbox], [["a@example.com"]])
        link = re.search(r"https?://\S+/growth/manage/(\S+)/", mail.outbox[0].body)
        with mock.patch("apps.growth.billing.portal_url", return_value="https://billing.stripe.com/p/session") as portal:
            r = self.client.get(reverse("growth:portal", args=[link.group(1)]))
        self.assertEqual(r["Location"], "https://billing.stripe.com/p/session")
        self.assertEqual(portal.call_args.args[0], "cus_1")

    def test_tampered_token_goes_back_to_manage(self):
        token = signing.dumps({"c": "cus_1", "l": "en"}, salt=MANAGE_SALT) + "x"
        r = self.client.get(reverse("growth:portal", args=[token]))
        self.assertEqual(r["Location"], f"{reverse('growth:manage')}?expired=1")

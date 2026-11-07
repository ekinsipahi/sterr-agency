import json
import re
from datetime import timedelta
from io import StringIO
from types import SimpleNamespace
from unittest import mock

import requests
import stripe
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.core.languages import LANGS

from . import billing, linksterr
from .content import CONTENT, CREATORS, PAGES, PLATFORMS, UI, alternates, followers_menu, page_path, routes
from .forms import clean_handle
from .models import AccountActivity, AgencySubscription, Customer, Dispute, StripeEvent, SubscriptionStat
from .constants import TERMS_VERSION
from .plan import PLANS
from .validate import check

WEBHOOK_SECRET = "whsec_test"
MAIL = dict(LEAD_NOTIFY_EMAILS=["owner@example.com"], GROWTH_NOTIFY_EMAILS=["ekinsipahi8@gmail.com"],
            EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
STRIPE_ON = dict(GROWTH_PAYMENTS=True, STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET=WEBHOOK_SECRET, **MAIL)
STRIPE_OFF = dict(GROWTH_PAYMENTS=False, STRIPE_SECRET_KEY="", **MAIL)
CODES = {lang.code for lang in LANGS}
PERIOD_END = int((timezone.now() + timedelta(days=30)).timestamp())


def stripe_sub(status="active", sub_id="sub_1", **extra):
    """A Stripe subscription as webhooks deliver it (period end on the items, as in newer API versions)."""
    return {"id": sub_id, "object": "subscription", "status": status, "customer": "cus_1", "cancel_at_period_end": False,
            "items": {"data": [{"current_period_end": PERIOD_END}]}, "metadata": {}, **extra}


class ContentTests(SimpleTestCase):
    def test_every_language_and_platform_is_complete(self):
        self.assertEqual(set(UI), CODES)
        for platform in PLATFORMS:
            self.assertEqual(set(CONTENT[platform]), CODES, platform)
        self.assertEqual(set(CREATORS), CODES)

    def test_every_language_passes_the_copy_check(self):
        for code in sorted(UI):
            with self.subTest(code=code):
                self.assertEqual(check(code), [])

    def test_titles_are_unique_across_the_whole_language(self):
        for code in UI:
            titles = [CONTENT[pl][code][page]["title"] for pl in PLATFORMS for page in PAGES]
            titles += [CREATORS[code][page]["title"] for page in CREATORS[code]["keywords"]]
            self.assertEqual(len(titles), len(set(titles)), code)

    def test_influencer_packages(self):
        self.assertEqual([p["key"] for p in PLANS], ["starter", "rising", "pro"])
        self.assertEqual([str(p["price"]) for p in PLANS], ["79.99", "149.99", "279.99"])
        self.assertEqual(PLANS[0]["followers"], (1000, 4000))
        for p in PLANS:  # 2–3 likes per new follower, about one comment per 10
            self.assertEqual(p["likes"], (p["followers"][0] * 2, p["followers"][1] * 3))
            self.assertEqual(p["comments"], (p["followers"][0] // 10, p["followers"][1] // 10))

    def test_alternates_and_routes(self):
        alts = dict(alternates("likes", "tiktok"))
        self.assertEqual(len(alts), len(CONTENT["tiktok"]) + 1)
        self.assertEqual(alts["x-default"], alts["en"])
        self.assertEqual(alts["en"], "/en/tiktok-likes-packages/")
        self.assertEqual(alternates("geo:uk"), [])
        paths = [r[0] for r in routes()]
        self.assertEqual(len(paths), len(set(paths)))

    def test_followers_menu_has_every_section_and_the_account(self):
        labels = [label for label, url in followers_menu("en")]
        self.assertEqual(labels, ["Instagram Followers", "Instagram Packages", "Instagram Likes", "Instagram Views", "Instagram Comments",
                                  "TikTok Followers", "TikTok Packages", "TikTok Likes", "TikTok Views", "TikTok Comments",
                                  "For creators", "My account"])

    def test_handle_cleaning(self):
        for raw in ("@Brand.Name", "brand.name", "https://www.instagram.com/brand.name/?igsh=abc", "instagram.com/brand.name",
                    "https://www.tiktok.com/@brand.name?lang=en", "tiktok.com/brand.name"):
            self.assertEqual(clean_handle(raw).lower(), "brand.name")

    def test_period_end_in_old_and_new_api_shapes(self):
        self.assertEqual(billing.period_end({"current_period_end": PERIOD_END}).timestamp(), PERIOD_END)
        self.assertEqual(billing.period_end(stripe_sub()).timestamp(), PERIOD_END)
        self.assertEqual(billing.invoice_subscription({"subscription": "sub_1"}), "sub_1")
        self.assertEqual(billing.invoice_subscription({"parent": {"subscription_details": {"subscription": "sub_2"}}}), "sub_2")


class PageTests(TestCase):
    def test_every_page_renders_with_packages_and_links_back_to_the_hub(self):
        for route, code, page, platform in routes():
            with self.subTest(route=route):
                r = self.client.get("/" + route)
                self.assertEqual(r.status_code, 200)
                html = r.content.decode()
                self.assertIn('name="plan"', html)
                self.assertNotRegex(html, r"\bSEO\b")
                if page != "main":
                    self.assertIn(f'href="{page_path(code, "main", platform)}"', html)

    def test_main_page_links_to_every_page(self):
        for platform in PLATFORMS:
            html = self.client.get(page_path("en", "main", platform)).content.decode()
            for page in PAGES[1:]:
                self.assertIn(f'href="{page_path("en", page, platform)}"', html)

    def test_creators_hub_renders_and_links_both_platforms(self):
        from .content import CREATOR_PAGES, creator_path, creator_routes
        self.assertEqual(len(creator_routes()), len(CREATORS) * len(CREATOR_PAGES))
        html = self.client.get(creator_path("en", "main")).content.decode()
        for platform in PLATFORMS:
            self.assertIn(f'href="{page_path("en", "main", platform)}#start"', html)
            self.assertIn(f'href="{page_path("en", "agency", platform)}"', html)
        self.assertIn(f'href="{creator_path("en", "main")}"', self.client.get(page_path("en", "main")).content.decode())

    def test_sitemap_index_and_follower_sections(self):
        index = self.client.get("/sitemap.xml").content.decode()
        for section in ("instagram-followers", "tiktok-followers", "creators"):
            self.assertIn(f"/sitemaps/{section}.xml</loc>", index)
        body = self.client.get("/sitemaps/tiktok-followers.xml").content.decode()
        self.assertEqual(body.count("<url>"), len(CODES) * len(PAGES))
        self.assertIn(page_path("tr", "pack_3k", "tiktok"), body)
        self.assertIn(page_path("de", "views_reels", "tiktok"), body)
        self.assertIn('hreflang="x-default"', body)
        self.assertFalse(any("instagram" in loc for loc in re.findall(r"<loc>([^<]+)</loc>", body)))
        self.assertIn("Disallow: /account/", self.client.get("/robots.txt").content.decode())

    def test_hero_shows_every_package_price(self):
        for page in ("guide_buy", "likes", "comments_custom"):
            html = self.client.get(page_path("de", page, "tiktok")).content.decode()
            for amount in ("$79.99", "$149.99", "$279.99"):
                self.assertIn(amount, html.split('id="start"')[0])

    def test_pages_preselect_a_package(self):
        self.assertRegex(self.client.get(page_path("en", "pack_10k")).content.decode(), r'value="pro"[^>]*checked')
        self.assertRegex(self.client.get(page_path("en", "pack_1k")).content.decode(), r'value="starter"[^>]*checked')
        self.assertRegex(self.client.get(page_path("en", "likes")).content.decode(), r'value="rising"[^>]*checked')

    def test_service_pages_have_their_own_paths(self):
        self.assertEqual(page_path("en", "likes_monthly"), "/en/monthly-instagram-likes/")
        self.assertEqual(page_path("tr", "views_reels"), "/" + CONTENT["instagram"]["tr"]["subs"]["views_reels"].lstrip("/"))
        self.assertEqual(self.client.get("/en/instagram-reels-views/").status_code, 200)


class FreshCache:
    """The IP rate limit lives in the cache; every test starts with a clean one."""

    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        super().setUp()


def order_data(**extra):
    data = {"lang": "en", "page": "main", "platform": "instagram", "plan": "rising", "handle": "@My.Brand",
            "location": "Berlin, Germany", "email": "Buyer@Example.com", "password": "s3cret-pass", "consent": "on"}
    data.update(extra)
    return data


@override_settings(**STRIPE_OFF)
class RequestModeTests(FreshCache, TestCase):
    def test_order_creates_account_and_request(self):
        r = self.client.post(reverse("growth:order"), order_data())
        sub = AgencySubscription.objects.get()
        self.assertRedirects(r, f"{reverse('growth:success')}?lang=en&platform=instagram&sub={sub.pk}", fetch_redirect_response=False)
        self.assertEqual((sub.status, sub.handle, sub.plan, str(sub.amount)), ("requested", "my.brand", "rising", "149.99"))
        user = get_user_model().objects.get(username="buyer@example.com")
        self.assertEqual(sub.user, user)
        self.assertTrue(Customer.objects.filter(user=user, lang="en").exists())
        self.assertTrue(sub.notified)
        subjects = [m.subject for m in mail.outbox]
        self.assertIn("We received your request: Rising Influencer for @my.brand on Instagram", subjects)
        page = self.client.get(r["Location"]).content.decode()
        self.assertIn("lead-event", page)
        self.assertIn("signup-event", page)
        self.assertIn("Rising Influencer", page)

    def test_existing_email_needs_the_right_password(self):
        get_user_model().objects.create_user("buyer@example.com", "buyer@example.com", "the-real-one")
        r = self.client.post(reverse("growth:order"), order_data())
        self.assertEqual(r.status_code, 400)
        self.assertFalse(AgencySubscription.objects.exists())
        r = self.client.post(reverse("growth:order"), order_data(password="the-real-one", platform="tiktok", plan="starter"))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(AgencySubscription.objects.get().platform, "tiktok")

    def test_signed_in_order_needs_no_email_or_password(self):
        user = get_user_model().objects.create_user("me@example.com", "me@example.com", "pass-word-1")
        self.client.force_login(user)
        data = order_data()
        del data["email"], data["password"]
        self.assertEqual(self.client.post(reverse("growth:order"), data).status_code, 302)
        self.assertEqual(AgencySubscription.objects.get().email, "me@example.com")

    def test_invalid_plan_and_short_password(self):
        r = self.client.post(reverse("growth:order"), order_data(plan="mega", password="short"))
        self.assertEqual(r.status_code, 400)
        self.assertFalse(get_user_model().objects.exists())

    def test_honeypot(self):
        self.client.post(reverse("growth:order"), order_data(fax="bot"))
        self.assertFalse(AgencySubscription.objects.exists())


@override_settings(**STRIPE_ON)
class CheckoutTests(FreshCache, TestCase):
    session = SimpleNamespace(id="cs_test_1", url="https://checkout.stripe.com/c/pay/cs_test_1")

    def signed_in(self):
        user = get_user_model().objects.create_user("me@example.com", "me@example.com", "pass-word-1")
        Customer.objects.create(user=user, email_verified=True)
        self.client.force_login(user)
        return user

    def test_unverified_email_gets_a_link_that_goes_straight_to_payment(self):
        r = self.client.post(reverse("growth:order"), order_data(plan="pro"))
        self.assertEqual(r["Location"], f"{reverse('growth:account')}?lang=en&verify=sent")
        sub = AgencySubscription.objects.get()
        self.assertEqual((sub.status, sub.plan), ("pending", "pro"))
        link = re.search(r"https?://[^/\s]+(/account/verify/\S+/)", mail.outbox[-1].body).group(1)
        self.client.logout()
        with mock.patch("apps.growth.billing.create_checkout", return_value=self.session) as create:
            r = self.client.get(link)
        self.assertEqual((r.status_code, r["Location"]), (303, self.session.url))
        self.assertEqual(create.call_args.args[0].pk, sub.pk)
        self.assertTrue(Customer.objects.get().email_verified)
        sub.refresh_from_db()
        self.assertEqual(sub.stripe_checkout_session_id, "cs_test_1")
        self.assertIsNotNone(sub.terms_accepted_at)
        self.assertEqual(sub.terms_version, TERMS_VERSION)
        self.assertIn("cancel", create.call_args.kwargs["note"])

    def test_verified_customer_goes_straight_to_stripe_and_retries_reuse_the_unpaid_one(self):
        self.signed_in()
        data = order_data(platform="tiktok", plan="starter")
        del data["email"], data["password"]
        with mock.patch("apps.growth.billing.create_checkout", return_value=self.session) as create:
            r = self.client.post(reverse("growth:order"), data)
            self.client.post(reverse("growth:order"), {**data, "plan": "pro", "location": "Paris"})
        self.assertEqual((r.status_code, r["Location"]), (303, self.session.url))
        sub = AgencySubscription.objects.get()
        self.assertEqual((sub.platform, sub.plan, str(sub.amount), sub.location), ("tiktok", "pro", "279.99", "Paris"))
        self.assertEqual(create.call_count, 2)
        self.assertFalse([m for m in mail.outbox if "owner@example.com" in m.to])  # unpaid: no team email

    def test_stripe_down_shows_the_form_again(self):
        self.signed_in()
        data = order_data()
        del data["email"], data["password"]
        with mock.patch("apps.growth.billing.create_checkout", side_effect=stripe.APIConnectionError("down")):
            r = self.client.post(reverse("growth:order"), data)
        self.assertEqual(r.status_code, 502)

    def test_success_page_activates_once(self):
        user = self.signed_in()
        sub = AgencySubscription.objects.create(user=user, email=user.email, handle="brand", location="Rome", plan="starter",
                                                amount="79.99", stripe_checkout_session_id="cs_ok")
        session = SimpleNamespace(id="cs_ok", status="complete", payment_status="paid", subscription="sub_1")
        url = f"{reverse('growth:success')}?lang=en&platform=instagram&sub={sub.pk}&session_id=cs_ok"
        with mock.patch("apps.growth.billing.retrieve_checkout", return_value=session), \
             mock.patch("apps.growth.billing.retrieve_subscription", return_value=stripe_sub()):
            first = self.client.get(url).content.decode()
            second = self.client.get(url).content.decode()
        self.assertIn("purchase-event", first)
        self.assertNotIn("purchase-event", second)
        sub.refresh_from_db()
        self.assertEqual((sub.status, sub.stripe_subscription_id, sub.stripe_customer_id), ("active", "sub_1", "cus_1"))
        self.assertEqual(int(sub.current_period_end.timestamp()), PERIOD_END)
        subjects = [m.subject for m in mail.outbox]
        self.assertEqual(subjects.count("Your campaign has started: Starter Creator for @brand on Instagram"), 1)
        self.assertEqual(sum("(ödendi)" in s for s in subjects), 1)

    def test_billing_portal(self):
        user = self.signed_in()
        AgencySubscription.objects.create(user=user, email=user.email, handle="brand", location="Rome", amount="79.99",
                                          status="active", stripe_customer_id="cus_1")
        with mock.patch("apps.growth.billing.portal_url", return_value="https://billing.stripe.com/p/x") as portal:
            r = self.client.post(reverse("growth:billing"), {"lang": "en"})
        self.assertEqual((r.status_code, r["Location"]), (303, "https://billing.stripe.com/p/x"))
        self.assertEqual(portal.call_args.args[0], "cus_1")
        self.assertContains(self.client.get(reverse("growth:account") + "?lang=en"), "Manage billing or cancel")


@override_settings(**STRIPE_ON)
class StripePriceTests(TestCase):
    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.sub = AgencySubscription.objects.create(email="a@example.com", handle="brand", location="Rome", platform="tiktok",
                                                     plan="pro", amount="279.99")

    def checkout_params(self, prices):
        client = mock.Mock()
        client.v1.prices.list.return_value = SimpleNamespace(data=prices)
        client.v1.checkout.sessions.create.return_value = SimpleNamespace(id="cs", url="u")
        with mock.patch("apps.growth.billing._client", return_value=client):
            billing.create_checkout(self.sub, "https://s/ok", "https://s/cancel")
        self.assertEqual(client.v1.prices.list.call_args.kwargs["params"]["lookup_keys"], ["sterr_tiktok_pro_monthly_usd"])
        return client.v1.checkout.sessions.create.call_args.kwargs["params"]

    def test_uses_the_monthly_price_from_setup_stripe(self):
        params = self.checkout_params([SimpleNamespace(id="price_pro", unit_amount=27999)])
        self.assertEqual(params["payment_method_options"], {"card": {"request_three_d_secure": "any"}})
        self.assertEqual(params["mode"], "subscription")
        self.assertEqual(params["line_items"], [{"quantity": 1, "price": "price_pro"}])
        self.assertEqual(params["subscription_data"]["metadata"]["subscription_id"], str(self.sub.pk))

    def test_portal_configuration_from_real_stripe_objects(self):
        confs = [stripe.StripeObject.construct_from({"id": "bpc_other", "metadata": {}}, "sk"),
                 stripe.StripeObject.construct_from({"id": "bpc_ours", "metadata": {"app": billing.PORTAL_TAG}}, "sk")]
        client = mock.Mock()
        client.v1.billing_portal.configurations.list.return_value = SimpleNamespace(data=confs)
        with mock.patch("apps.growth.billing._client", return_value=client):
            self.assertEqual(billing.portal_configuration(), "bpc_ours")

    def test_retrieve_subscription_with_decimal_fields(self):
        # A real Stripe subscription: price.unit_amount_decimal comes back as a Decimal.
        sub = stripe.Subscription.construct_from({"id": "sub_1", "object": "subscription", "status": "active", "items": {
            "object": "list", "data": [{"object": "subscription_item", "current_period_end": 1700000000,
                                        "price": {"object": "price", "id": "p", "unit_amount_decimal": "7999"}}]}}, "sk")
        client = mock.Mock()
        client.v1.subscriptions.retrieve.return_value = sub
        with mock.patch("apps.growth.billing._client", return_value=client):
            data = billing.retrieve_subscription("sub_1")
        self.assertEqual(data["items"]["data"][0]["price"]["unit_amount_decimal"], "7999")
        self.assertIsNotNone(billing.period_end(data))

    def test_falls_back_to_inline_monthly_price_when_missing_or_outdated(self):
        params = self.checkout_params([SimpleNamespace(id="price_old", unit_amount=9900)])
        data = params["line_items"][0]["price_data"]
        self.assertEqual((data["unit_amount"], data["recurring"]), (27999, {"interval": "month"}))


def signed(payload):
    body = json.dumps(payload)
    return body, stripe.WebhookSignature.generate_signature_header(body, WEBHOOK_SECRET)


@override_settings(**STRIPE_ON)
class WebhookTests(TestCase):
    def setUp(self):
        self.sub = AgencySubscription.objects.create(email="a@example.com", handle="brand", location="Berlin", lang="de",
                                                     plan="rising", amount="149.99", stripe_checkout_session_id="cs_1")

    def send(self, event_id, event_type, obj, stripe_obj=None):
        body, header = signed({"id": event_id, "type": event_type, "data": {"object": obj}})
        with mock.patch("apps.growth.billing.retrieve_subscription", return_value=stripe_obj or stripe_sub()):
            return self.client.post(reverse("growth:webhook"), body, content_type="application/json", HTTP_STRIPE_SIGNATURE=header)

    def checkout(self, event_id="evt_1", **extra):
        obj = {"id": "cs_1", "mode": "subscription", "payment_status": "paid", "client_reference_id": str(self.sub.pk),
               "subscription": "sub_1", **extra}
        return self.send(event_id, "checkout.session.completed", obj)

    def team(self, words):
        return [m for m in mail.outbox if words in m.subject]

    def test_bad_signature_rejected(self):
        r = self.client.post(reverse("growth:webhook"), "{}", content_type="application/json", HTTP_STRIPE_SIGNATURE="t=1,v1=nope")
        self.assertEqual(r.status_code, 400)

    def test_paid_checkout_activates_and_emails_once(self):
        self.assertEqual(self.checkout().status_code, 200)
        self.assertEqual(self.checkout().content, b"duplicate")
        self.send("evt_2", "invoice.paid", {"id": "in_1", "subscription": "sub_1", "billing_reason": "subscription_create"})
        self.sub.refresh_from_db()
        self.assertEqual((self.sub.status, self.sub.stripe_subscription_id), ("active", "sub_1"))
        self.assertIsNotNone(self.sub.started_at)
        self.assertEqual(sum(m.subject.startswith("Your campaign has started: Rising Influencer") for m in mail.outbox), 1)
        team = self.team("paketi (ödendi)")
        self.assertEqual(len(team), 1)
        self.assertEqual(team[0].to, ["owner@example.com", "ekinsipahi8@gmail.com"])
        self.assertIn("Rising Influencer", team[0].body)
        self.assertEqual(StripeEvent.objects.count(), 2)

    def test_another_sites_checkout_is_skipped(self):
        # Other sites share the Stripe account: a numeric reference that happens to match our id is not ours.
        r = self.checkout(id="cs_other_site", client_reference_id=str(self.sub.pk), metadata={"subscription_id": str(self.sub.pk)})
        self.assertEqual(r.status_code, 200)
        self.send("evt_9", "customer.subscription.updated", stripe_sub(sub_id="sub_other", metadata={"subscription_id": str(self.sub.pk)}))
        self.sub.refresh_from_db()
        self.assertEqual((self.sub.status, self.sub.stripe_subscription_id), ("pending", ""))
        self.assertFalse(mail.outbox)

    def test_failed_payment_and_its_recovery_are_told_and_linksterr_is_asked_at_once(self):
        with mock.patch("apps.growth.linksterr.ping_soon") as ping:
            with self.captureOnCommitCallbacks(execute=True):
                self.checkout()
            self.assertEqual(ping.call_count, 1)  # first payment: Linksterr opens the campaign now
            with self.captureOnCommitCallbacks(execute=True):
                self.send("evt_f", "invoice.payment_failed", {"id": "in_f", "subscription": "sub_1"}, stripe_sub("past_due"))
            with self.captureOnCommitCallbacks(execute=True):
                self.send("evt_r", "invoice.paid", {"id": "in_r", "subscription": "sub_1", "billing_reason": "subscription_cycle"})
            self.assertEqual(ping.call_count, 3)
            with self.captureOnCommitCallbacks(execute=True):
                self.send("evt_same", "customer.subscription.updated", stripe_sub())
            self.assertEqual(ping.call_count, 3)  # nothing changed: no ping
        self.assertEqual(len(self.team("ödemesi alınamadı")), 1)
        self.assertEqual(len(self.team("ödemesi alındı")), 1)
        self.assertEqual(sum(m.subject == "Payment received: your campaign is running again" for m in mail.outbox), 1)

    def test_unpaid_checkout_does_nothing(self):
        self.checkout(payment_status="unpaid")
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.status, "pending")
        self.assertFalse(mail.outbox)

    def test_renewal_failed_payment_cancel(self):
        self.checkout()
        renewal = {"id": "in_2", "parent": {"subscription_details": {"subscription": "sub_1"}},
                   "billing_reason": "subscription_cycle", "amount_paid": 14999}
        self.send("evt_3", "invoice.paid", renewal)
        self.assertEqual(len(self.team("yenilendi (ödendi)")), 1)
        self.send("evt_4", "invoice.payment_failed", {"id": "in_3", "subscription": "sub_1"}, stripe_sub("past_due"))
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.status, "past_due")
        self.send("evt_5", "customer.subscription.updated", stripe_sub(cancel_at_period_end=True))
        self.sub.refresh_from_db()
        self.assertEqual((self.sub.status, self.sub.cancel_at_period_end), ("active", True))
        self.send("evt_6", "customer.subscription.deleted", stripe_sub("canceled"))
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.status, "canceled")
        self.assertIsNotNone(self.sub.canceled_at)
        self.assertEqual(len(self.team("iptal edildi")), 1)
        self.assertEqual(sum(m.subject.startswith("Your campaign has started") for m in mail.outbox), 1)  # the welcome went out once
        self.assertEqual(len(self.team("ödemesi alınamadı")), 1)  # past_due: the campaign pauses
        self.assertEqual(sum(m.subject.startswith("We couldn't take your payment") for m in mail.outbox), 1)


@override_settings(**STRIPE_ON)
class CancelTests(TestCase):
    """Cancel from the dashboard or the reminder's link, take it back, the 3-day reminder."""

    def setUp(self):
        self.user = get_user_model().objects.create_user("me@example.com", "me@example.com", "pass-word-1")
        self.sub = AgencySubscription.objects.create(
            user=self.user, email="me@example.com", handle="brand", location="Berlin", lang="en", plan="starter",
            amount="79.99", status="active", started_at=timezone.now(), stripe_subscription_id="sub_1",
            stripe_customer_id="cus_1", current_period_end=timezone.now() + timedelta(days=2))
        self.url = reverse("growth:cancel", args=[self.sub.pk])

    def cancel(self, path, data):
        with mock.patch("apps.growth.billing.set_cancel", return_value=stripe_sub(cancel_at_period_end=True)) as set_cancel:
            r = self.client.post(path, data)
        set_cancel.assert_called_once_with("sub_1", True)
        self.sub.refresh_from_db()
        return r

    def team(self, words):
        return [m for m in mail.outbox if words in m.subject]

    def test_cancel_from_the_dashboard(self):
        self.client.force_login(self.user)
        r = self.client.get(reverse("growth:account") + "?lang=en")
        self.assertContains(r, self.url)
        self.assertContains(self.client.get(self.url + "?lang=en"), "Yes, cancel")
        r = self.cancel(self.url, {"lang": "en"})
        self.assertContains(r, "Your subscription is canceled")
        self.assertEqual((self.sub.cancel_at_period_end, self.sub.cancel_source, self.sub.status), (True, "account", "active"))
        self.assertIsNotNone(self.sub.cancel_requested_at)
        team = self.team("iptal talebi")
        self.assertEqual(len(team), 1)
        self.assertIn("hesap panelinden", team[0].body)
        self.assertEqual(len([m for m in mail.outbox if m.subject.startswith("Cancellation confirmed")]), 1)
        # Stripe's own webhook for the same change sends nothing more.
        body, header = signed({"id": "evt_c", "type": "customer.subscription.updated", "data": {"object": stripe_sub(cancel_at_period_end=True)}})
        self.client.post(reverse("growth:webhook"), body, content_type="application/json", HTTP_STRIPE_SIGNATURE=header)
        self.assertEqual(len(self.team("iptal talebi")), 1)
        self.assertContains(self.client.get(reverse("growth:account") + "?lang=en"), reverse("growth:resume", args=[self.sub.pk]))

    def test_cancel_needs_the_owner(self):
        self.assertEqual(self.client.get(self.url).status_code, 302)  # signed out: to the login page
        other = get_user_model().objects.create_user("x@example.com", "x@example.com", "pass-word-1")
        self.client.force_login(other)
        self.assertContains(self.client.get(self.url + "?lang=en"), "This link no longer works")

    def test_reminder_once_per_period(self):
        body, header = signed({"id": "evt_u", "type": "invoice.upcoming", "data": {"object": {
            "parent": {"subscription_details": {"subscription": "sub_1"}}, "amount_due": 7999}}})
        for _ in range(2):
            self.client.post(reverse("growth:webhook"), body, content_type="application/json", HTTP_STRIPE_SIGNATURE=header)
        call_command("send_renewal_reminders", stdout=StringIO())
        reminders = [m for m in mail.outbox if m.subject.startswith("Your Starter Creator package renews in 2 days")]
        self.assertEqual(len(reminders), 1)
        text = reminders[0].body
        self.assertNotIn("cancel", text.split("--")[0].lower())  # only the small note at the very end mentions it
        self.assertIn("manage or cancel your subscription any time in your account", text.split("--")[1])
        self.assertIn("/account/?lang=en", text)

    def test_reminder_command_skips_far_or_canceling(self):
        far = AgencySubscription.objects.create(email="f@example.com", handle="far", location="x", plan="rising", amount="149.99",
                                                status="active", stripe_subscription_id="sub_2",
                                                current_period_end=timezone.now() + timedelta(days=20))
        AgencySubscription.objects.filter(pk=self.sub.pk).update(cancel_at_period_end=True)
        call_command("send_renewal_reminders", stdout=StringIO())
        self.assertFalse(mail.outbox)
        far.refresh_from_db()
        self.assertIsNone(far.reminded_for)

    def test_resume(self):
        AgencySubscription.objects.filter(pk=self.sub.pk).update(cancel_at_period_end=True, cancel_source="account",
                                                                 cancel_requested_at=timezone.now())
        self.client.force_login(self.user)
        with mock.patch("apps.growth.billing.set_cancel", return_value=stripe_sub()) as set_cancel:
            r = self.client.post(reverse("growth:resume", args=[self.sub.pk]), {"lang": "en"})
        set_cancel.assert_called_once_with("sub_1", False)
        self.assertEqual(r["Location"], f"{reverse('growth:account')}?lang=en&resumed=1")
        self.sub.refresh_from_db()
        self.assertEqual((self.sub.cancel_at_period_end, self.sub.cancel_source, self.sub.cancel_requested_at), (False, "", None))
        self.assertEqual(len(self.team("iptali geri alındı")), 1)


@override_settings(**STRIPE_ON)
class DisputeTests(FreshCache, TestCase):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user("me@example.com", "me@example.com", "pass-word-1")
        self.sub = AgencySubscription.objects.create(
            user=self.user, email="me@example.com", handle="brand", location="Berlin", plan="rising", amount="149.99",
            status="active", started_at=timezone.now() - timedelta(days=12), stripe_subscription_id="sub_1",
            stripe_customer_id="cus_1", current_period_end=timezone.now() + timedelta(days=18), ip="203.0.113.9",
            terms_accepted_at=timezone.now() - timedelta(days=12), terms_version=TERMS_VERSION)
        SubscriptionStat.objects.create(subscription=self.sub, date=timezone.now().date(), new_followers=140, impressions=1200,
                                        visits=310, confirms=95, countries={"DE": {"impressions": 900, "visits": 200, "confirms": 70}})

    def dispute(self, event_id, status="needs_response", traced=("sub_1", "cus_1")):
        obj = {"id": "dp_1", "object": "dispute", "amount": 14999, "reason": "product_not_received", "status": status,
               "charge": "ch_1", "payment_intent": "pi_1", "evidence_details": {"due_by": 1767225600}}
        body, header = signed({"id": event_id, "type": f"charge.dispute.{'created' if status == 'needs_response' else 'closed'}",
                               "data": {"object": obj}})
        with mock.patch("apps.growth.billing.dispute_subscription", return_value=traced), \
                mock.patch("apps.growth.billing.stage_evidence") as stage:
            self.client.post(reverse("growth:webhook"), body, content_type="application/json", HTTP_STRIPE_SIGNATURE=header)
        return stage

    def test_dispute_stages_evidence_and_tells_the_team(self):
        self.client.force_login(self.user)  # a sign-in and a dashboard visit are on record
        self.client.get(reverse("growth:account") + "?lang=en")
        stage = self.dispute("evt_d1")
        dispute_id, evidence = stage.call_args.args
        self.assertEqual(dispute_id, "dp_1")
        self.assertIn("@brand", evidence["product_description"])
        self.assertIn("203.0.113.9", evidence["cancellation_policy_disclosure"])
        self.assertIn("follow step shown 1,200 times", evidence["uncategorized_text"])
        self.assertIn("DE 900", evidence["uncategorized_text"])
        self.assertIn("opened the growth dashboard", evidence["access_activity_log"])
        self.assertIn("never canceled", evidence["cancellation_rebuttal"])
        self.assertTrue(all(len(v) <= 20000 for v in evidence.values()))
        d = Dispute.objects.get()
        self.assertEqual((d.subscription_id, str(d.amount), d.evidence_staged), (self.sub.pk, "149.99", True))
        team = [m for m in mail.outbox if "itiraz (dispute) açıldı" in m.subject]
        self.assertEqual(len(team), 1)
        self.assertIn("dashboard.stripe.com/disputes/dp_1", team[0].body)
        self.dispute("evt_d2", status="won")
        self.assertEqual(Dispute.objects.get().status, "won")
        self.assertIn("KAZANILDI", [m for m in mail.outbox if "itirazı sonuçlandı" in m.subject][0].body)

    def test_another_sites_dispute_is_skipped(self):
        stage = self.dispute("evt_d3", traced=("sub_x", "cus_x"))
        stage.assert_not_called()
        self.assertFalse(Dispute.objects.exists())
        self.assertFalse(mail.outbox)

    def test_evidence_page_in_admin(self):
        admin = get_user_model().objects.create_superuser("boss", "boss@example.com", "pass-word-1")
        self.client.force_login(admin)
        r = self.client.get(reverse("admin:growth_agencysubscription_evidence", args=[self.sub.pk]))
        self.assertContains(r, "service record for @brand")
        self.assertContains(r, "follow step shown 1,200 times")
        self.assertFalse(AccountActivity.objects.filter(user=admin).exists())  # staff sign-ins aren't customer activity

    def test_activity_log_once_an_hour(self):
        self.client.post(reverse("growth:login") + "?lang=en", {"email": "me@example.com", "password": "pass-word-1"})
        for _ in range(3):
            self.client.get(reverse("growth:account") + "?lang=en")
        self.assertEqual(sorted(AccountActivity.objects.values_list("kind", flat=True)), ["dashboard", "login"])


@override_settings(GROWTH_API_TOKEN="tok_test", **MAIL)
class StatsApiTests(TestCase):
    def setUp(self):
        self.sub = AgencySubscription.objects.create(email="a@example.com", handle="brand", location="Oslo", amount="79.99",
                                                     status="active", started_at=timezone.now() - timedelta(days=5),
                                                     current_period_end=timezone.now() + timedelta(days=25))

    def post(self, payload, token="tok_test"):
        return self.client.post(reverse("growth:api_stats"), json.dumps(payload), content_type="application/json",
                                HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_token_required(self):
        self.assertEqual(self.post({"subscription_id": self.sub.pk}, token="nope").status_code, 401)
        self.assertEqual(self.client.get(reverse("growth:api_subscriptions")).status_code, 401)

    def test_lists_active_subscriptions(self):
        r = self.client.get(reverse("growth:api_subscriptions"), HTTP_AUTHORIZATION="Bearer tok_test")
        self.assertEqual([s["handle"] for s in r.json()["subscriptions"]], ["brand"])

    @override_settings(LINKSTERR_AGENCY_TOKEN="agency-test-token")
    def test_linksterr_token_reads_subscriptions_but_cannot_write(self):
        AgencySubscription.objects.filter(pk=self.sub.pk).update(cancel_at_period_end=True, plan="pro", amount="279.99")
        r = self.client.get(reverse("growth:api_subscriptions") + "?status=active,past_due,canceled",
                            HTTP_AUTHORIZATION="Bearer agency-test-token")
        item = r.json()["subscriptions"][0]
        self.assertEqual((item["plan"], item["amount"], item["cancel_at_period_end"], item["canceled_at"]), ("pro", 279.99, True, None))
        self.assertIsNotNone(item["current_period_end"])
        self.assertEqual(self.post({"subscription_id": self.sub.pk, "new_followers": 5}, token="agency-test-token").status_code, 401)
        self.assertFalse(SubscriptionStat.objects.exists())

    def test_daily_stats(self):
        today = timezone.now().date()
        r = self.post({"updates": [
            {"subscription_id": self.sub.pk, "date": str(today - timedelta(days=2)), "followers": 1200, "likes": 40, "comments": 2},
            {"subscription_id": self.sub.pk, "date": str(today), "followers": 1650, "likes": 300, "comments": 9},
            {"subscription_id": 999999, "likes": 1},
            {"subscription_id": self.sub.pk, "likes": -1},
        ]})
        self.assertEqual(r.status_code, 207)
        self.sub.refresh_from_db()
        self.assertEqual((self.sub.start_followers, self.sub.current_followers, self.sub.gained), (1200, 1650, 450))
        self.post({"subscription_id": self.sub.pk, "date": str(today), "followers": 1700, "likes": 310, "comments": 9})
        self.assertEqual(SubscriptionStat.objects.count(), 2)
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.gained, 500)

    def test_delivery_evidence(self):
        r = self.post({"subscription_id": self.sub.pk, "date": "2026-11-04", "new_followers": 120, "impressions": 1500,
                       "visits": 300, "confirms": 110, "countries": {"no": {"impressions": 1500, "visits": 300, "confirms": 110}}})
        self.assertEqual(r.status_code, 200)
        stat = SubscriptionStat.objects.get()
        self.assertEqual((stat.impressions, stat.visits, stat.confirms), (1500, 300, 110))
        self.assertEqual(stat.countries, {"NO": {"impressions": 1500, "visits": 300, "confirms": 110}})
        r = self.post({"subscription_id": self.sub.pk, "countries": {"Norway": {"impressions": 1}}})
        self.assertEqual(r.status_code, 207)

    def test_our_count_of_new_followers_wins_over_the_follower_count(self):
        today = timezone.now().date()
        self.post({"updates": [
            {"subscription_id": self.sub.pk, "date": str(today - timedelta(days=1)), "followers": 1000, "new_followers": 80},
            {"subscription_id": self.sub.pk, "date": str(today), "followers": 1050, "new_followers": 120},
            {"subscription_id": self.sub.pk, "date": str(today - timedelta(days=2)), "new_followers": 40},
        ]})
        self.sub.refresh_from_db()
        daily = self.sub.daily()
        self.assertEqual([d["followers"] for d in daily], [40, 80, 120])
        self.assertEqual([(d["likes"], d["comments"]) for d in daily], [(None, None)] * 3)  # nothing invented
        self.assertEqual(self.sub.gained, 240)

    def test_dashboard_shows_the_numbers(self):
        user = get_user_model().objects.create_user("a@example.com", "a@example.com", "pass-word-1")
        self.sub.user = user
        self.sub.save()
        today = timezone.now().date()
        self.post({"updates": [{"subscription_id": self.sub.pk, "date": str(today - timedelta(days=3)), "followers": 4200, "likes": 500},
                               {"subscription_id": self.sub.pk, "date": str(today), "followers": 5400, "likes": 1500, "comments": 120}]})
        self.client.force_login(user)
        html = self.client.get(reverse("growth:account") + "?lang=en").content.decode()
        self.assertIn("Today", html)
        self.assertIn("+1,200", html)  # new followers today (count went 4,200 -> 5,400)
        self.assertNotIn("<span>Likes</span>", html)  # never shown: Linksterr does not measure them
        self.assertIn("<rect", html)  # new followers per day
        self.assertIn("Day by day", html)
        self.assertIn("Renews on", html)


def linksterr_account(account="instagram:brand", days=(), readings=()):
    return {"account": account, "platform": account.split(":")[0], "handle": account.split(":")[1],
            "campaigns": [{"id": 2, "status": "active", "live": True, "period_start": None, "period_end": None,
                           "rate": 0.057, "own_weight": 0.1}] if days else [],
            "readings": list(readings), "days": list(days)}


def linksterr_day(date, new=40, visits=420, impressions=700, confirms=380, countries=None):
    return {"date": str(date), "live": True, "new_followers": new, "visits": visits, "impressions": impressions,
            "confirms": confirms, "countries": countries if countries is not None else {"DE": {"impressions": 500, "visits": 300, "confirms": 250}}}


@override_settings(LINKSTERR_AGENCY_TOKEN="agency-test-token", LINKSTERR_API_URL="https://linksterr.example", **MAIL)
class LinksterrTests(FreshCache, TestCase):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user("me@example.com", "me@example.com", "pass-word-1")
        self.today = timezone.now().date()
        self.sub = AgencySubscription.objects.create(
            user=self.user, email="me@example.com", handle="Brand", location="Berlin", plan="starter", amount="79.99",
            status="active", started_at=timezone.now() - timedelta(days=5), stripe_subscription_id="sub_1",
            current_period_end=timezone.now() + timedelta(days=25))

    def respond(self, *accounts, status=200):
        response = mock.Mock(status_code=status)
        response.json.return_value = {"day": "UTC", "accounts": list(accounts)}
        response.raise_for_status.side_effect = None if status == 200 else requests.HTTPError(str(status))
        return mock.patch("apps.growth.linksterr.requests.get", return_value=response)

    def test_sync_stores_the_days_of_the_package(self):
        start = self.today - timedelta(days=5)
        days = [linksterr_day(start - timedelta(days=1), new=999),  # before the package: not ours
                linksterr_day(start, new=30, countries={"DE": {"impressions": 1, "visits": 2, "confirms": 3}, "": {"visits": 9}}),
                linksterr_day(self.today, new=41)]
        readings = [{"date": str(start - timedelta(days=1)), "followers": 1000}, {"date": str(self.today), "followers": 1071}]
        with self.respond(linksterr_account(days=days, readings=readings)) as get:
            self.assertEqual(linksterr.sync([self.sub]), 1)
        args, kwargs = get.call_args
        self.assertEqual(args[0], "https://linksterr.example/user-api/v1/agency/accounts/")
        self.assertEqual(kwargs["headers"], {"Authorization": "Bearer agency-test-token"})
        self.assertIn(("account", "instagram:brand"), kwargs["params"])
        self.assertIn(("since", str(start)), kwargs["params"])
        self.assertIn(("until", str(self.today)), kwargs["params"])
        rows = {s.date: s for s in SubscriptionStat.objects.filter(subscription=self.sub)}
        self.assertEqual(sorted(rows), [start, self.today])
        self.assertEqual((rows[start].new_followers, rows[start].visits, rows[start].confirms), (30, 420, 380))
        self.assertEqual(rows[start].countries, {"DE": {"impressions": 1, "visits": 2, "confirms": 3}})
        self.assertEqual(rows[self.today].followers, 1071)
        self.assertIsNone(rows[self.today].likes)  # Linksterr does not measure likes
        self.sub.refresh_from_db()
        self.assertEqual((self.sub.start_followers, self.sub.current_followers), (1000, 1071))
        self.assertIsNotNone(self.sub.stats_at)

    def test_settled_days_are_not_rewritten(self):
        old, recent = self.today - timedelta(days=4), self.today - timedelta(days=1)
        with self.respond(linksterr_account(days=[linksterr_day(old, new=30), linksterr_day(recent, new=30)])):
            linksterr.sync([self.sub])
        with self.respond(linksterr_account(days=[linksterr_day(old, new=55), linksterr_day(recent, new=55)])):
            linksterr.sync([self.sub], force=True)
        rows = dict(SubscriptionStat.objects.filter(subscription=self.sub).values_list("date", "new_followers"))
        self.assertEqual(rows, {old: 30, recent: 55})

    def test_fetches_at_most_every_ten_minutes_and_survives_outages(self):
        with self.respond(linksterr_account()) as get:
            linksterr.sync([self.sub])
            linksterr.sync([self.sub])
            self.assertEqual(get.call_count, 1)
            linksterr.sync([self.sub], force=True)
            self.assertEqual(get.call_count, 2)
        with mock.patch("apps.growth.linksterr.requests.get", side_effect=requests.ConnectionError("down")):
            self.assertEqual(linksterr.sync([self.sub], force=True), 0)
        with self.respond(status=500):
            self.assertEqual(linksterr.sync([self.sub], force=True), 0)

    def test_many_subscriptions_go_in_batches_within_linksterrs_limits(self):
        subs = [self.sub] + [AgencySubscription.objects.create(
            email=f"u{i}@example.com", handle=f"brand{i}", location="x", plan="starter", amount="79.99", status="active",
            started_at=timezone.now() - timedelta(days=500)) for i in range(120)]
        with self.respond(linksterr_account()) as get:
            linksterr.sync(subs)
        self.assertEqual(get.call_count, 2)
        for args, kwargs in get.call_args_list:
            params = kwargs["params"]
            self.assertLessEqual(sum(1 for k, _ in params if k == "account"), 100)
            self.assertIn(("since", str(self.today - timedelta(days=399))), params)

    def test_a_day_fetched_while_running_is_fetched_again_later(self):
        day = self.today - timedelta(days=3)
        with self.respond(linksterr_account(days=[linksterr_day(day, new=15)])):
            linksterr.sync([self.sub])
        SubscriptionStat.objects.filter(date=day).update(synced_at=timezone.now() - timedelta(days=3, hours=12))  # mid-day
        with self.respond(linksterr_account(days=[linksterr_day(day, new=45)])) as get:
            linksterr.sync([self.sub], force=True)
        self.assertEqual(SubscriptionStat.objects.get(date=day).new_followers, 45)
        self.assertIn(("since", str(day)), get.call_args.kwargs["params"])
        with self.respond(linksterr_account(days=[linksterr_day(day, new=99)])):
            linksterr.sync([self.sub], force=True)
        self.assertEqual(SubscriptionStat.objects.get(date=day).new_followers, 45)  # now settled

    def test_two_packages_of_one_account_never_count_a_day_twice(self):
        second = AgencySubscription.objects.create(
            user=self.user, email="me@example.com", handle="brand", location="x", plan="pro", amount="279.99",
            status="active", started_at=timezone.now() - timedelta(days=1))
        days = [linksterr_day(self.today - timedelta(days=n), new=10) for n in range(4)]
        with self.respond(linksterr_account(days=days)):
            linksterr.sync([self.sub, second])
        first_days = set(SubscriptionStat.objects.filter(subscription=self.sub).values_list("date", flat=True))
        second_days = set(SubscriptionStat.objects.filter(subscription=second).values_list("date", flat=True))
        self.assertFalse(first_days & second_days)
        self.assertEqual(len(first_days | second_days), 4)

    def test_a_bad_handle_or_a_failed_batch_does_not_stop_the_rest(self):
        odd = AgencySubscription.objects.create(email="x@example.com", handle="not valid!", location="x", plan="starter",
                                                amount="79.99", status="active", started_at=timezone.now())
        with self.respond(linksterr_account(days=[linksterr_day(self.today)])) as get:
            self.assertEqual(linksterr.sync([self.sub, odd]), 1)
        self.assertNotIn(("account", "instagram:not valid!"), get.call_args.kwargs["params"])

    def test_linksterr_token_sees_only_paid_packages(self):
        AgencySubscription.objects.create(email="p@example.com", handle="unpaid", location="x", plan="starter",
                                          amount="79.99", status="pending")
        AgencySubscription.objects.create(email="o@example.com", handle="oldend", location="x", plan="starter", amount="79.99",
                                          status="canceled", started_at=timezone.now() - timedelta(days=200),
                                          canceled_at=timezone.now() - timedelta(days=120))
        r = self.client.get(reverse("growth:api_subscriptions") + "?status=active,pending,canceled",
                            HTTP_AUTHORIZATION="Bearer agency-test-token")
        self.assertEqual([s["handle"] for s in r.json()["subscriptions"]], ["Brand"])

    @override_settings(LINKSTERR_AGENCY_TOKEN="")
    def test_off_without_a_token(self):
        with mock.patch("apps.growth.linksterr.requests.get") as get:
            self.assertEqual(linksterr.sync([self.sub], force=True), 0)
        get.assert_not_called()

    def test_canceled_package_stops_at_its_last_day(self):
        AgencySubscription.objects.filter(pk=self.sub.pk).update(status="canceled", canceled_at=timezone.now() - timedelta(days=2))
        self.sub.refresh_from_db()
        last = (timezone.now() - timedelta(days=2)).date()
        with self.respond(linksterr_account(days=[linksterr_day(last), linksterr_day(self.today)])):
            linksterr.sync([self.sub])
        self.assertEqual(list(SubscriptionStat.objects.filter(subscription=self.sub).values_list("date", flat=True)), [last])

    def test_dashboard_fetches_and_shows_what_they_gained(self):
        self.client.force_login(self.user)
        with self.respond(linksterr_account(days=[linksterr_day(self.today, new=41, visits=420)])) as get:
            html = self.client.get(reverse("growth:account") + "?lang=en").content.decode()
        get.assert_called_once()
        self.assertIn("+41", html)
        self.assertIn("Profile visits", html)
        self.assertIn("420", html)
        self.assertIn("Visits by country:", html)
        self.assertIn('data-region="DE">DE</span> <b>100%</b>', html)
        self.assertIn("These numbers come from our delivery system", html)
        self.assertNotIn("<span>Likes</span>", html)
        self.assertNotIn(">700<", html)  # impressions stay out of the customer's dashboard

    def test_staff_sees_a_customers_dashboard_read_only(self):
        SubscriptionStat.objects.create(subscription=self.sub, date=self.today, new_followers=41, visits=420)
        path = reverse("growth:view_as", args=[self.user.pk]) + "?lang=en"
        self.assertEqual(self.client.get(path).status_code, 302)  # signed out: to the admin login
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(path).status_code, 302)  # a customer cannot use it
        boss = get_user_model().objects.create_user("boss@example.com", "boss@example.com", "pass-word-1", is_staff=True)
        self.client.force_login(boss)
        self.assertEqual(self.client.get(path).status_code, 403)  # staff without the growth permission
        from django.contrib.auth.models import Permission
        boss.user_permissions.add(Permission.objects.get(codename="view_agencysubscription"))
        boss = get_user_model().objects.get(pk=boss.pk)
        self.client.force_login(boss)
        with self.respond(linksterr_account()):
            r = self.client.get(path)
        html = r.content.decode()
        self.assertEqual(r.status_code, 200)
        self.assertIn("me@example.com", html)
        self.assertIn("+41", html)
        self.assertIn("salt okunur", html)
        for action in ("growth:logout", "growth:billing"):
            self.assertNotIn(reverse(action), html)
        self.assertNotIn(reverse("growth:cancel", args=[self.sub.pk]), html)
        self.assertNotIn("csrfmiddlewaretoken", html)  # no form at all
        self.assertIn("no-cache", r["Cache-Control"])
        self.assertFalse(AccountActivity.objects.filter(user=self.user, kind="dashboard").exists())
        self.assertEqual(self.client.get(reverse("growth:view_as", args=[9999])).status_code, 404)

    def test_admin_lists_link_to_the_read_only_dashboard(self):
        Customer.objects.create(user=self.user, lang="de")
        boss = get_user_model().objects.create_superuser("boss", "boss@example.com", "pass-word-1")
        self.client.force_login(boss)
        link = reverse("growth:view_as", args=[self.user.pk])
        self.assertContains(self.client.get(reverse("admin:growth_customer_changelist")), f"{link}?lang=de")
        self.assertContains(self.client.get(reverse("admin:growth_agencysubscription_changelist")), link)

    def test_stats_api_updates_only_the_fields_sent(self):
        SubscriptionStat.objects.create(subscription=self.sub, date=self.today, new_followers=40, impressions=700, visits=420)
        with override_settings(GROWTH_API_TOKEN="tok_test"):
            r = self.client.post(reverse("growth:api_stats"), json.dumps({"subscription_id": self.sub.pk, "date": str(self.today),
                                                                          "followers": 5000}),
                                 content_type="application/json", HTTP_AUTHORIZATION="Bearer tok_test")
        self.assertEqual(r.status_code, 200)
        row = SubscriptionStat.objects.get()
        self.assertEqual((row.followers, row.new_followers, row.impressions, row.visits), (5000, 40, 700, 420))


@override_settings(**MAIL)
class AccountTests(TestCase):
    def test_login_logout_and_bad_password(self):
        get_user_model().objects.create_user("me@example.com", "me@example.com", "pass-word-1")
        r = self.client.post(reverse("growth:login") + "?lang=en", {"email": "me@example.com", "password": "wrong-pass"})
        self.assertEqual(r.status_code, 400)
        r = self.client.post(reverse("growth:login") + "?lang=en", {"email": "ME@example.com", "password": "pass-word-1"})
        self.assertEqual(r["Location"], f"{reverse('growth:account')}?lang=en")
        self.assertEqual(self.client.get(r["Location"]).status_code, 200)
        self.client.post(reverse("growth:logout"), {"lang": "en"})
        self.assertEqual(self.client.get(reverse("growth:account")).status_code, 302)

    def test_login_ignores_offsite_next(self):
        get_user_model().objects.create_user("me@example.com", "me@example.com", "pass-word-1")
        r = self.client.post(reverse("growth:login"), {"email": "me@example.com", "password": "pass-word-1", "next": "https://evil.example/"})
        self.assertTrue(r["Location"].startswith(reverse("growth:account")))

    def test_password_reset(self):
        get_user_model().objects.create_user("me@example.com", "me@example.com", "pass-word-1")
        self.client.post(reverse("growth:reset") + "?lang=en", {"email": "me@example.com"})
        self.client.post(reverse("growth:reset") + "?lang=en", {"email": "nobody@example.com"})
        self.assertEqual(len(mail.outbox), 1)
        path = re.search(r"https?://[^/\s]+(/account/password/\S+)", mail.outbox[0].body).group(1)
        r = self.client.post(path, {"password": "brand-new-pass"})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(get_user_model().objects.get().check_password("brand-new-pass"))
        self.assertEqual(self.client.get(path).status_code, 200)  # used link now shows "invalid"

    def test_signup(self):
        r = self.client.post(reverse("growth:signup") + "?lang=en", {"email": "new@example.com", "password": "pass-word-1", "consent": "on"})
        self.assertEqual(r["Location"], f"{reverse('growth:account')}?lang=en&verify=sent")
        self.assertTrue(mail.outbox[0].subject.startswith("Confirm your email"))
        r = self.client.post(reverse("growth:signup") + "?lang=en", {"email": "new@example.com", "password": "pass-word-1", "consent": "on"})
        self.assertEqual(r.status_code, 400)


@override_settings(GOOGLE_OAUTH_CLIENT_ID="cid.apps.googleusercontent.com", GOOGLE_OAUTH_CLIENT_SECRET="GOCSPX-x", **MAIL)
class GoogleSignInTests(FreshCache, TestCase):
    def start(self, next_url="/en/tiktok-followers/#start"):
        r = self.client.get(reverse("growth:google") + "?lang=de&next=" + next_url.replace("#", "%23"))
        self.assertTrue(r["Location"].startswith("https://accounts.google.com/o/oauth2/v2/auth?"))
        self.assertIn("redirect_uri=http%3A%2F%2Ftestserver%2Faccount%2Fgoogle%2Fcomplete%2F", r["Location"])
        return self.client.session["google_oauth"]["state"]

    def complete(self, state, info):
        token = mock.Mock(json=mock.Mock(return_value={"access_token": "at"}))
        userinfo = mock.Mock(json=mock.Mock(return_value=info))
        with mock.patch("apps.growth.accounts.requests.post", return_value=token), \
             mock.patch("apps.growth.accounts.requests.get", return_value=userinfo):
            return self.client.get(reverse("growth:google_complete") + f"?state={state}&code=abc")

    def test_new_user_is_created_verified_and_sent_back(self):
        state = self.start()
        r = self.complete(state, {"email": "New@Gmail.com", "email_verified": True, "given_name": "Ada"})
        self.assertEqual(r["Location"], "/en/tiktok-followers/#start")
        user = get_user_model().objects.get(username="new@gmail.com")
        self.assertFalse(user.has_usable_password())
        self.assertTrue(user.customer.email_verified)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_existing_account_signs_in(self):
        user = get_user_model().objects.create_user("me@gmail.com", "me@gmail.com", "pass-word-1")
        self.complete(self.start(), {"email": "me@gmail.com", "email_verified": True})
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)
        self.assertTrue(get_user_model().objects.get().check_password("pass-word-1"))

    def test_bad_state_or_unverified_email_fails(self):
        self.start()
        r = self.complete("wrong", {"email": "x@gmail.com", "email_verified": True})
        self.assertIn("google=failed", r["Location"])
        r = self.complete(self.start(), {"email": "x@gmail.com", "email_verified": False})
        self.assertIn("google=failed", r["Location"])
        self.assertFalse(get_user_model().objects.exists())

    def test_button_shows_on_login_and_order_form(self):
        self.assertContains(self.client.get(reverse("growth:login") + "?lang=en"), "Continue with Google")
        self.assertContains(self.client.get(page_path("en", "main")), "Continue with Google")


@override_settings(GOOGLE_OAUTH_CLIENT_ID="cid.apps.googleusercontent.com", GOOGLE_OAUTH_CLIENT_SECRET="GOCSPX-x")
class GoogleOrderTests(FreshCache, TestCase):
    """Order details first, then "Continue with Google" instead of email + password."""

    def google_order(self, **extra):
        data = order_data(via="google", platform="tiktok", plan="pro", **extra)
        del data["email"], data["password"]
        r = self.client.post(reverse("growth:order"), data)
        self.assertTrue(r["Location"].startswith(reverse("growth:google") + "?lang=en&order=1&next="))
        self.client.get(r["Location"])
        state = self.client.session["google_oauth"]["state"]
        token = mock.Mock(json=mock.Mock(return_value={"access_token": "at"}))
        userinfo = mock.Mock(json=mock.Mock(return_value={"email": "fan@gmail.com", "email_verified": True}))
        with mock.patch("apps.growth.accounts.requests.post", return_value=token), \
             mock.patch("apps.growth.accounts.requests.get", return_value=userinfo):
            return self.client.get(reverse("growth:google_complete") + f"?state={state}&code=abc")

    @override_settings(**STRIPE_OFF)
    def test_request_mode_places_the_filled_in_order(self):
        r = self.google_order()
        sub = AgencySubscription.objects.get()
        self.assertEqual((sub.email, sub.platform, sub.handle, sub.plan, sub.status),
                         ("fan@gmail.com", "tiktok", "my.brand", "pro", "requested"))
        self.assertIn(f"sub={sub.pk}", r["Location"])
        self.assertNotIn("google_order", self.client.session)

    @override_settings(**STRIPE_ON)
    def test_payments_on_go_straight_to_stripe(self):
        session = SimpleNamespace(id="cs_g", url="https://checkout.stripe.com/c/pay/cs_g")
        with mock.patch("apps.growth.billing.create_checkout", return_value=session) as create:
            r = self.google_order()
        self.assertEqual((r.status_code, r["Location"]), (303, session.url))  # Google verified the email: no extra step
        self.assertEqual(create.call_args.args[0].plan, "pro")

    @override_settings(**STRIPE_OFF)
    def test_details_are_still_required(self):
        data = order_data(via="google", handle="")
        del data["email"], data["password"]
        r = self.client.post(reverse("growth:order"), data)
        self.assertEqual(r.status_code, 400)
        self.assertContains(r, 'name="email"', status_code=400)  # the email/password option is still there
        self.assertNotIn("google_order", self.client.session)

    @override_settings(**STRIPE_OFF)
    def test_plain_sign_in_does_not_place_an_abandoned_order(self):
        data = order_data(via="google")
        del data["email"], data["password"]
        self.client.post(reverse("growth:order"), data)  # went to Google, never came back
        self.client.get(reverse("growth:google") + "?lang=en")  # later: plain sign-in
        self.assertNotIn("google_order", self.client.session)

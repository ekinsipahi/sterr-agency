"""Dispute evidence for a subscription, in the shape of Stripe's dispute `evidence` fields
(English, for the card issuer). Staged on Stripe when a dispute opens (views._on_dispute)
and shown in the admin (Kanıt paketi) to print or check before pressing Submit."""
from django.conf import settings
from django.urls import reverse

from .constants import PROFILE_URL
from .models import AccountActivity
from .plan import PLAN_BY_KEY

TEXT_LIMIT = 19000  # Stripe allows 20,000 characters per text field
CANCEL_WAYS = {"account": "the Cancel button in their account",
               "stripe": "the Stripe billing portal"}
ACTIVITY = {"login": "signed in", "dashboard": "opened the growth dashboard", "cancel_page": "opened the cancel page"}


def _utc(value):
    return f"{value:%Y-%m-%d %H:%M} UTC" if value else "-"


def _n(value):
    return f"{value:,}" if value is not None else "-"


def delivery_log(sub):
    """One line per day the growth system reported, newest first."""
    stats = {s.date: s for s in sub.stats.all()}
    lines = []
    for day in reversed(sub.daily()):
        stat = stats[day["date"]]
        reach = []
        if stat.impressions is not None:
            reach.append(f"follow step shown {_n(stat.impressions)} times")
        if stat.visits is not None:
            reach.append(f"{_n(stat.visits)} visited the profile")
        if stat.confirms is not None:
            reach.append(f"{_n(stat.confirms)} tapped Done after the follow step")
        result = f"{_n(day['followers'])} new followers (estimated)" if day["followers"] is not None else ""
        countries = ", ".join(f"{code} {_n(v.get('impressions'))}" for code, v in
                              sorted(stat.countries.items(), key=lambda kv: -kv[1].get("impressions", 0))[:6])
        parts = [p for p in ("; ".join(reach), result, f"countries (people shown): {countries}" if countries else "") if p]
        account = f" (account: {_n(stat.followers)} followers)" if stat.followers is not None else ""
        lines.append(f"{stat.date:%Y-%m-%d}: {'; '.join(parts) or 'reported'}{account}")
    return lines


def activity_log(sub):
    if not sub.user_id:
        return []
    return [f"{_utc(a.at)}: {ACTIVITY.get(a.kind, a.kind)} from IP {a.ip or '-'} ({a.user_agent[:90] or 'unknown browser'})"
            for a in AccountActivity.objects.filter(user_id=sub.user_id)[:300]]



def build(sub):
    """Stripe dispute evidence fields for this subscription (text only; files are added by hand)."""
    package = PLAN_BY_KEY[sub.plan]
    low, high = package["followers"]
    terms_url = f"{settings.SITE_URL}{reverse('core:terms')}"
    profile = PROFILE_URL[sub.platform].format(sub.handle)
    delivery = delivery_log(sub)
    activity = activity_log(sub)
    reports = sub.stats.count()

    product = (
        f"Sterr Agency {sub.get_plan_display()}: a monthly growth-agency subscription (${sub.amount:.2f} a month) for the "
        f"customer's {sub.platform_name} account @{sub.handle} ({profile}), target audience: {sub.location}. "
        f"During every 30-day period we promote the customer's public profile to real people through our partner "
        f"network; people who like it follow, like and comment on their own (typically {low:,}-{high:,} new followers a month, "
        f"described on the site as a typical range, not a fixed count). It is a digital service delivered every day "
        f"from the first payment; no password or account access is needed. The customer follows the results day by day "
        f"in their account dashboard at {settings.SITE_URL}{reverse('growth:account')}."
    )
    disclosure = (
        f"Before paying, the customer ticked a required box accepting our terms (version {sub.terms_version or '-'}, "
        f"accepted {_utc(sub.terms_accepted_at)} from IP {sub.ip or '-'}). The order form, Stripe Checkout and the welcome "
        f"email all say: billed monthly until canceled; cancel any time in the account; canceling stops the next payment "
        f"and the paid month runs to its end and isn't refunded. A reminder with the renewal date, the amount and how to "
        f"cancel is emailed 3 days before every renewal. Terms, section 2a: {terms_url}"
    )
    if sub.cancel_requested_at:
        rebuttal = (f"The customer canceled the renewal on {_utc(sub.cancel_requested_at)} through "
                    f"{CANCEL_WAYS.get(sub.cancel_source, 'Stripe')}. No payment was taken after that; the package ran to "
                    f"the end of the period already paid for, as the terms say.")
    else:
        rebuttal = ("The customer never canceled: there is no cancellation from the Cancel button in the account "
                    "or the billing portal on record, although canceling takes one click.")
    if sub.reminded_for:
        rebuttal += f" The renewal reminder, saying how to cancel, was emailed to {sub.email} before the renewal of {_utc(sub.reminded_for)}."
    summary = [
        f"Subscription started {_utc(sub.started_at)}; status {sub.status}; current period ends {_utc(sub.current_period_end)}.",
        f"Welcome email with the terms sent to {sub.email} on activation.",
        f"Account followers at the start: {_n(sub.start_followers)}; latest: {_n(sub.current_followers)}"
        f" ({_utc(sub.stats_at)}); {reports} daily delivery reports on record.",
        "", "Daily delivery log (UTC days, from our delivery system). Visits are taps that opened the customer's "
            "profile. New followers are estimated: the day's views of the follow step times the follow rate measured "
            "from the account's real follower counts, never more than the visits. 'Tapped Done' is the visitor's own "
            "confirmation and is not a follow count:", *delivery,
    ]
    evidence = {
        "product_description": product,
        "customer_email_address": sub.email,
        "customer_name": (sub.user.get_full_name() if sub.user_id else "") or sub.email,
        "customer_purchase_ip": sub.ip or "",
        "service_date": f"{sub.started_at:%Y-%m-%d}" if sub.started_at else "",
        "cancellation_policy_disclosure": disclosure,
        "cancellation_rebuttal": rebuttal,
        "refund_policy_disclosure": ("Paid months are not refunded: the service starts with the payment and is delivered "
                                     "across the month. Shown on the order form, in Stripe Checkout, in the welcome email "
                                     f"and in the terms (section 2a): {terms_url}"),
        "refund_refusal_explanation": ("The service for the disputed period was delivered every day, as the delivery log "
                                       "shows, and the customer could cancel the next renewal at any time in one click."),
        "access_activity_log": "\n".join(activity) or "No sign-ins on record.",
        "uncategorized_text": "\n".join(summary),
    }
    return {k: v[:TEXT_LIMIT] for k, v in evidence.items() if v}

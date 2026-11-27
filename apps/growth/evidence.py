"""Dispute evidence for a subscription, in the shape of Stripe's dispute `evidence` fields
(English, for the card issuer). Staged on Stripe when a dispute opens (views._on_dispute)
and shown in the admin (Kanıt paketi) to print or check before pressing Submit. The wording
follows the platform (sub.words): followers and a profile, or subscribers and a channel."""
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
    w = sub.words
    lines = []
    for day in reversed(sub.daily()):
        stat = stats[day["date"]]
        reach = []
        if stat.impressions is not None:
            reach.append(f"{w['follow']} step shown {_n(stat.impressions)} times")
        if stat.visits is not None:
            reach.append(f"{_n(stat.visits)} visited the {w['profile']}")
        if stat.confirms is not None:
            reach.append(f"{_n(stat.confirms)} tapped Done after the {w['follow']} step")
        result = f"{_n(day['followers'])} new {w['audience']} (estimated)" if day["followers"] is not None else ""
        countries = ", ".join(f"{code} {_n(v.get('impressions'))}" for code, v in
                              sorted(stat.countries.items(), key=lambda kv: -kv[1].get("impressions", 0))[:6])
        parts = [p for p in ("; ".join(reach), result, f"countries (people shown): {countries}" if countries else "") if p]
        account = f" (account: {_n(stat.followers)} {w['audience']})" if stat.followers is not None else ""
        lines.append(f"{stat.date:%Y-%m-%d}: {'; '.join(parts) or 'reported'}{account}")
    return lines


def activity_log(sub):
    if not sub.user_id:
        return []
    return [f"{_utc(a.at)}: {ACTIVITY.get(a.kind, a.kind)} from IP {a.ip or '-'} ({a.user_agent[:90] or 'unknown browser'})"
            for a in AccountActivity.objects.filter(user_id=sub.user_id)[:300]]




CARRYOVER_POLICY = (
    "Current merchant commitment (terms section 2a.1, effective 2026-11-13): monthly growth can fall below "
    "the applicable target (for example 1,000 {audience}). Verified shortfalls for paid periods are recorded "
    "and completed in addition to later months' normal growth, at no extra charge. Canceling the subscription, "
    "stopping Stripe automatic payments or removing the payment method does not erase this obligation; no new "
    "subscription or payment is required. The {profile} must remain public and accessible. This commitment is "
    "not proof of completed delivery and does not restrict mandatory consumer, refund or payment dispute rights. "
    "It does not establish that a customer accepted a later terms version."
)


def carryover_policy(sub):
    return CARRYOVER_POLICY.format(**sub.words)


def carryover_record(sub):
    w = sub.words
    if sub.outstanding_followers is None:
        return (f"Outstanding {w['one']} balance: not yet reconciled. Paid-period targets and verified delivery "
                "must be reviewed before stating a number; missing data is not a zero balance. "
                "Daily delivery estimates below are not a verified reconciliation.")
    return (
        f"Reconciliation as of {_utc(sub.reconciled_at)}: total applicable target for paid periods "
        f"{_n(sub.reconciled_target)} {w['audience']}; verified delivery allocated to those targets "
        f"{_n(sub.reconciled_delivered)}; outstanding {w['one']} balance {_n(sub.outstanding_followers)} "
        f"(max(target - delivery, 0)). Basis: {sub.reconciliation_note}. "
        "This is a staff-reviewed snapshot, not an automatically verified total or proof of full delivery "
        "for the disputed invoice. Cancellation does not clear the recorded balance."
    )


def build(sub):
    """Stripe dispute evidence fields for this subscription (text only; files are added by hand)."""
    package = PLAN_BY_KEY[sub.plan]
    low, high = package["followers"]
    terms_url = f"{settings.SITE_URL}{reverse('core:terms')}"
    profile = PROFILE_URL[sub.platform].format(sub.handle)
    delivery = delivery_log(sub)
    activity = activity_log(sub)
    reports = sub.stats.count()
    carryover = carryover_record(sub)
    policy = carryover_policy(sub)
    w = sub.words
    joins = "subscribe, watch, like and comment" if w["audience"] == "subscribers" else "follow, like and comment"

    product = (
        f"Sterr Agency {sub.get_plan_display()}: a monthly growth-agency subscription (${sub.amount:.2f} a month) for the "
        f"customer's {sub.platform_name} account @{sub.handle} ({profile}), target audience: {sub.location}. "
        f"During every 30-day period we promote the customer's public {w['profile']} to real people through our partner "
        f"network; people who like it {joins} on their own (typically {low:,}-{high:,} new {w['audience']} a month, "
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
                    f"{CANCEL_WAYS.get(sub.cancel_source, 'Stripe')}. Cancellation stops future renewals; the paid service period is recorded through "
                    f"{_utc(sub.current_period_end)}. This does not establish that all delivery is complete.")
    else:
        rebuttal = ("The customer never canceled: there is no cancellation from the Cancel button in the account "
                    "or the billing portal on record, although canceling takes one click.")
    if sub.reminded_for:
        rebuttal += f" The renewal reminder, saying how to cancel, was emailed to {sub.email} before the renewal of {_utc(sub.reminded_for)}."
    disclosure += " " + policy
    rebuttal += " " + policy + " " + carryover
    summary = [
        policy, carryover, "",
        f"Subscription started {_utc(sub.started_at)}; status {sub.status}; current period ends {_utc(sub.current_period_end)}.",
        f"Welcome email with the terms sent to {sub.email} on activation.",
        f"Account {w['audience']} at the start: {_n(sub.start_followers)}; latest: {_n(sub.current_followers)}"
        f" ({_utc(sub.stats_at)}); {reports} daily delivery reports on record.",
        "", "Daily delivery log (UTC days, from our delivery system). Visits are taps that opened the customer's "
            f"{w['profile']}. New {w['audience']} are estimated: the day's views of the {w['follow']} step times the {w['follow']} rate measured "
            f"from the account's real {w['one']} counts, never more than the visits. 'Tapped Done' is the visitor's own "
            f"confirmation and is not a {w['follow']} count:", *delivery,
    ]
    shared = [r for r in (sub.shared_usernames or []) if r.get("status") == "exists"]
    if shared:
        summary += ["", f"{len(shared)} visitors we sent typed their {sub.platform_name} username after the {w['follow']} step "
                        f"(optional field). Each account was checked to exist; the customer can find them in the "
                        f"{w['profile']}'s {w['audience']} list: "
                        + ", ".join(f"@{r['handle']} ({r['date']}{', ' + r['country'] if r['country'] else ''})" for r in shared)]
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
        "refund_refusal_explanation": (
            "Delivery records and the reviewed balance are supplied for assessment. We do not assert full "
            "delivery solely because a subscription existed or a shortfall is scheduled for completion. "
            + carryover + " " + policy),
        "access_activity_log": "\n".join(activity) or "No sign-ins on record.",
        "uncategorized_text": "\n".join(summary),
    }
    return {k: v[:TEXT_LIMIT] for k, v in evidence.items() if v}

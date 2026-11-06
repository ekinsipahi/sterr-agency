"""Delivery numbers from Linksterr, where the promoted campaigns behind each package run.
GET {LINKSTERR_API_URL}/user-api/v1/agency/accounts/ with LINKSTERR_AGENCY_TOKEN (the same
token is set on Linksterr) returns, per account and UTC day: new followers (Linksterr's
calibrated count of real follows, never more than the profile visits), profile visits,
impressions, "I followed" confirms and countries, plus dated follower readings.

sync() stores them in SubscriptionStat for the days the package ran, so the dashboard, the
admin and dispute evidence fill themselves. Days older than FINAL_AFTER_DAYS keep what was
stored: a customer never sees yesterday's number change when the model's rate moves."""
import logging
from datetime import timedelta, timezone as dt_timezone

import requests
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_date

from .models import SubscriptionStat

logger = logging.getLogger(__name__)

PATH = "/user-api/v1/agency/accounts/"
TIMEOUT = (3, 8)            # connect, read: the dashboard waits for this at most
FRESH_SECONDS = 10 * 60     # a subscription is fetched at most this often (unless forced)
FINAL_AFTER_DAYS = 2        # older days are settled and never rewritten
MAX_ACCOUNTS, MAX_DAYS = 100, 400   # Linksterr's limits per request
FIELDS = ("new_followers", "visits", "impressions", "confirms")


def enabled():
    return bool(settings.LINKSTERR_AGENCY_TOKEN)


def account_key(sub):
    return f"{sub.platform}:{sub.handle.lstrip('@').lower()}"


def period(sub, today):
    """First and last UTC day of delivery for this subscription (Linksterr counts UTC days)."""
    start = sub.started_at.astimezone(dt_timezone.utc).date()
    end = today
    if sub.status == "canceled" and sub.canceled_at:
        end = min(end, sub.canceled_at.astimezone(dt_timezone.utc).date())
    return start, end


def fetch(accounts, since, until):
    """{account: Linksterr's account dict}. Raises requests/ValueError errors."""
    params = [("account", a) for a in accounts] + [("since", since.isoformat()), ("until", until.isoformat())]
    response = requests.get(settings.LINKSTERR_API_URL.rstrip("/") + PATH, params=params, timeout=TIMEOUT,
                            headers={"Authorization": f"Bearer {settings.LINKSTERR_AGENCY_TOKEN}"})
    response.raise_for_status()
    return {item["account"]: item for item in response.json()["accounts"]}


def _count(value):
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else 0


def _countries(value):
    if not isinstance(value, dict):
        return {}
    return {cc.upper(): {f: _count((numbers or {}).get(f)) for f in ("impressions", "visits", "confirms")}
            for cc, numbers in value.items()
            if isinstance(cc, str) and len(cc) == 2 and cc.isalpha() and isinstance(numbers, dict)}


def _readings(account):
    out = {}
    for reading in account.get("readings") or []:
        date = parse_date(str(reading.get("date", "")))
        if date is not None:
            out[date] = _count(reading.get("followers"))
    return sorted(out.items())


def store(sub, account, today):
    """Write one account's days into the subscription's stats. Returns the days written."""
    start, end = period(sub, today)
    settled = today - timedelta(days=FINAL_AFTER_DAYS)
    readings = _readings(account)
    on_day = dict(readings)
    written = 0
    with transaction.atomic():
        for day in account.get("days") or []:
            date = parse_date(str(day.get("date", "")))
            if date is None or not start <= date <= end:
                continue
            values = {f: _count(day.get(f)) for f in FIELDS}
            values["countries"] = _countries(day.get("countries"))
            if date in on_day:
                values["followers"] = on_day[date]
            row, created = SubscriptionStat.objects.get_or_create(subscription=sub, date=date, defaults=values)
            if not created:
                if date < settled:
                    continue
                for name, value in values.items():
                    setattr(row, name, value)
                row.save(update_fields=[*values])
            written += 1
        # The account's count when the package started: the last reading in the two weeks up
        # to its first day, else the first one after it. "Now": the latest reading.
        before = [f for d, f in readings if start - timedelta(days=14) <= d <= start]
        after = [f for d, f in readings if start < d <= end]
        if sub.start_followers is None and (before or after):
            sub.start_followers = before[-1] if before else after[0]
        latest = [f for d, f in readings if d <= end]
        if latest:
            sub.current_followers = latest[-1]
        sub.stats_at = timezone.now()
        sub.save(update_fields=["start_followers", "current_followers", "stats_at", "updated_at"])
    return written


def sync(subs, force=False):
    """Fetch and store the numbers of these subscriptions (those that have started). At most
    one fetch per subscription every FRESH_SECONDS unless `force`. Returns how many were
    updated; never raises, so a Linksterr outage only means older numbers."""
    if not enabled():
        return 0
    subs = [s for s in subs if s.started_at and (force or cache.add(f"linksterr-sync:{s.pk}", 1, FRESH_SECONDS))]
    if not subs:
        return 0
    today = timezone.now().astimezone(dt_timezone.utc).date()
    since = max(min(period(s, today)[0] for s in subs), today - timedelta(days=MAX_DAYS - 1))
    accounts = sorted({account_key(s) for s in subs})
    data = {}
    try:
        for i in range(0, len(accounts), MAX_ACCOUNTS):
            data.update(fetch(accounts[i:i + MAX_ACCOUNTS], min(since, today), today))
    except (requests.RequestException, ValueError, KeyError, TypeError):
        logger.warning("Linksterr sync failed for %s", [s.pk for s in subs], exc_info=True)
        return 0
    updated = 0
    for sub in subs:
        account = data.get(account_key(sub))
        if account is None:
            continue
        try:
            store(sub, account, today)
            updated += 1
        except Exception:
            logger.exception("Could not store Linksterr numbers for subscription #%s", sub.pk)
    return updated

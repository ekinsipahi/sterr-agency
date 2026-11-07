"""Delivery numbers from Linksterr, where the promoted campaigns behind each package run.
GET {LINKSTERR_API_URL}/user-api/v1/agency/accounts/ with LINKSTERR_AGENCY_TOKEN (the same
token is set on Linksterr) returns, per account and UTC day: new followers (Linksterr's
calibrated count of real follows, never more than the profile visits), profile visits,
impressions, "Done" taps and countries, plus dated follower readings.

sync() stores them in SubscriptionStat for the days the package ran, so the dashboard, the
admin and dispute evidence fill themselves. A day is settled once it was fetched after it
ended (UTC) and is FINAL_AFTER_DAYS old: from then on a customer never sees its number change
when Linksterr's rate moves. A day fetched while still running is fetched again later."""
import logging
import re
from datetime import datetime, time, timedelta, timezone as dt_timezone

import requests
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_date

from .models import AgencySubscription, SubscriptionStat

logger = logging.getLogger(__name__)

PATH = "/user-api/v1/agency/accounts/"
TIMEOUT = (3, 8)            # connect, read: the dashboard waits for this at most
FRESH_SECONDS = 10 * 60     # a subscription is fetched at most this often (unless forced)
FINAL_AFTER_DAYS = 2        # a day fetched after it ended is settled once it is this old
MAX_ACCOUNTS, MAX_DAYS = 100, 400   # Linksterr's limits per request
READING_LOOKBACK_DAYS = 14  # a follower reading this long before the package still counts as its start
FIELDS = ("new_followers", "visits", "impressions", "confirms")
HANDLE = re.compile(r"[A-Za-z0-9._]{1,30}")   # what Linksterr accepts


def enabled():
    return bool(settings.LINKSTERR_AGENCY_TOKEN)


def account_key(sub):
    return f"{sub.platform}:{sub.handle.strip().lstrip('@').lower()}"


def _valid(sub):
    return sub.platform in ("instagram", "tiktok") and bool(HANDLE.fullmatch(sub.handle.strip().lstrip("@")))


def _utc_day(value):
    return value.astimezone(dt_timezone.utc).date()


def period(sub, today):
    """First and last UTC day of delivery for this subscription (Linksterr counts UTC days)."""
    start = _utc_day(sub.started_at)
    end = today
    if sub.status == "canceled" and sub.canceled_at:
        end = min(end, _utc_day(sub.canceled_at))
    return start, end


def _periods(subs, today):
    """{sub.pk: (start, end)} where several packages of one account never claim the same day:
    a day belongs to the package that started last on or before it."""
    by_account = {}
    for sub in subs:
        by_account.setdefault(account_key(sub), []).append(sub)
    out = {}
    for group in by_account.values():
        group.sort(key=lambda s: (s.started_at, s.pk))
        for sub, after in zip(group, group[1:] + [None]):
            start, end = period(sub, today)
            if after is not None:
                end = min(end, _utc_day(after.started_at) - timedelta(days=1))
            out[sub.pk] = (start, end)
    return out


def _day_end(day):
    return datetime.combine(day + timedelta(days=1), time.min, tzinfo=dt_timezone.utc)


def _settled(row, today):
    return (row.date < today - timedelta(days=FINAL_AFTER_DAYS)
            and row.synced_at is not None and row.synced_at >= _day_end(row.date))


def _since(sub, start, today):
    """The first day still worth fetching: the oldest day of the package that is not settled."""
    rows = list(sub.stats.filter(date__gte=start))
    if not rows:
        return start
    open_days = [r.date for r in rows if not _settled(r, today)]
    return max(start, min(open_days + [today - timedelta(days=FINAL_AFTER_DAYS)]))


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


def store(sub, account, today, start=None, end=None):
    """Write one account's days into the subscription's stats for [start, end] (default: the
    subscription's period). Returns the days written."""
    if start is None or end is None:
        start, end = period(sub, today)
    now = timezone.now()
    readings = _readings(account)
    written = 0
    with transaction.atomic():
        for day in account.get("days") or []:
            date = parse_date(str(day.get("date", "")))
            if date is None or not start <= date <= end:
                continue
            values = {f: _count(day.get(f)) for f in FIELDS}
            values["countries"] = _countries(day.get("countries"))
            values["synced_at"] = now
            row, created = SubscriptionStat.objects.get_or_create(subscription=sub, date=date, defaults=values)
            if not created:
                if _settled(row, today):
                    continue
                for name, value in values.items():
                    setattr(row, name, value)
                row.save(update_fields=[*values])
            written += 1
        # Follower readings are measurements: they go on their day's row even when it is settled.
        for date, followers in readings:
            if start <= date <= end:
                SubscriptionStat.objects.filter(subscription=sub, date=date).exclude(followers=followers).update(
                    followers=followers)
        # The account's count when the package started: the last reading in the two weeks up to
        # its first day, else the first one after it. "Now": the latest reading of that time.
        recent = [(d, f) for d, f in readings if start - timedelta(days=READING_LOOKBACK_DAYS) <= d <= end]
        before = [f for d, f in recent if d <= start]
        after = [f for d, f in recent if d > start]
        if sub.start_followers is None and (before or after):
            sub.start_followers = before[-1] if before else after[0]
        if recent:
            sub.current_followers = recent[-1][1]
        sub.stats_at = now
        sub.save(update_fields=["start_followers", "current_followers", "stats_at", "updated_at"])
    return written


def sync(subs, force=False):
    """Fetch and store the numbers of these subscriptions (those that have started). At most
    one fetch per subscription every FRESH_SECONDS unless `force`. Returns how many were
    updated; never raises, so a Linksterr outage only means older numbers."""
    if not enabled():
        return 0
    subs = [s for s in subs if s.started_at and _valid(s)
            and (force or cache.add(f"linksterr-sync:{s.pk}", 1, FRESH_SECONDS))]
    if not subs:
        return 0
    today = timezone.now().astimezone(dt_timezone.utc).date()
    keys = {account_key(s) for s in subs}
    # Every package of these accounts, whoever bought it, so no day is counted twice.
    periods = _periods([s for s in AgencySubscription.objects.exclude(started_at=None) if account_key(s) in keys], today)
    oldest = today - timedelta(days=MAX_DAYS - 1)
    since = max(min(_since(s, periods[s.pk][0], today) for s in subs), oldest)
    accounts = sorted({account_key(s) for s in subs})
    data = {}
    for i in range(0, len(accounts), MAX_ACCOUNTS):
        batch = accounts[i:i + MAX_ACCOUNTS]
        try:
            data.update(fetch(batch, min(since, today), today))
        except (requests.RequestException, ValueError, KeyError, TypeError):
            logger.warning("Linksterr sync failed for %s", batch, exc_info=True)
    updated = 0
    for sub in subs:
        account = data.get(account_key(sub))
        if account is None:
            continue
        start, end = periods[sub.pk]
        try:
            store(sub, account, today, start, end)
            updated += 1
        except Exception:
            logger.exception("Could not store Linksterr numbers for subscription #%s", sub.pk)
    return updated

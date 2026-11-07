"""Machine API for the growth system. Authenticated with `Authorization: Bearer
<GROWTH_API_TOKEN>`; disabled while the token is unset. The subscriptions list also opens
with LINKSTERR_AGENCY_TOKEN (read-only): Linksterr reads it to keep each package's campaign
running, renewed, resumed or ended.

GET  /growth/api/subscriptions/?status=active   accounts to grow, newest first (default: active;
     several: status=active,past_due,canceled; packages that ended over 90 days ago are left out;
     the Linksterr token sees only paid packages in those three statuses)
POST /growth/api/stats/                         one day's numbers or {"updates": [...]}:
     {"subscription_id": 12, "date": "2026-11-04", "followers": 5120,
      "new_followers": 140, "start_followers": 4300}
     Only subscription_id is required; "date" defaults to today (UTC). Sending the same
     subscription + date again updates only the fields sent. new_followers is what we brought that day (left
     out: the change in the follower count); likes and comments are counted from it
     (× 2.5 and ÷ 10) unless sent. followers is the account's follower count that day. start_followers (the
     count when the package started) defaults to the first reading's followers.
     Delivery evidence (kept for disputes, optional): "impressions" (people shown the
     profile), "visits" (went to it), "confirms" (said they followed) and "countries":
     {"DE": {"impressions": 900, "visits": 210, "confirms": 95}, ...}.
Linksterr's numbers arrive without this API: linksterr.py fetches them (pull).
"""
import hmac
import json
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import AgencySubscription, SubscriptionStat

MAX_UPDATES = 500
MAX_SUBSCRIPTIONS = 5000
ENDED_DAYS = 90
LINKSTERR_STATUSES = ("active", "past_due", "canceled")
COUNTRY_FIELDS = ("impressions", "visits", "confirms")
STAT_FIELDS = ("followers", "new_followers", "likes", "comments", *COUNTRY_FIELDS)


def _caller(request, read_only=False):
    """'growth' (GROWTH_API_TOKEN: the whole API), 'linksterr' (LINKSTERR_AGENCY_TOKEN: only the
    subscriptions list) or None."""
    given = request.headers.get("Authorization", "").removeprefix("Bearer ").strip().encode()
    callers = [("growth", settings.GROWTH_API_TOKEN), ("linksterr", settings.LINKSTERR_AGENCY_TOKEN if read_only else "")]
    return next((name for name, token in callers if token and hmac.compare_digest(given, token.encode())), None)


def _authorized(request):
    return _caller(request) == "growth"


def _iso(value):
    return value.isoformat() if value else None


def _sub_json(s):
    return {"id": s.pk, "platform": s.platform, "handle": s.handle, "location": s.location, "status": s.status,
            "plan": s.plan, "amount": float(s.amount), "started_at": _iso(s.started_at),
            "current_period_end": _iso(s.current_period_end), "cancel_at_period_end": s.cancel_at_period_end,
            "canceled_at": _iso(s.canceled_at), "start_followers": s.start_followers,
            "current_followers": s.current_followers}


@require_GET
def subscriptions(request):
    caller = _caller(request, read_only=True)
    if caller is None:
        return JsonResponse({"error": "unauthorized"}, status=401)
    qs = AgencySubscription.objects.filter(status__in=request.GET.get("status", "active").split(","))
    if caller == "linksterr":  # only paid packages, only what its campaigns need
        qs = qs.filter(status__in=LINKSTERR_STATUSES).exclude(started_at=None)
    # A package that ended long ago has nothing left to stop; keeping it out keeps every running one in.
    qs = qs.exclude(status="canceled", canceled_at__lt=timezone.now() - timedelta(days=ENDED_DAYS))
    qs = qs.order_by("-started_at", "-created_at")[:MAX_SUBSCRIPTIONS]
    return JsonResponse({"subscriptions": [_sub_json(s) for s in qs]})


def _countries(value):
    if value is None:
        return {}
    if not isinstance(value, dict) or len(value) > 250:
        raise ValueError("countries must be an object of up to 250 country codes")
    out = {}
    for country, numbers in value.items():
        if not (isinstance(country, str) and len(country) == 2 and country.isalpha()) or not isinstance(numbers, dict):
            raise ValueError("countries: use 2-letter codes, each with impressions/visits/confirms")
        out[country.upper()] = {f: _int(numbers.get(f), f"countries.{country}.{f}") or 0 for f in COUNTRY_FIELDS}
    return out


def _int(value, name, required=False):
    if value is None and not required:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


@csrf_exempt
@require_POST
def stats(request):
    if not _authorized(request):
        return JsonResponse({"error": "unauthorized"}, status=401)
    try:
        payload = json.loads(request.body)
    except ValueError:
        return JsonResponse({"error": "invalid JSON"}, status=400)
    updates = payload.get("updates", [payload]) if isinstance(payload, dict) else payload
    if not isinstance(updates, list) or not updates or len(updates) > MAX_UPDATES:
        return JsonResponse({"error": f"send 1-{MAX_UPDATES} updates"}, status=400)

    results = []
    for item in updates:
        try:
            if not isinstance(item, dict):
                raise ValueError("each update must be an object")
            sub_id = _int(item.get("subscription_id"), "subscription_id", required=True)
            # Only the fields sent are written, so one sender never wipes another's numbers.
            values = {f: _int(item[f], f) for f in STAT_FIELDS if f in item}
            if "countries" in item:
                values["countries"] = _countries(item["countries"])
            followers = values.get("followers")
            start = _int(item.get("start_followers"), "start_followers")
            day = parse_date(item["date"]) if item.get("date") else timezone.now().date()  # UTC, like Linksterr
            if day is None:
                raise ValueError("date must be YYYY-MM-DD")
        except (ValueError, TypeError) as exc:
            results.append({"subscription_id": item.get("subscription_id") if isinstance(item, dict) else None,
                            "ok": False, "error": str(exc)})
            continue
        with transaction.atomic():
            sub = AgencySubscription.objects.select_for_update().filter(pk=sub_id).first()
            if sub is None:
                results.append({"subscription_id": sub_id, "ok": False, "error": "unknown subscription"})
                continue
            SubscriptionStat.objects.update_or_create(subscription=sub, date=day, defaults=values)
            if start is not None:
                sub.start_followers = start
            elif sub.start_followers is None and followers is not None:
                sub.start_followers = followers
            latest = sub.stats.exclude(followers=None).order_by("-date").first()
            if latest is not None:
                sub.current_followers = latest.followers
            sub.stats_at = timezone.now()
            sub.save()
        results.append({"subscription_id": sub_id, "ok": True, "status": sub.status, "gained": sub.gained})
    return JsonResponse({"results": results}, status=200 if all(r["ok"] for r in results) else 207)

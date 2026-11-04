"""Machine API for the growth system. Authenticated with `Authorization: Bearer
<GROWTH_API_TOKEN>`; disabled while the token is unset.

GET  /growth/api/subscriptions/?status=active   accounts to grow (default: active)
POST /growth/api/stats/                         one day's numbers or {"updates": [...]}:
     {"subscription_id": 12, "date": "2026-11-04", "followers": 5120,
      "new_followers": 140, "start_followers": 4300}
     Only subscription_id is required; "date" defaults to today. The same
     subscription + date overwrites. new_followers is what we brought that day (left
     out: the change in the follower count); likes and comments are counted from it
     (× 2.5 and ÷ 10) unless sent. followers is the account's follower count that day. start_followers (the
     count when the package started) defaults to the first reading's followers.
"""
import hmac
import json

from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import AgencySubscription, SubscriptionStat

MAX_UPDATES = 500


def _authorized(request):
    token = settings.GROWTH_API_TOKEN
    given = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    return bool(token) and hmac.compare_digest(given.encode(), token.encode())


def _sub_json(s):
    return {"id": s.pk, "platform": s.platform, "handle": s.handle, "location": s.location, "status": s.status,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "current_period_end": s.current_period_end.isoformat() if s.current_period_end else None,
            "cancel_at_period_end": s.cancel_at_period_end, "start_followers": s.start_followers,
            "current_followers": s.current_followers}


@require_GET
def subscriptions(request):
    if not _authorized(request):
        return JsonResponse({"error": "unauthorized"}, status=401)
    status = request.GET.get("status", "active")
    qs = AgencySubscription.objects.filter(status__in=status.split(",")).order_by("started_at", "created_at")[:1000]
    return JsonResponse({"subscriptions": [_sub_json(s) for s in qs]})


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
            followers = _int(item.get("followers"), "followers")
            new_followers = _int(item.get("new_followers"), "new_followers")
            likes = _int(item.get("likes"), "likes")
            comments = _int(item.get("comments"), "comments")
            start = _int(item.get("start_followers"), "start_followers")
            day = parse_date(item["date"]) if item.get("date") else timezone.localdate()
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
            SubscriptionStat.objects.update_or_create(subscription=sub, date=day, defaults={
                "followers": followers, "new_followers": new_followers, "likes": likes, "comments": comments})
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

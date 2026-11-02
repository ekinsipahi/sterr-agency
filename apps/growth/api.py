"""Machine API for the delivery system. Authenticated with `Authorization: Bearer
<GROWTH_API_TOKEN>`; disabled while the token is unset.

GET  /growth/api/orders/?status=paid    orders to deliver (default: paid)
POST /growth/api/progress/              one reading or {"updates": [...]}:
     {"order_id": 12, "delivered": 840, "followers": 5120, "start_followers": 4300,
      "at": "2026-11-02T10:00:00Z", "completed": false}
     Only order_id and delivered are required. "at" defaults to now; the same
     order + at overwrites. delivered >= the package size (or completed: true)
     completes the order and emails the customer.
"""
import hmac
import json

from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import FollowerOrder, OrderProgress
from .notifications import confirm_completed

MAX_UPDATES = 500


def _authorized(request):
    token = settings.GROWTH_API_TOKEN
    given = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    return bool(token) and hmac.compare_digest(given.encode(), token.encode())


def _order_json(o):
    return {"id": o.pk, "platform": o.platform, "handle": o.handle, "location": o.location, "package": o.package,
            "followers": o.followers, "delivered": o.delivered, "status": o.status,
            "paid_at": o.paid_at.isoformat() if o.paid_at else None, "created_at": o.created_at.isoformat()}


@require_GET
def orders(request):
    if not _authorized(request):
        return JsonResponse({"error": "unauthorized"}, status=401)
    status = request.GET.get("status", "paid")
    qs = FollowerOrder.objects.filter(status__in=status.split(",")).order_by("paid_at", "created_at")[:1000]
    return JsonResponse({"orders": [_order_json(o) for o in qs]})


def _int(value, name, required=False):
    if value is None and not required:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


@csrf_exempt
@require_POST
def progress(request):
    if not _authorized(request):
        return JsonResponse({"error": "unauthorized"}, status=401)
    try:
        payload = json.loads(request.body)
    except ValueError:
        return JsonResponse({"error": "invalid JSON"}, status=400)
    updates = payload.get("updates", [payload]) if isinstance(payload, dict) else payload
    if not isinstance(updates, list) or not updates or len(updates) > MAX_UPDATES:
        return JsonResponse({"error": f"send 1-{MAX_UPDATES} updates"}, status=400)

    results, completed = [], []
    for item in updates:
        try:
            if not isinstance(item, dict):
                raise ValueError("each update must be an object")
            order_id = _int(item.get("order_id"), "order_id", required=True)
            delivered = _int(item.get("delivered"), "delivered", required=True)
            followers = _int(item.get("followers"), "followers")
            start = _int(item.get("start_followers"), "start_followers")
            at = parse_datetime(item["at"]) if item.get("at") else timezone.now()
            if at is None:
                raise ValueError("at must be an ISO 8601 datetime")
            if timezone.is_naive(at):
                at = timezone.make_aware(at, timezone.utc)
        except (ValueError, TypeError) as exc:
            results.append({"order_id": item.get("order_id") if isinstance(item, dict) else None, "ok": False, "error": str(exc)})
            continue
        with transaction.atomic():
            order = FollowerOrder.objects.select_for_update().filter(pk=order_id).first()
            if order is None:
                results.append({"order_id": order_id, "ok": False, "error": "unknown order"})
                continue
            OrderProgress.objects.update_or_create(order=order, at=at, defaults={"delivered": delivered, "followers": followers})
            latest = order.progress_at is None or at >= order.progress_at
            if latest:
                order.delivered, order.progress_at = delivered, at
                if followers is not None:
                    order.current_followers = followers
            if start is not None:
                order.start_followers = start
            if order.status == "paid" and (item.get("completed") is True or delivered >= order.followers):
                order.status, order.completed_at = "completed", timezone.now()
                completed.append(order)
            order.save()
        results.append({"order_id": order_id, "ok": True, "status": order.status, "delivered": order.delivered})
    for order in completed:
        confirm_completed(order)
    return JsonResponse({"results": results}, status=200 if all(r["ok"] for r in results) else 207)

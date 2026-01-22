import base64
from io import BytesIO

from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required, user_passes_test

import qrcode
from django_ratelimit.decorators import ratelimit

from .models import Question, AppSetting
from .forms import AskForm


def staff_required(view):
    return login_required(user_passes_test(lambda u: u.is_staff)(view))


@never_cache
def settings_json(request):
    s = AppSetting.get_solo()
    return JsonResponse({
        "event_title": s.event_title,
        "background_color": s.background_color,
        "title_color": s.title_color,
        "question_color": s.question_color,
        "name_color": s.name_color,
        "title_size": s.title_size,
        "question_size": s.question_size,
        "name_size": s.name_size,
        "qr_size": s.qr_size,
        "max_question_length": s.max_question_length,
        "submissions_enabled": s.submissions_enabled,
    })


@never_cache
def approved_questions_json(request):
    qs = (Question.objects
          .filter(status=Question.STATUS_APPROVED)
          .order_by("-created_at")
          .values("id", "name", "question", "created_at"))
    return JsonResponse({"approved": list(qs)})


@never_cache
@staff_required
def pending_questions_json(request):
    qs = (Question.objects
          .filter(status=Question.STATUS_PENDING)
          .order_by("-created_at")
          .values("id", "name", "question", "created_at"))
    return JsonResponse({"pending": list(qs)})


@never_cache
def screen_view(request):
    s = AppSetting.get_solo()
    ask_url = request.build_absolute_uri(reverse("ask"))

    # QR code points to /ask (absolute)
    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(ask_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buff = BytesIO()
    img.save(buff, format="PNG")
    qr_b64 = base64.b64encode(buff.getvalue()).decode("ascii")

    return render(request, "qa/screen.html", {
        "qr_data_uri": f"data:image/png;base64,{qr_b64}",
        "ask_url": ask_url,
        "s": s,
    })


@require_http_methods(["GET", "POST"])
@ratelimit(key="ip", rate="5/m", block=True)
def ask_view(request):
    s = AppSetting.get_solo()

    if request.method == "POST":
        form = AskForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.status = Question.STATUS_PENDING
            obj.save()
            return render(request, "qa/ask_success.html")
    else:
        form = AskForm()

    return render(request, "qa/ask.html", {
        "form": form,
        "submissions_enabled": s.submissions_enabled,
        "max_len": s.max_question_length,
    })


@never_cache
@staff_required
def moderation_view(request):
    # Main moderation tool (staff only)
    return render(request, "qa/moderation.html", {})


from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@require_http_methods(["POST"])
@staff_required
def moderation_action(request):
    """
    POST:
      action = approve | reject | delete
      ids = comma-separated list of question IDs
    """
    action = (request.POST.get("action") or "").strip()
    ids_raw = (request.POST.get("ids") or "").strip()

    if action not in {"approve", "reject", "delete"}:
        return HttpResponseBadRequest("Invalid action")

    if not ids_raw:
        return HttpResponseBadRequest("No ids")

    try:
        ids = [int(x) for x in ids_raw.split(",") if x.strip()]
    except ValueError:
        return HttpResponseBadRequest("Invalid ids")

    qs = Question.objects.filter(id__in=ids)

    if action == "approve":
        qs.update(status=Question.STATUS_APPROVED)
    elif action == "reject":
        qs.update(status=Question.STATUS_REJECTED)
    else:
        qs.delete()

    # 🔥 MANUAL REAL-TIME BROADCAST (THIS IS THE FIX)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "moderators",
        {"type": "broadcast.refresh", "reason": "moderation_action"},
    )
    async_to_sync(channel_layer.group_send)(
        "screens",
        {"type": "broadcast.refresh", "reason": "moderation_action"},
    )

    return JsonResponse({"ok": True})

from django.contrib import admin
from django.urls import path
from qa import views as qa_views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("screen/", qa_views.screen_view, name="screen"),
    path("ask/", qa_views.ask_view, name="ask"),

    # JSON endpoints (used by websocket-triggered refresh)
    path("screen/approved.json", qa_views.approved_questions_json, name="approved_questions_json"),
    path("moderation/pending.json", qa_views.pending_questions_json, name="pending_questions_json"),
    path("settings.json", qa_views.settings_json, name="settings_json"),

    # Main admin tool
    path("moderation/", qa_views.moderation_view, name="moderation"),
    path("moderation/action/", qa_views.moderation_action, name="moderation_action"),
]

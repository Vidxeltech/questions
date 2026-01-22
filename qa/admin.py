from django.contrib import admin
from .models import Question, AppSetting

@admin.action(description="Approve selected questions")
def approve_selected(modeladmin, request, queryset):
    queryset.update(status=Question.STATUS_APPROVED)

@admin.action(description="Reject selected questions")
def reject_selected(modeladmin, request, queryset):
    queryset.update(status=Question.STATUS_REJECTED)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status", "created_at", "question_preview")
    list_filter = ("status", "created_at")
    search_fields = ("name", "question")
    ordering = ("-created_at",)
    actions = [approve_selected, reject_selected]
    readonly_fields = ("created_at",)

    def question_preview(self, obj):
        s = obj.question
        return s if len(s) <= 80 else (s[:77] + "…")
    question_preview.short_description = "Question"

@admin.register(AppSetting)
class AppSettingAdmin(admin.ModelAdmin):
    list_display = ("event_title", "max_question_length", "submissions_enabled")

    def has_add_permission(self, request):
        return False

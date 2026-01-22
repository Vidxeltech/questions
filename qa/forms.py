from django import forms
from .models import Question, AppSetting

class AskForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["name", "question"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        settings = AppSetting.get_solo()
        max_len = settings.max_question_length

        self.fields["name"].required = False
        self.fields["name"].widget = forms.TextInput(attrs={
            "placeholder": "Your name (optional)",
            "autocomplete": "name",
            "class": "input",
        })

        self.fields["question"].required = True
        self.fields["question"].help_text = f"Max {max_len} characters."
        self.fields["question"].widget = forms.Textarea(attrs={
            "placeholder": "Type your question…",
            "rows": 4,
            "maxlength": str(max_len),
            "class": "textarea",
        })

    def clean_question(self):
        q = (self.cleaned_data.get("question") or "").strip()
        settings = AppSetting.get_solo()

        if not settings.submissions_enabled:
            raise forms.ValidationError("Submissions are currently disabled.")

        if len(q) == 0:
            raise forms.ValidationError("Question is required.")

        if len(q) > settings.max_question_length:
            raise forms.ValidationError(f"Question is too long (max {settings.max_question_length} characters).")

        return q

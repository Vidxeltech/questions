from django.db import models
from django.core.validators import MinValueValidator, RegexValidator

hex_color = RegexValidator(
    regex=r"^#([A-Fa-f0-9]{6})$",
    message="Enter a valid hex color like #FFFFFF",
)

class Question(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    name = models.CharField(max_length=120, blank=True, null=True)
    question = models.TextField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self):
        return f"[{self.status}] {self.question[:60]}"

class AppSetting(models.Model):
    # Singleton (enforced by pk=1)
    max_question_length = models.PositiveIntegerField(default=200, validators=[MinValueValidator(10)])
    submissions_enabled = models.BooleanField(default=True)

    # NEW: Event title + theme controls
    event_title = models.CharField(max_length=200, default="Live Questions")

    background_color = models.CharField(max_length=7, default="#FFFFFF", validators=[hex_color])
    title_color = models.CharField(max_length=7, default="#0A699A", validators=[hex_color])
    question_color = models.CharField(max_length=7, default="#111111", validators=[hex_color])
    name_color = models.CharField(max_length=7, default="#444444", validators=[hex_color])

    title_size = models.PositiveIntegerField(default=56, validators=[MinValueValidator(18)])     # px
    question_size = models.PositiveIntegerField(default=42, validators=[MinValueValidator(18)])  # px
    name_size = models.PositiveIntegerField(default=26, validators=[MinValueValidator(12)])      # px
    qr_size = models.PositiveIntegerField(default=180, validators=[MinValueValidator(100)])      # px

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                "max_question_length": 200,
                "submissions_enabled": True,
            },
        )
        return obj

    def __str__(self):
        return "App Settings (Singleton)"

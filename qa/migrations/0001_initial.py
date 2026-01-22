from django.db import migrations, models
import django.core.validators

class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AppSetting",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("max_question_length", models.PositiveIntegerField(default=200, validators=[django.core.validators.MinValueValidator(10)])),
                ("submissions_enabled", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(blank=True, max_length=120, null=True)),
                ("question", models.TextField()),
                ("status", models.CharField(choices=[("pending","Pending"),("approved","Approved"),("rejected","Rejected")], db_index=True, default="pending", max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                "indexes": [models.Index(fields=["status", "-created_at"], name="qa_question_status_created_idx")],
            },
        ),
    ]

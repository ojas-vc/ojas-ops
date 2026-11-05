# Generated for ProjectWorkspace on 2026-11-05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ojas_ops", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectWorkspace",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("tenant_id", models.CharField(db_index=True, default="default", max_length=64)),
                ("project_id", models.CharField(db_index=True, max_length=128, unique=True)),
                ("title", models.CharField(max_length=255)),
                ("pipeline_type", models.CharField(db_index=True, max_length=64)),
                ("ruleset", models.CharField(blank=True, default="", max_length=64)),
                ("status", models.CharField(db_index=True, default="IN_PROGRESS", max_length=32)),
                ("current_stage", models.CharField(blank=True, default="", max_length=64)),
                ("temporal_workflow_id", models.CharField(blank=True, db_index=True, default="", max_length=128)),
                ("completed_stages", models.JSONField(blank=True, default=list)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "abstract": False,
                "indexes": [
                    models.Index(fields=["tenant_id", "status"], name="ojas_ops_pw_tenant_status_idx"),
                    models.Index(fields=["tenant_id", "-created_at"], name="ojas_ops_pw_tenant_created_idx"),
                    models.Index(fields=["tenant_id", "pipeline_type"], name="ojas_ops_pw_tenant_pipe_idx"),
                ],
            },
        ),
    ]


"""Serializers for ProjectWorkspace operational model."""

from rest_framework import serializers

from ojas_ops.models.project_workspace import ProjectWorkspace


class ProjectWorkspaceSerializer(serializers.ModelSerializer):
    """Full serializer for ProjectWorkspace instances."""

    class Meta:
        model = ProjectWorkspace
        fields = [
            "id",
            "tenant_id",
            "project_id",
            "title",
            "pipeline_type",
            "ruleset",
            "status",
            "current_stage",
            "temporal_workflow_id",
            "completed_stages",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProjectWorkspaceCreateSerializer(serializers.ModelSerializer):
    """Serializer for initializing a new ProjectWorkspace."""

    class Meta:
        model = ProjectWorkspace
        fields = [
            "tenant_id",
            "project_id",
            "title",
            "pipeline_type",
            "ruleset",
            "metadata",
        ]


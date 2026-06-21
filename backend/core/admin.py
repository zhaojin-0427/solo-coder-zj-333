from django.contrib import admin
from .models import Topic, ProgramExcerpt, Version, Comment, FollowUpItem


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color", "icon", "created_at")
    search_fields = ("name",)


@admin.register(ProgramExcerpt)
class ProgramExcerptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "date",
        "program_name",
        "time_slot",
        "topic",
        "is_duplicate",
        "created_by",
        "created_at",
    )
    list_filter = ("date", "topic", "is_duplicate", "created_by")
    search_fields = ("program_name", "content_summary", "elderly_notes")
    raw_id_fields = ("topic", "duplicate_of", "created_by")


@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ("id", "excerpt", "created_by", "created_at", "merge_note")
    list_filter = ("created_at", "created_by")
    search_fields = ("content", "merge_note")
    raw_id_fields = ("excerpt", "created_by")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "excerpt", "user", "created_at")
    list_filter = ("created_at", "user")
    search_fields = ("content",)
    raw_id_fields = ("excerpt", "user")


@admin.register(FollowUpItem)
class FollowUpItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "status",
        "priority",
        "excerpt",
        "assigned_to",
        "due_date",
        "created_at",
    )
    list_filter = ("status", "priority", "due_date", "assigned_to")
    search_fields = ("title", "description")
    raw_id_fields = ("excerpt", "assigned_to")

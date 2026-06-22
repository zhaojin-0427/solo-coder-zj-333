from django.contrib import admin
from .models import (
    Topic, ProgramExcerpt, Version, Comment, FollowUpItem,
    ReviewPackage, ReviewPackageItem, ReviewPackageFeedback,
    CompanionPlan, CompanionPlanMaterial,
    ListeningSchedule, ListeningRecord, ListeningExcerptDraft
)


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
        "source_type",
        "excerpt",
        "assigned_to",
        "due_date",
        "created_at",
    )
    list_filter = ("status", "priority", "source_type", "due_date", "assigned_to")
    search_fields = ("title", "description")
    raw_id_fields = ("excerpt", "review_package_item", "assigned_to")


@admin.register(ReviewPackage)
class ReviewPackageAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_by", "family_group", "created_at", "updated_at")
    list_filter = ("created_at", "family_group", "created_by")
    search_fields = ("title", "purpose_description", "guide_text")
    raw_id_fields = ("created_by", "family_group")


@admin.register(ReviewPackageItem)
class ReviewPackageItemAdmin(admin.ModelAdmin):
    list_display = ("id", "review_package", "excerpt", "order_index", "is_highlighted", "created_at")
    list_filter = ("is_highlighted", "created_at")
    search_fields = ("family_reminder",)
    raw_id_fields = ("review_package", "excerpt")


@admin.register(ReviewPackageFeedback)
class ReviewPackageFeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "package_item", "elderly_user", "feedback_type", "created_at")
    list_filter = ("feedback_type", "created_at")
    search_fields = ("note",)
    raw_id_fields = ("package_item", "elderly_user")


@admin.register(CompanionPlan)
class CompanionPlanAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "handle_location", "created_by", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "handle_location")
    raw_id_fields = ("source_excerpt", "source_topic", "companion_user", "created_by", "family_group")


@admin.register(CompanionPlanMaterial)
class CompanionPlanMaterialAdmin(admin.ModelAdmin):
    list_display = ("id", "companion_plan", "name", "is_prepared", "order_index")
    list_filter = ("is_prepared",)
    search_fields = ("name", "description")
    raw_id_fields = ("companion_plan", "prepared_by")


@admin.register(ListeningSchedule)
class ListeningScheduleAdmin(admin.ModelAdmin):
    list_display = ("id", "program_name", "repeat_cycle", "broadcast_time", "channel_source", "is_active", "created_by", "created_at")
    list_filter = ("repeat_cycle", "is_active", "created_at")
    search_fields = ("program_name", "channel_source", "remark")
    raw_id_fields = ("created_by", "family_group")


@admin.register(ListeningRecord)
class ListeningRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "schedule", "listen_date", "status", "listener", "created_at")
    list_filter = ("status", "listen_date")
    search_fields = ("note",)
    raw_id_fields = ("schedule", "listener", "excerpt_draft")


@admin.register(ListeningExcerptDraft)
class ListeningExcerptDraftAdmin(admin.ModelAdmin):
    list_display = ("id", "program_name", "listen_date", "is_completed", "created_by", "created_at")
    list_filter = ("is_completed", "created_at")
    search_fields = ("program_name", "content_summary", "elderly_notes")
    raw_id_fields = ("schedule", "topic", "created_by", "excerpt")

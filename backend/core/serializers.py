from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import (
    Topic, ProgramExcerpt, Version, Comment, FollowUpItem,
    ReviewPackage, ReviewPackageItem, ReviewPackageFeedback
)


class TopicSerializer(serializers.ModelSerializer):
    excerpt_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Topic
        fields = (
            "id",
            "name",
            "color",
            "icon",
            "description",
            "excerpt_count",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "excerpt_count")

    def get_excerpt_count(self, obj):
        return obj.excerpts.filter(is_duplicate=False).count()


class VersionSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Version
        fields = (
            "id",
            "content",
            "created_by",
            "created_at",
            "merge_note",
        )
        read_only_fields = ("id", "created_at", "created_by")


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "user",
            "content",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "user")


class ProgramExcerptDetailSerializer(serializers.ModelSerializer):
    topic = TopicSerializer(read_only=True)
    topic_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    created_by = UserSerializer(read_only=True)
    duplicate_of = serializers.PrimaryKeyRelatedField(
        queryset=ProgramExcerpt.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )
    versions = VersionSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    topic_name = serializers.SerializerMethodField(read_only=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)
    confirmed_by = UserSerializer(read_only=True)
    confirmed_by_name = serializers.SerializerMethodField(read_only=True)
    confirmation_status_display = serializers.CharField(source="get_confirmation_status_display", read_only=True)

    class Meta:
        model = ProgramExcerpt
        fields = (
            "id",
            "date",
            "program_name",
            "time_slot",
            "content_summary",
            "elderly_notes",
            "topic",
            "topic_id",
            "topic_name",
            "is_duplicate",
            "duplicate_of",
            "created_by",
            "created_by_name",
            "confirmation_status",
            "confirmation_status_display",
            "confirmed_by",
            "confirmed_by_name",
            "confirmed_at",
            "confirmation_note",
            "versions",
            "comments",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "versions", "comments", "confirmation_status", "confirmed_by", "confirmed_at", "confirmation_note")

    def get_topic_name(self, obj):
        return obj.topic.name if obj.topic else None

    def get_created_by_name(self, obj):
        return obj.created_by.first_name or obj.created_by.username

    def get_confirmed_by_name(self, obj):
        if obj.confirmed_by:
            return obj.confirmed_by.first_name or obj.confirmed_by.username
        return None


class ProgramExcerptListSerializer(serializers.ModelSerializer):
    topic = TopicSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    comment_count = serializers.SerializerMethodField(read_only=True)
    topic_name = serializers.SerializerMethodField(read_only=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)
    confirmed_by_name = serializers.SerializerMethodField(read_only=True)
    confirmation_status_display = serializers.CharField(source="get_confirmation_status_display", read_only=True)

    class Meta:
        model = ProgramExcerpt
        fields = (
            "id",
            "date",
            "program_name",
            "time_slot",
            "content_summary",
            "elderly_notes",
            "topic",
            "topic_name",
            "is_duplicate",
            "created_by",
            "created_by_name",
            "confirmation_status",
            "confirmation_status_display",
            "confirmed_by_name",
            "confirmed_at",
            "confirmation_note",
            "comment_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "created_by")

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_topic_name(self, obj):
        return obj.topic.name if obj.topic else None

    def get_created_by_name(self, obj):
        return obj.created_by.first_name or obj.created_by.username

    def get_confirmed_by_name(self, obj):
        if obj.confirmed_by:
            return obj.confirmed_by.first_name or obj.confirmed_by.username
        return None


class ReviewPackageItemSerializer(serializers.ModelSerializer):
    excerpt = ProgramExcerptListSerializer(read_only=True)
    excerpt_id = serializers.IntegerField(write_only=True)
    feedback_type = serializers.SerializerMethodField(read_only=True)
    feedback_count = serializers.SerializerMethodField(read_only=True)
    latest_feedback = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ReviewPackageItem
        fields = (
            "id",
            "excerpt",
            "excerpt_id",
            "order_index",
            "is_highlighted",
            "family_reminder",
            "feedback_type",
            "feedback_count",
            "latest_feedback",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "excerpt", "feedback_type", "feedback_count", "latest_feedback")

    def get_feedback_type(self, obj):
        request = self.context.get("request")
        if request and request.user.role == "elderly":
            feedback = obj.feedbacks.filter(elderly_user=request.user).order_by("-created_at").first()
            return feedback.feedback_type if feedback else None
        return None

    def get_feedback_count(self, obj):
        return obj.feedbacks.count()

    def get_latest_feedback(self, obj):
        feedback = obj.feedbacks.order_by("-created_at").first()
        if feedback:
            return {
                "id": feedback.id,
                "feedback_type": feedback.feedback_type,
                "feedback_type_display": feedback.get_feedback_type_display(),
                "note": feedback.note,
                "elderly_user_name": feedback.elderly_user.first_name or feedback.elderly_user.username,
                "created_at": feedback.created_at,
            }
        return None


class ReviewPackageListSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)
    item_count = serializers.SerializerMethodField(read_only=True)
    feedback_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ReviewPackage
        fields = (
            "id",
            "title",
            "purpose_description",
            "guide_text",
            "created_by",
            "created_by_name",
            "item_count",
            "feedback_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "item_count", "feedback_count")

    def get_created_by_name(self, obj):
        return obj.created_by.first_name or obj.created_by.username

    def get_item_count(self, obj):
        return obj.items.count()

    def get_feedback_count(self, obj):
        return ReviewPackageFeedback.objects.filter(
            package_item__review_package=obj
        ).count()


class ReviewPackageDetailSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)
    items = ReviewPackageItemSerializer(many=True, read_only=True)

    class Meta:
        model = ReviewPackage
        fields = (
            "id",
            "title",
            "purpose_description",
            "guide_text",
            "created_by",
            "created_by_name",
            "items",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "items")

    def get_created_by_name(self, obj):
        return obj.created_by.first_name or obj.created_by.username


class ReviewPackageCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    purpose_description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    guide_text = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    excerpt_ids = serializers.ListField(child=serializers.IntegerField())
    items_config = serializers.DictField(required=False, allow_empty=True, default=None)


class ReviewPackageUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200, required=False)
    purpose_description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    guide_text = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    excerpt_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    items_config = serializers.DictField(required=False, allow_empty=True, default=None)


class ReorderItemsSerializer(serializers.Serializer):
    ordered_item_ids = serializers.ListField(child=serializers.IntegerField())


class UpdateItemConfigSerializer(serializers.Serializer):
    is_highlighted = serializers.BooleanField(required=False)
    family_reminder = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class SubmitFeedbackSerializer(serializers.Serializer):
    feedback_type = serializers.ChoiceField(choices=["read", "review_again", "needs_explanation"])
    note = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class ReviewPackageFeedbackSerializer(serializers.ModelSerializer):
    package_item = ReviewPackageItemSerializer(read_only=True)
    elderly_user = UserSerializer(read_only=True)
    elderly_user_name = serializers.SerializerMethodField(read_only=True)
    feedback_type_display = serializers.CharField(source="get_feedback_type_display", read_only=True)

    class Meta:
        model = ReviewPackageFeedback
        fields = (
            "id",
            "package_item",
            "elderly_user",
            "elderly_user_name",
            "feedback_type",
            "feedback_type_display",
            "note",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "package_item", "elderly_user")

    def get_elderly_user_name(self, obj):
        return obj.elderly_user.first_name or obj.elderly_user.username


class FollowUpItemSerializer(serializers.ModelSerializer):
    excerpt = ProgramExcerptListSerializer(read_only=True)
    excerpt_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    review_package_item = ReviewPackageItemSerializer(read_only=True)
    review_package_item_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    source_type_display = serializers.CharField(source="get_source_type_display", read_only=True)
    assigned_to_name = serializers.SerializerMethodField(read_only=True)
    review_package = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FollowUpItem
        fields = (
            "id",
            "title",
            "description",
            "status",
            "status_display",
            "priority",
            "priority_display",
            "source_type",
            "source_type_display",
            "excerpt",
            "excerpt_id",
            "review_package_item",
            "review_package_item_id",
            "review_package",
            "assigned_to",
            "assigned_to_id",
            "assigned_to_name",
            "due_date",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "excerpt", "review_package_item", "review_package", "assigned_to", "source_type")

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.first_name or obj.assigned_to.username
        return None

    def get_review_package(self, obj):
        if obj.review_package_item:
            package = obj.review_package_item.review_package
            return {
                "id": package.id,
                "title": package.title,
            }
        return None


class MergeDuplicateSerializer(serializers.Serializer):
    duplicate_id = serializers.IntegerField()
    merge_note = serializers.CharField(required=False, allow_blank=True)


class ConfirmExcerptSerializer(serializers.Serializer):
    confirmation_status = serializers.ChoiceField(choices=["confirmed", "needs_verification"])
    confirmation_note = serializers.CharField(required=False, allow_blank=True)
    generate_followup = serializers.BooleanField(required=False, default=False)

from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import (
    Topic, ProgramExcerpt, Version, Comment, FollowUpItem,
    ReviewPackage, ReviewPackageItem, ReviewPackageFeedback,
    CompanionPlan, CompanionPlanMaterial
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


class MergeDuplicateSerializer(serializers.Serializer):
    duplicate_id = serializers.IntegerField()
    merge_note = serializers.CharField(required=False, allow_blank=True)


class ConfirmExcerptSerializer(serializers.Serializer):
    confirmation_status = serializers.ChoiceField(choices=["confirmed", "needs_verification"])
    confirmation_note = serializers.CharField(required=False, allow_blank=True)
    generate_followup = serializers.BooleanField(required=False, default=False)


class CompanionPlanMaterialSerializer(serializers.ModelSerializer):
    prepared_by = UserSerializer(read_only=True)
    prepared_by_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    prepared_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CompanionPlanMaterial
        fields = (
            "id",
            "name",
            "description",
            "is_prepared",
            "prepared_by",
            "prepared_by_id",
            "prepared_by_name",
            "prepared_at",
            "order_index",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "prepared_by", "prepared_at")

    def get_prepared_by_name(self, obj):
        if obj.prepared_by:
            return obj.prepared_by.first_name or obj.prepared_by.username
        return None


class CompanionPlanMaterialCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    order_index = serializers.IntegerField(required=False, default=0)


class CompanionPlanListSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)
    companion_user = UserSerializer(read_only=True)
    companion_user_name = serializers.SerializerMethodField(read_only=True)
    source_excerpt = ProgramExcerptListSerializer(read_only=True)
    source_topic = TopicSerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    source_type_display = serializers.CharField(source="get_source_type_display", read_only=True)
    transportation_display = serializers.SerializerMethodField(read_only=True)
    material_count = serializers.SerializerMethodField(read_only=True)
    prepared_material_count = serializers.SerializerMethodField(read_only=True)
    material_prepared_rate = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CompanionPlan
        fields = (
            "id",
            "title",
            "source_type",
            "source_type_display",
            "source_excerpt",
            "source_topic",
            "source_excerpt_content",
            "handle_location",
            "handle_time_start",
            "handle_time_end",
            "handle_time_note",
            "transportation",
            "transportation_display",
            "transportation_note",
            "companion_user",
            "companion_user_name",
            "elderly_notes",
            "elderly_concerns",
            "status",
            "status_display",
            "materials_confirmed",
            "time_location_known",
            "needs_companion",
            "created_by",
            "created_by_name",
            "material_count",
            "prepared_material_count",
            "material_prepared_rate",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "materials_confirmed", "time_location_known", "needs_companion")

    def get_created_by_name(self, obj):
        return obj.created_by.first_name or obj.created_by.username

    def get_companion_user_name(self, obj):
        if obj.companion_user:
            return obj.companion_user.first_name or obj.companion_user.username
        return None

    def get_transportation_display(self, obj):
        if obj.transportation:
            return obj.get_transportation_display()
        return None

    def get_material_count(self, obj):
        return obj.materials.count()

    def get_prepared_material_count(self, obj):
        return obj.materials.filter(is_prepared=True).count()

    def get_material_prepared_rate(self, obj):
        total = obj.materials.count()
        if total == 0:
            return 0
        prepared = obj.materials.filter(is_prepared=True).count()
        return round(prepared / total, 2)


class CompanionPlanDetailSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)
    companion_user = UserSerializer(read_only=True)
    companion_user_name = serializers.SerializerMethodField(read_only=True)
    companion_user_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    source_excerpt = ProgramExcerptListSerializer(read_only=True)
    source_excerpt_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    source_topic = TopicSerializer(read_only=True)
    source_topic_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    source_type_display = serializers.CharField(source="get_source_type_display", read_only=True)
    transportation_display = serializers.SerializerMethodField(read_only=True)
    materials = CompanionPlanMaterialSerializer(many=True, read_only=True)
    material_count = serializers.SerializerMethodField(read_only=True)
    prepared_material_count = serializers.SerializerMethodField(read_only=True)
    material_prepared_rate = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CompanionPlan
        fields = (
            "id",
            "title",
            "source_type",
            "source_type_display",
            "source_excerpt",
            "source_excerpt_id",
            "source_topic",
            "source_topic_id",
            "source_excerpt_content",
            "handle_location",
            "handle_time_start",
            "handle_time_end",
            "handle_time_note",
            "transportation",
            "transportation_display",
            "transportation_note",
            "companion_user",
            "companion_user_id",
            "companion_user_name",
            "elderly_notes",
            "elderly_concerns",
            "status",
            "status_display",
            "materials_confirmed",
            "time_location_known",
            "needs_companion",
            "created_by",
            "created_by_name",
            "materials",
            "material_count",
            "prepared_material_count",
            "material_prepared_rate",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "materials")

    def get_created_by_name(self, obj):
        return obj.created_by.first_name or obj.created_by.username

    def get_companion_user_name(self, obj):
        if obj.companion_user:
            return obj.companion_user.first_name or obj.companion_user.username
        return None

    def get_transportation_display(self, obj):
        if obj.transportation:
            return obj.get_transportation_display()
        return None

    def get_material_count(self, obj):
        return obj.materials.count()

    def get_prepared_material_count(self, obj):
        return obj.materials.filter(is_prepared=True).count()

    def get_material_prepared_rate(self, obj):
        total = obj.materials.count()
        if total == 0:
            return 0
        prepared = obj.materials.filter(is_prepared=True).count()
        return round(prepared / total, 2)


class CompanionPlanCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    source_type = serializers.ChoiceField(choices=["excerpt", "topic", "manual"], required=False, default="manual")
    source_excerpt_id = serializers.IntegerField(required=False, allow_null=True, default=None)
    source_topic_id = serializers.IntegerField(required=False, allow_null=True, default=None)
    source_excerpt_content = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    handle_location = serializers.CharField(max_length=300)
    handle_time_start = serializers.DateField(required=False, allow_null=True)
    handle_time_end = serializers.DateField(required=False, allow_null=True)
    handle_time_note = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    transportation = serializers.ChoiceField(
        choices=["walk", "bus", "subway", "taxi", "private_car", "community_shuttle", "other"],
        required=False, allow_null=True
    )
    transportation_note = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    companion_user_id = serializers.IntegerField(required=False, allow_null=True, default=None)
    elderly_notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    materials = serializers.ListField(
        child=CompanionPlanMaterialCreateSerializer(),
        required=False,
        default=list
    )
    status = serializers.ChoiceField(
        choices=["pending", "preparing", "scheduled", "completed", "cancelled"],
        required=False, default="pending"
    )


class CompanionPlanUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200, required=False)
    source_type = serializers.ChoiceField(choices=["excerpt", "topic", "manual"], required=False)
    source_excerpt_id = serializers.IntegerField(required=False, allow_null=True)
    source_topic_id = serializers.IntegerField(required=False, allow_null=True)
    source_excerpt_content = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    handle_location = serializers.CharField(max_length=300, required=False)
    handle_time_start = serializers.DateField(required=False, allow_null=True)
    handle_time_end = serializers.DateField(required=False, allow_null=True)
    handle_time_note = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    transportation = serializers.ChoiceField(
        choices=["walk", "bus", "subway", "taxi", "private_car", "community_shuttle", "other"],
        required=False, allow_null=True
    )
    transportation_note = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    companion_user_id = serializers.IntegerField(required=False, allow_null=True)
    elderly_notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    elderly_concerns = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    status = serializers.ChoiceField(
        choices=["pending", "preparing", "scheduled", "completed", "cancelled"],
        required=False
    )
    materials_confirmed = serializers.BooleanField(required=False)
    time_location_known = serializers.BooleanField(required=False)
    needs_companion = serializers.BooleanField(required=False)
    materials = serializers.ListField(
        child=CompanionPlanMaterialCreateSerializer(),
        required=False
    )


class ElderlyCheckInSerializer(serializers.Serializer):
    materials_confirmed = serializers.BooleanField(required=False)
    time_location_known = serializers.BooleanField(required=False)
    needs_companion = serializers.BooleanField(required=False)
    elderly_concerns = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    material_ids = serializers.ListField(child=serializers.IntegerField(), required=False, default=list)


class UpdateMaterialStatusSerializer(serializers.Serializer):
    is_prepared = serializers.BooleanField()


class FollowUpItemSerializer(serializers.ModelSerializer):
    excerpt = ProgramExcerptListSerializer(read_only=True)
    excerpt_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    review_package_item = ReviewPackageItemSerializer(read_only=True)
    review_package_item_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    companion_plan = CompanionPlanListSerializer(read_only=True)
    companion_plan_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
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
            "companion_plan",
            "companion_plan_id",
            "review_package",
            "assigned_to",
            "assigned_to_id",
            "assigned_to_name",
            "due_date",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "excerpt", "review_package_item", "companion_plan", "review_package", "assigned_to", "source_type")

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

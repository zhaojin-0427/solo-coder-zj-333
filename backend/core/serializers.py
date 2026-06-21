from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Topic, ProgramExcerpt, Version, Comment, FollowUpItem


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
            "versions",
            "comments",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "versions", "comments")

    def get_topic_name(self, obj):
        return obj.topic.name if obj.topic else None

    def get_created_by_name(self, obj):
        return obj.created_by.first_name or obj.created_by.username


class ProgramExcerptListSerializer(serializers.ModelSerializer):
    topic = TopicSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    comment_count = serializers.SerializerMethodField(read_only=True)
    topic_name = serializers.SerializerMethodField(read_only=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)

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


class FollowUpItemSerializer(serializers.ModelSerializer):
    excerpt = ProgramExcerptListSerializer(read_only=True)
    excerpt_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    assigned_to_name = serializers.SerializerMethodField(read_only=True)

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
            "excerpt",
            "excerpt_id",
            "assigned_to",
            "assigned_to_id",
            "assigned_to_name",
            "due_date",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "excerpt", "assigned_to")

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.first_name or obj.assigned_to.username
        return None


class MergeDuplicateSerializer(serializers.Serializer):
    duplicate_id = serializers.IntegerField()
    merge_note = serializers.CharField(required=False, allow_blank=True)

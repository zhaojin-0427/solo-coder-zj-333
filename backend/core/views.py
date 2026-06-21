from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from django.shortcuts import get_object_or_404

from accounts.serializers import UserSerializer
from accounts.models import User

from .models import Topic, ProgramExcerpt, Comment, FollowUpItem
from .serializers import (
    TopicSerializer,
    ProgramExcerptListSerializer,
    ProgramExcerptDetailSerializer,
    VersionSerializer,
    CommentSerializer,
    FollowUpItemSerializer,
    MergeDuplicateSerializer,
)
from .services import StatisticsService, ProgramExcerptService


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return super().get_permissions()


class ProgramExcerptViewSet(viewsets.ModelViewSet):
    queryset = ProgramExcerpt.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "delete"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            if self.action == "retrieve":
                return ProgramExcerptDetailSerializer
            return ProgramExcerptListSerializer
        return ProgramExcerptDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        family_group_id = self.request.user.family_group_id
        if family_group_id:
            queryset = queryset.filter(created_by__family_group_id=family_group_id)

        topic_id = self.request.query_params.get("topic_id")
        if topic_id:
            queryset = queryset.filter(topic_id=topic_id)

        date = self.request.query_params.get("date")
        if date:
            queryset = queryset.filter(date=date)

        include_duplicates = self.request.query_params.get("include_duplicates", "false").lower() == "true"
        if not include_duplicates:
            queryset = queryset.filter(is_duplicate=False)

        return queryset.order_by("-date", "-created_at")

    def perform_create(self, serializer):
        topic_id = serializer.validated_data.get("topic_id")
        if topic_id:
            topic = get_object_or_404(Topic, id=topic_id)
            serializer.save(created_by=self.request.user, topic=topic)
        else:
            serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        topic_id = serializer.validated_data.get("topic_id")
        if topic_id:
            topic = get_object_or_404(Topic, id=topic_id)
            serializer.save(topic=topic)
        else:
            serializer.save()

    @action(detail=True, methods=["get"])
    def versions(self, request, pk=None):
        excerpt = self.get_object()
        versions = excerpt.versions.all()
        serializer = VersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def merge(self, request, pk=None):
        main_excerpt = self.get_object()
        serializer = MergeDuplicateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        duplicate_id = serializer.validated_data["duplicate_id"]
        merge_note = serializer.validated_data.get("merge_note", "")

        try:
            result = ProgramExcerptService.merge_duplicates(
                main_excerpt_id=main_excerpt.id,
                duplicate_excerpt_id=duplicate_id,
                merge_note=merge_note,
                user=request.user
            )
            return Response(
                ProgramExcerptDetailSerializer(result).data,
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["get", "post"], url_path="comments")
    def comments_list(self, request, pk=None):
        excerpt = self.get_object()
        if request.method == "GET":
            comments = excerpt.comments.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        elif request.method == "POST":
            serializer = CommentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(excerpt=excerpt, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post"]

    def get_queryset(self):
        queryset = super().get_queryset()
        family_group_id = self.request.user.family_group_id
        if family_group_id:
            queryset = queryset.filter(excerpt__created_by__family_group_id=family_group_id)
        return queryset

    def perform_create(self, serializer):
        excerpt_id = self.request.data.get("excerpt_id")
        excerpt = get_object_or_404(ProgramExcerpt, id=excerpt_id)
        serializer.save(excerpt=excerpt, user=self.request.user)


class FollowUpItemViewSet(viewsets.ModelViewSet):
    queryset = FollowUpItem.objects.all()
    serializer_class = FollowUpItemSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put"]

    def get_queryset(self):
        queryset = super().get_queryset()
        family_group_id = self.request.user.family_group_id
        if family_group_id:
            queryset = queryset.filter(
                Q(assigned_to__family_group_id=family_group_id) |
                Q(excerpt__created_by__family_group_id=family_group_id)
            )

        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def perform_create(self, serializer):
        excerpt_id = serializer.validated_data.get("excerpt_id")
        assigned_to_id = serializer.validated_data.get("assigned_to_id")

        kwargs = {}
        if excerpt_id:
            kwargs["excerpt"] = get_object_or_404(ProgramExcerpt, id=excerpt_id)
        if assigned_to_id:
            kwargs["assigned_to"] = get_object_or_404(User, id=assigned_to_id)

        serializer.save(**kwargs)

    def perform_update(self, serializer):
        excerpt_id = serializer.validated_data.get("excerpt_id")
        assigned_to_id = serializer.validated_data.get("assigned_to_id")

        kwargs = {}
        if excerpt_id:
            kwargs["excerpt"] = get_object_or_404(ProgramExcerpt, id=excerpt_id)
        if assigned_to_id:
            kwargs["assigned_to"] = get_object_or_404(User, id=assigned_to_id)

        serializer.save(**kwargs)


class FamilyMembersView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        family_group_id = request.user.family_group_id
        if not family_group_id:
            return Response([])

        members = User.objects.filter(family_group_id=family_group_id)
        serializer = UserSerializer(members, many=True)
        return Response(serializer.data)


class FamilyFeedView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        family_group_id = request.user.family_group_id
        if not family_group_id:
            return Response([])

        excerpts = ProgramExcerpt.objects.filter(
            created_by__family_group_id=family_group_id,
            is_duplicate=False
        ).order_by("-date", "-created_at")[:50]

        result = []
        for excerpt in excerpts:
            item = {
                "type": "excerpt",
                "data": ProgramExcerptListSerializer(excerpt).data,
            }
            result.append(item)

        return Response(result)


class StatisticsView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        family_group_id = request.user.family_group_id
        stats = StatisticsService.get_statistics(family_group_id=family_group_id)
        return Response(stats)

from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from django.shortcuts import get_object_or_404

from accounts.serializers import UserSerializer
from accounts.models import User

from .models import (
    Topic, ProgramExcerpt, Comment, FollowUpItem,
    ReviewPackage, ReviewPackageItem, ReviewPackageFeedback
)
from .serializers import (
    TopicSerializer,
    ProgramExcerptListSerializer,
    ProgramExcerptDetailSerializer,
    VersionSerializer,
    CommentSerializer,
    FollowUpItemSerializer,
    MergeDuplicateSerializer,
    ConfirmExcerptSerializer,
    ReviewPackageListSerializer,
    ReviewPackageDetailSerializer,
    ReviewPackageCreateSerializer,
    ReviewPackageUpdateSerializer,
    ReorderItemsSerializer,
    UpdateItemConfigSerializer,
    SubmitFeedbackSerializer,
    ReviewPackageFeedbackSerializer,
    ReviewPackageItemSerializer,
)
from .services import (
    StatisticsService, ProgramExcerptService, ConfirmationService,
    ReviewPackageService
)


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

        confirmation_status = self.request.query_params.get("confirmation_status")
        if confirmation_status:
            queryset = queryset.filter(confirmation_status=confirmation_status)

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

    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm(self, request, pk=None):
        excerpt = self.get_object()
        serializer = ConfirmExcerptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated_excerpt, follow_up_item = ConfirmationService.confirm_excerpt(
                excerpt_id=excerpt.id,
                user=request.user,
                confirmation_status=serializer.validated_data["confirmation_status"],
                confirmation_note=serializer.validated_data.get("confirmation_note", ""),
                generate_followup=serializer.validated_data.get("generate_followup", False),
            )
            result = ProgramExcerptDetailSerializer(updated_excerpt).data
            if follow_up_item:
                result["generated_followup"] = FollowUpItemSerializer(follow_up_item).data
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


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
                Q(excerpt__created_by__family_group_id=family_group_id) |
                Q(review_package_item__review_package__family_group_id=family_group_id)
            )

        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def perform_create(self, serializer):
        excerpt_id = serializer.validated_data.get("excerpt_id")
        assigned_to_id = serializer.validated_data.get("assigned_to_id")
        review_package_item_id = serializer.validated_data.get("review_package_item_id")

        kwargs = {}
        if excerpt_id:
            kwargs["excerpt"] = get_object_or_404(ProgramExcerpt, id=excerpt_id)
        if assigned_to_id:
            kwargs["assigned_to"] = get_object_or_404(User, id=assigned_to_id)
        if review_package_item_id:
            kwargs["review_package_item"] = get_object_or_404(ReviewPackageItem, id=review_package_item_id)

        serializer.save(**kwargs)

    def perform_update(self, serializer):
        excerpt_id = serializer.validated_data.get("excerpt_id")
        assigned_to_id = serializer.validated_data.get("assigned_to_id")
        review_package_item_id = serializer.validated_data.get("review_package_item_id")

        kwargs = {}
        if excerpt_id:
            kwargs["excerpt"] = get_object_or_404(ProgramExcerpt, id=excerpt_id)
        if assigned_to_id:
            kwargs["assigned_to"] = get_object_or_404(User, id=assigned_to_id)
        if review_package_item_id:
            kwargs["review_package_item"] = get_object_or_404(ReviewPackageItem, id=review_package_item_id)

        serializer.save(**kwargs)


class ReviewPackageViewSet(viewsets.ModelViewSet):
    queryset = ReviewPackage.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "delete"]

    def get_serializer_class(self):
        if self.action == "list":
            return ReviewPackageListSerializer
        elif self.action in ["retrieve", "create", "update", "partial_update"]:
            return ReviewPackageDetailSerializer
        return ReviewPackageDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        family_group_id = self.request.user.family_group_id
        if family_group_id:
            queryset = queryset.filter(family_group_id=family_group_id)
        return queryset.order_by("-created_at")

    def create(self, request, *args, **kwargs):
        serializer = ReviewPackageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            package = ReviewPackageService.create_package(
                user=request.user,
                title=serializer.validated_data["title"],
                excerpt_ids=serializer.validated_data["excerpt_ids"],
                purpose_description=serializer.validated_data.get("purpose_description"),
                guide_text=serializer.validated_data.get("guide_text"),
                items_config=serializer.validated_data.get("items_config"),
            )
            detail_serializer = ReviewPackageDetailSerializer(
                package, context={"request": request}
            )
            return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        package = self.get_object()
        serializer = ReviewPackageUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            package = ReviewPackageService.update_package(
                package=package,
                user=request.user,
                title=serializer.validated_data.get("title"),
                purpose_description=serializer.validated_data.get("purpose_description"),
                guide_text=serializer.validated_data.get("guide_text"),
                excerpt_ids=serializer.validated_data.get("excerpt_ids"),
                items_config=serializer.validated_data.get("items_config"),
            )
            detail_serializer = ReviewPackageDetailSerializer(
                package, context={"request": request}
            )
            return Response(detail_serializer.data)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["post"], url_path="reorder-items")
    def reorder_items(self, request, pk=None):
        package = self.get_object()
        serializer = ReorderItemsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            items = ReviewPackageService.reorder_items(
                package=package,
                ordered_item_ids=serializer.validated_data["ordered_item_ids"],
            )
            item_serializer = ReviewPackageItemSerializer(
                items, many=True, context={"request": request}
            )
            return Response(item_serializer.data)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["get", "post"], url_path="feedbacks")
    def feedbacks_list(self, request, pk=None):
        package = self.get_object()
        if request.method == "GET":
            feedbacks = ReviewPackageFeedback.objects.filter(
                package_item__review_package=package
            ).order_by("-created_at")
            serializer = ReviewPackageFeedbackSerializer(feedbacks, many=True)
            return Response(serializer.data)


class ReviewPackageItemViewSet(viewsets.ModelViewSet):
    queryset = ReviewPackageItem.objects.all()
    serializer_class = ReviewPackageItemSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "put", "post", "patch", "delete"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        family_group_id = self.request.user.family_group_id
        if family_group_id:
            queryset = queryset.filter(review_package__family_group_id=family_group_id)

        package_id = self.request.query_params.get("package_id")
        if package_id:
            queryset = queryset.filter(review_package_id=package_id)

        return queryset

    @action(detail=True, methods=["post"], url_path="update-config")
    def update_config(self, request, pk=None):
        item = self.get_object()
        serializer = UpdateItemConfigSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            item = ReviewPackageService.update_item_config(
                package_item=item,
                is_highlighted=serializer.validated_data.get("is_highlighted"),
                family_reminder=serializer.validated_data.get("family_reminder"),
            )
            item_serializer = ReviewPackageItemSerializer(
                item, context={"request": request}
            )
            return Response(item_serializer.data)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["post"], url_path="submit-feedback")
    def submit_feedback(self, request, pk=None):
        item = self.get_object()
        serializer = SubmitFeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            feedback, follow_up_item = ReviewPackageService.submit_feedback(
                package_item=item,
                elderly_user=request.user,
                feedback_type=serializer.validated_data["feedback_type"],
                note=serializer.validated_data.get("note", ""),
            )
            result = ReviewPackageFeedbackSerializer(feedback).data
            if follow_up_item:
                result["generated_followup"] = FollowUpItemSerializer(follow_up_item).data
            return Response(result, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


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

        result = []

        excerpts = ProgramExcerpt.objects.filter(
            created_by__family_group_id=family_group_id,
            is_duplicate=False
        ).order_by("-created_at")[:30]

        for excerpt in excerpts:
            item = {
                "type": "excerpt",
                "data": ProgramExcerptListSerializer(excerpt).data,
                "created_at": excerpt.created_at,
            }
            if excerpt.confirmation_status != "pending" and excerpt.confirmed_by:
                item["confirmation_info"] = {
                    "confirmed_by_name": excerpt.confirmed_by.first_name or excerpt.confirmed_by.username,
                    "confirmed_at": excerpt.confirmed_at,
                    "confirmation_note": excerpt.confirmation_note or "",
                    "confirmation_status": excerpt.confirmation_status,
                    "confirmation_status_display": excerpt.get_confirmation_status_display(),
                }
            result.append(item)

        packages = ReviewPackage.objects.filter(
            family_group_id=family_group_id
        ).order_by("-created_at")[:20]

        for package in packages:
            result.append({
                "type": "review_package",
                "data": ReviewPackageListSerializer(package).data,
                "created_at": package.created_at,
            })

        feedbacks = ReviewPackageFeedback.objects.filter(
            package_item__review_package__family_group_id=family_group_id
        ).order_by("-created_at")[:30]

        for feedback in feedbacks:
            package = feedback.package_item.review_package
            result.append({
                "type": "review_package_feedback",
                "data": {
                    "id": feedback.id,
                    "feedback_type": feedback.feedback_type,
                    "feedback_type_display": feedback.get_feedback_type_display(),
                    "note": feedback.note,
                    "elderly_user_name": feedback.elderly_user.first_name or feedback.elderly_user.username,
                    "elderly_user_avatar": feedback.elderly_user.avatar,
                    "package_id": package.id,
                    "package_title": package.title,
                    "package_item_id": feedback.package_item.id,
                    "excerpt_program_name": feedback.package_item.excerpt.program_name,
                    "excerpt_content_summary": feedback.package_item.excerpt.content_summary,
                },
                "created_at": feedback.created_at,
            })

        result.sort(key=lambda x: x["created_at"], reverse=True)

        return Response(result[:50])


class StatisticsView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        family_group_id = request.user.family_group_id
        stats = StatisticsService.get_statistics(family_group_id=family_group_id)
        return Response(stats)

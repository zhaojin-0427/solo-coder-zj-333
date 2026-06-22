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
    ReviewPackage, ReviewPackageItem, ReviewPackageFeedback,
    CompanionPlan, CompanionPlanMaterial,
    ListeningSchedule, ListeningRecord, ListeningExcerptDraft
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
    CompanionPlanListSerializer,
    CompanionPlanDetailSerializer,
    CompanionPlanCreateSerializer,
    CompanionPlanUpdateSerializer,
    CompanionPlanMaterialSerializer,
    ElderlyCheckInSerializer,
    UpdateMaterialStatusSerializer,
    ListeningScheduleListSerializer,
    ListeningScheduleDetailSerializer,
    ListeningScheduleCreateSerializer,
    ListeningScheduleUpdateSerializer,
    ListeningRecordSerializer,
    UpdateListeningRecordStatusSerializer,
    ListeningExcerptDraftSerializer,
    UpdateDraftSerializer,
    ConsecutiveMissedItemSerializer,
)
from .services import (
    StatisticsService, ProgramExcerptService, ConfirmationService,
    ReviewPackageService, CompanionPlanService, ListeningScheduleService
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
                Q(review_package_item__review_package__family_group_id=family_group_id) |
                Q(companion_plan__family_group_id=family_group_id) |
                Q(listening_schedule__family_group_id=family_group_id) |
                Q(listening_record__schedule__family_group_id=family_group_id)
            )

        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def perform_create(self, serializer):
        excerpt_id = serializer.validated_data.get("excerpt_id")
        assigned_to_id = serializer.validated_data.get("assigned_to_id")
        review_package_item_id = serializer.validated_data.get("review_package_item_id")
        companion_plan_id = serializer.validated_data.get("companion_plan_id")
        listening_schedule_id = serializer.validated_data.get("listening_schedule_id")
        listening_record_id = serializer.validated_data.get("listening_record_id")

        kwargs = {}
        if excerpt_id:
            kwargs["excerpt"] = get_object_or_404(ProgramExcerpt, id=excerpt_id)
        if assigned_to_id:
            kwargs["assigned_to"] = get_object_or_404(User, id=assigned_to_id)
        if review_package_item_id:
            kwargs["review_package_item"] = get_object_or_404(ReviewPackageItem, id=review_package_item_id)
        if companion_plan_id:
            kwargs["companion_plan"] = get_object_or_404(CompanionPlan, id=companion_plan_id)
        if listening_schedule_id:
            kwargs["listening_schedule"] = get_object_or_404(ListeningSchedule, id=listening_schedule_id)
        if listening_record_id:
            kwargs["listening_record"] = get_object_or_404(ListeningRecord, id=listening_record_id)

        serializer.save(**kwargs)

    def perform_update(self, serializer):
        excerpt_id = serializer.validated_data.get("excerpt_id")
        assigned_to_id = serializer.validated_data.get("assigned_to_id")
        review_package_item_id = serializer.validated_data.get("review_package_item_id")
        companion_plan_id = serializer.validated_data.get("companion_plan_id")
        listening_schedule_id = serializer.validated_data.get("listening_schedule_id")
        listening_record_id = serializer.validated_data.get("listening_record_id")

        kwargs = {}
        if excerpt_id:
            kwargs["excerpt"] = get_object_or_404(ProgramExcerpt, id=excerpt_id)
        if assigned_to_id:
            kwargs["assigned_to"] = get_object_or_404(User, id=assigned_to_id)
        if review_package_item_id:
            kwargs["review_package_item"] = get_object_or_404(ReviewPackageItem, id=review_package_item_id)
        if companion_plan_id:
            kwargs["companion_plan"] = get_object_or_404(CompanionPlan, id=companion_plan_id)
        if listening_schedule_id:
            kwargs["listening_schedule"] = get_object_or_404(ListeningSchedule, id=listening_schedule_id)
        if listening_record_id:
            kwargs["listening_record"] = get_object_or_404(ListeningRecord, id=listening_record_id)

        serializer.save(**kwargs)


class CompanionPlanViewSet(viewsets.ModelViewSet):
    queryset = CompanionPlan.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "delete"]

    def get_serializer_class(self):
        if self.action == "list":
            return CompanionPlanListSerializer
        return CompanionPlanDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        family_group_id = self.request.user.family_group_id
        if family_group_id:
            queryset = queryset.filter(family_group_id=family_group_id)

        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by("-handle_time_start", "-created_at")

    def create(self, request, *args, **kwargs):
        serializer = CompanionPlanCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            plan = CompanionPlanService.create_plan(
                user=request.user,
                title=serializer.validated_data["title"],
                handle_location=serializer.validated_data["handle_location"],
                source_type=serializer.validated_data.get("source_type", "manual"),
                source_excerpt_id=serializer.validated_data.get("source_excerpt_id"),
                source_topic_id=serializer.validated_data.get("source_topic_id"),
                source_excerpt_content=serializer.validated_data.get("source_excerpt_content"),
                handle_time_start=serializer.validated_data.get("handle_time_start"),
                handle_time_end=serializer.validated_data.get("handle_time_end"),
                handle_time_note=serializer.validated_data.get("handle_time_note"),
                transportation=serializer.validated_data.get("transportation"),
                transportation_note=serializer.validated_data.get("transportation_note"),
                companion_user_id=serializer.validated_data.get("companion_user_id"),
                elderly_notes=serializer.validated_data.get("elderly_notes"),
                materials=serializer.validated_data.get("materials", []),
                status=serializer.validated_data.get("status", "pending"),
            )
            detail_serializer = CompanionPlanDetailSerializer(plan)
            return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        plan = self.get_object()
        serializer = CompanionPlanUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            plan = CompanionPlanService.update_plan(
                plan=plan,
                user=request.user,
                **serializer.validated_data
            )
            detail_serializer = CompanionPlanDetailSerializer(plan)
            return Response(detail_serializer.data)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["post"], url_path="elderly-checkin")
    def elderly_checkin(self, request, pk=None):
        plan = self.get_object()
        serializer = ElderlyCheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            plan, follow_up_item = CompanionPlanService.elderly_checkin(
                plan=plan,
                elderly_user=request.user,
                materials_confirmed=serializer.validated_data.get("materials_confirmed"),
                time_location_known=serializer.validated_data.get("time_location_known"),
                needs_companion=serializer.validated_data.get("needs_companion"),
                elderly_concerns=serializer.validated_data.get("elderly_concerns"),
                material_ids=serializer.validated_data.get("material_ids", []),
            )
            result = CompanionPlanDetailSerializer(plan).data
            if follow_up_item:
                result["generated_followup"] = FollowUpItemSerializer(follow_up_item).data
            return Response(result)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CompanionPlanMaterialViewSet(viewsets.ModelViewSet):
    queryset = CompanionPlanMaterial.objects.all()
    serializer_class = CompanionPlanMaterialSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "patch", "delete"]

    def get_queryset(self):
        queryset = super().get_queryset()
        family_group_id = self.request.user.family_group_id
        if family_group_id:
            queryset = queryset.filter(companion_plan__family_group_id=family_group_id)

        plan_id = self.request.query_params.get("plan_id")
        if plan_id:
            queryset = queryset.filter(companion_plan_id=plan_id)

        return queryset

    def perform_create(self, serializer):
        plan_id = self.request.data.get("companion_plan_id")
        plan = get_object_or_404(CompanionPlan, id=plan_id)
        serializer.save(companion_plan=plan)

    @action(detail=True, methods=["post"], url_path="update-status")
    def update_status(self, request, pk=None):
        material = self.get_object()
        serializer = UpdateMaterialStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            material, follow_up_item = CompanionPlanService.update_material_status(
                material=material,
                user=request.user,
                is_prepared=serializer.validated_data["is_prepared"],
            )
            result = CompanionPlanMaterialSerializer(material).data
            if follow_up_item:
                result["generated_followup"] = FollowUpItemSerializer(follow_up_item).data
            return Response(result)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


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

        companion_plans = CompanionPlan.objects.filter(
            family_group_id=family_group_id
        ).order_by("-created_at")[:20]

        for plan in companion_plans:
            item = {
                "type": "companion_plan",
                "data": CompanionPlanListSerializer(plan).data,
                "created_at": plan.created_at,
            }
            if plan.status != "pending" or plan.materials_confirmed or plan.time_location_known or plan.needs_companion:
                item["activity_info"] = {
                    "status": plan.status,
                    "status_display": plan.get_status_display(),
                    "materials_confirmed": plan.materials_confirmed,
                    "time_location_known": plan.time_location_known,
                    "needs_companion": plan.needs_companion,
                    "updated_at": plan.updated_at,
                }
            result.append(item)

        listening_schedules = ListeningSchedule.objects.filter(
            family_group_id=family_group_id
        ).order_by("-created_at")[:20]

        for schedule in listening_schedules:
            result.append({
                "type": "listening_schedule",
                "data": ListeningScheduleListSerializer(schedule).data,
                "created_at": schedule.created_at,
            })

        listening_records = ListeningRecord.objects.filter(
            schedule__family_group_id=family_group_id
        ).exclude(status="pending").order_by("-status_updated_at", "-created_at")[:30]

        for record in listening_records:
            sort_time = record.status_updated_at or record.created_at
            result.append({
                "type": "listening_record",
                "data": ListeningRecordSerializer(record).data,
                "created_at": sort_time,
            })

        excerpt_drafts = ListeningExcerptDraft.objects.filter(
            schedule__family_group_id=family_group_id
        ).order_by("-created_at")[:20]

        for draft in excerpt_drafts:
            result.append({
                "type": "listening_draft",
                "data": ListeningExcerptDraftSerializer(draft).data,
                "created_at": draft.created_at,
            })

        result.sort(key=lambda x: x["created_at"], reverse=True)

        return Response(result[:80])


class StatisticsView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        family_group_id = request.user.family_group_id
        stats = StatisticsService.get_statistics(family_group_id=family_group_id)
        return Response(stats)


class ListeningScheduleViewSet(viewsets.ModelViewSet):
    queryset = ListeningSchedule.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "delete"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ListeningScheduleListSerializer
        return ListeningScheduleDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        family_group_id = self.request.user.family_group_id
        if family_group_id:
            queryset = queryset.filter(family_group_id=family_group_id)

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=(is_active.lower() == "true"))

        return queryset.order_by("-created_at")

    def create(self, request, *args, **kwargs):
        serializer = ListeningScheduleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            schedule = ListeningScheduleService.create_schedule(
                user=request.user,
                program_name=serializer.validated_data["program_name"],
                start_date=serializer.validated_data["start_date"],
                broadcast_time=serializer.validated_data["broadcast_time"],
                channel_source=serializer.validated_data["channel_source"],
                end_date=serializer.validated_data.get("end_date"),
                repeat_cycle=serializer.validated_data.get("repeat_cycle", "once"),
                repeat_weekdays=serializer.validated_data.get("repeat_weekdays"),
                reminder_advance_minutes=serializer.validated_data.get("reminder_advance_minutes", 0),
                suitable_listener_ids=serializer.validated_data.get("suitable_listener_ids", []),
                remark=serializer.validated_data.get("remark"),
                is_active=serializer.validated_data.get("is_active", True),
            )
            detail_serializer = ListeningScheduleDetailSerializer(schedule)
            return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        schedule = self.get_object()
        serializer = ListeningScheduleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            schedule = ListeningScheduleService.update_schedule(
                schedule=schedule,
                user=request.user,
                **serializer.validated_data
            )
            detail_serializer = ListeningScheduleDetailSerializer(schedule)
            return Response(detail_serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ListeningRecordViewSet(viewsets.ModelViewSet):
    queryset = ListeningRecord.objects.all()
    serializer_class = ListeningRecordSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put"]

    def get_queryset(self):
        queryset = super().get_queryset()
        family_group_id = self.request.user.family_group_id
        if family_group_id:
            queryset = queryset.filter(schedule__family_group_id=family_group_id)

        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        listener_id = self.request.query_params.get("listener_id")
        if listener_id:
            queryset = queryset.filter(listener_id=listener_id)

        return queryset.order_by("-listen_date", "-created_at")

    @action(detail=False, methods=["get"], url_path="range")
    def get_range(self, request):
        from django.utils import timezone
        family_group_id = request.user.family_group_id
        if not family_group_id:
            return Response([])

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        listener_id = request.query_params.get("listener_id")

        today = timezone.now().date()
        if not start_date:
            start_date = (today - timezone.timedelta(days=today.weekday())).isoformat()
        if not end_date:
            end_date = (today + timezone.timedelta(days=6 - today.weekday())).isoformat()

        from datetime import date
        s = date.fromisoformat(start_date)
        e = date.fromisoformat(end_date)
        lid = int(listener_id) if listener_id else None

        records = ListeningScheduleService.get_records_for_range(
            family_group_id, s, e, lid
        )
        serializer = ListeningRecordSerializer(records, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="today")
    def get_today(self, request):
        from django.utils import timezone
        family_group_id = request.user.family_group_id
        if not family_group_id:
            return Response([])

        today = timezone.now().date()
        listener_id = request.query_params.get("listener_id")
        lid = int(listener_id) if listener_id else None

        records = ListeningScheduleService.get_records_for_range(
            family_group_id, today, today, lid
        )
        serializer = ListeningRecordSerializer(records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="update-status")
    def update_status(self, request, pk=None):
        record = self.get_object()
        serializer = UpdateListeningRecordStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            record, excerpt_draft, follow_up_item = ListeningScheduleService.update_record_status(
                record=record,
                elderly_user=request.user,
                new_status=serializer.validated_data["status"],
                note=serializer.validated_data.get("note"),
                generate_excerpt=serializer.validated_data.get("generate_excerpt", True),
            )
            result = ListeningRecordSerializer(record).data
            if excerpt_draft:
                result["generated_excerpt_draft"] = ListeningExcerptDraftSerializer(excerpt_draft).data
            if follow_up_item:
                result["generated_followup"] = FollowUpItemSerializer(follow_up_item).data
            return Response(result)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ListeningExcerptDraftViewSet(viewsets.ModelViewSet):
    queryset = ListeningExcerptDraft.objects.all()
    serializer_class = ListeningExcerptDraftSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put"]

    def get_queryset(self):
        queryset = super().get_queryset()
        family_group_id = self.request.user.family_group_id
        if family_group_id:
            queryset = queryset.filter(schedule__family_group_id=family_group_id)

        is_completed = self.request.query_params.get("is_completed")
        if is_completed is not None:
            queryset = queryset.filter(is_completed=(is_completed.lower() == "true"))

        return queryset.order_by("-created_at")

    def update(self, request, *args, **kwargs):
        draft = self.get_object()
        serializer = UpdateDraftSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            draft = ListeningScheduleService.update_draft(
                draft=draft,
                user=request.user,
                content_summary=serializer.validated_data.get("content_summary"),
                elderly_notes=serializer.validated_data.get("elderly_notes"),
                topic_id=serializer.validated_data.get("topic_id"),
            )
            return Response(ListeningExcerptDraftSerializer(draft).data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="convert")
    def convert_to_excerpt(self, request, pk=None):
        draft = self.get_object()
        try:
            excerpt = ListeningScheduleService.convert_draft_to_excerpt(draft, request.user)
            result = ListeningExcerptDraftSerializer(draft).data
            result["converted_excerpt"] = ProgramExcerptDetailSerializer(excerpt).data
            return Response(result)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ConsecutiveMissedView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        family_group_id = request.user.family_group_id
        if not family_group_id:
            return Response([])

        min_streak = int(request.query_params.get("min_streak", 3))
        items = ListeningScheduleService.get_consecutive_missed_list(
            family_group_id, min_streak=min_streak
        )
        serializer = ConsecutiveMissedItemSerializer(items, many=True)
        return Response(serializer.data)

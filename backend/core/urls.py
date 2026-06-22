from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TopicViewSet,
    ProgramExcerptViewSet,
    CommentViewSet,
    FollowUpItemViewSet,
    ReviewPackageViewSet,
    ReviewPackageItemViewSet,
    CompanionPlanViewSet,
    CompanionPlanMaterialViewSet,
    ListeningScheduleViewSet,
    ListeningRecordViewSet,
    ListeningExcerptDraftViewSet,
    FamilyMembersView,
    FamilyFeedView,
    StatisticsView,
    ConsecutiveMissedView,
)

router = DefaultRouter()
router.register(r"topics", TopicViewSet, basename="topic")
router.register(r"excerpts", ProgramExcerptViewSet, basename="excerpt")
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"followups", FollowUpItemViewSet, basename="followup")
router.register(r"review-packages", ReviewPackageViewSet, basename="review-package")
router.register(r"review-package-items", ReviewPackageItemViewSet, basename="review-package-item")
router.register(r"companion-plans", CompanionPlanViewSet, basename="companion-plan")
router.register(r"companion-plan-materials", CompanionPlanMaterialViewSet, basename="companion-plan-material")
router.register(r"listening-schedules", ListeningScheduleViewSet, basename="listening-schedule")
router.register(r"listening-records", ListeningRecordViewSet, basename="listening-record")
router.register(r"listening-drafts", ListeningExcerptDraftViewSet, basename="listening-draft")

urlpatterns = [
    path("", include(router.urls)),
    path("family/members/", FamilyMembersView.as_view(), name="family-members"),
    path("family/feed/", FamilyFeedView.as_view(), name="family-feed"),
    path("statistics/", StatisticsView.as_view(), name="statistics"),
    path("listening/consecutive-missed/", ConsecutiveMissedView.as_view(), name="consecutive-missed"),
]

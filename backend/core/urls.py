from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TopicViewSet,
    ProgramExcerptViewSet,
    CommentViewSet,
    FollowUpItemViewSet,
    FamilyMembersView,
    FamilyFeedView,
    StatisticsView,
)

router = DefaultRouter()
router.register(r"topics", TopicViewSet, basename="topic")
router.register(r"excerpts", ProgramExcerptViewSet, basename="excerpt")
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"followups", FollowUpItemViewSet, basename="followup")

urlpatterns = [
    path("", include(router.urls)),
    path("family/members/", FamilyMembersView.as_view(), name="family-members"),
    path("family/feed/", FamilyFeedView.as_view(), name="family-feed"),
    path("statistics/", StatisticsView.as_view(), name="statistics"),
]

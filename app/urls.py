from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app.community.viewsets import CommunityPostViewSets
from app.course.viewsets import CourseViewSets
from app.chat.viewsets import ChatThreadViewSet, ChatMessageViewSet
# from app.schedule.viewsets import ScheduleViewSet, AvailabilityViewSet
from app.tutee.viewsets import TuteeViewset
from app.tutor.viewsets import TutorViewset
from app.video_conference.viewsets import VideoConference
from app.views import SearchBar
from app.user.viewsets import OTPViewSet, UserViewSet

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()

router.register(r"user", UserViewSet, basename="user")
router.register(r"user-otp", OTPViewSet, basename="user-otp")
router.register(r"tutor", TutorViewset, basename="tutor")
router.register(r"tutee", TuteeViewset, basename="tutee")
router.register(r"course", CourseViewSets, basename="course")
router.register(r"user-conversations", ChatThreadViewSet, basename="chat")
router.register(r"chat-messages", ChatMessageViewSet, basename="chat-thread")
# router.register(r"schedule", ScheduleViewSet, basename="schedule-view")
# router.register(r"availability", AvailabilityViewSet, basename="availability-view")
router.register(r"community", CommunityPostViewSets, basename="community")
router.register(r"video", VideoConference, basename="video-app")

# router.register(r"course", ModuleViewSets, basename="module")

urlpatterns = [
    path("", include(router.urls)),
    path('search/', SearchBar.as_view()),
    path('token/access/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]

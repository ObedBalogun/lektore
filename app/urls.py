from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app.course.viewsets import CourseViewSets
from app.chat.viewsets import ChatThreadViewSet, ChatMessageViewSet
from app.schedule.viewsets import ScheduleViewSet, AvailabilityViewSet
from app.tutor.viewsets import TutorViewset
from app.views import SearchBar
from app.user.viewsets import OTPViewSet, UserViewSet

router = DefaultRouter()

router.register(r"user", UserViewSet, basename="user")
router.register(r"user-otp", OTPViewSet, basename="user-otp")
router.register(r"tutor", TutorViewset, basename="tutor")
router.register(r"course", CourseViewSets, basename="course")
router.register(r"user-conversations", ChatThreadViewSet, basename="chat")
router.register(r"chat-messages", ChatMessageViewSet, basename="chat-thread")
router.register(r"schedule", ScheduleViewSet, basename="schedule-view")
router.register(r"availability", AvailabilityViewSet, basename="availability-view")


# router.register(r"course", ModuleViewSets, basename="module")

urlpatterns = [
    path("", include(router.urls)),
    path('search/', SearchBar.as_view()),


]

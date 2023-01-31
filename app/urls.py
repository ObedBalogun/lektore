from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app.course.viewsets import CourseViewSets
from app.chat.viewsets import ChatThreadViewSet, ChatMessageViewSet
from app.schedule.viewsets import ScheduleViewSet, AvailabilityViewSet
from app.views import UserRegistrationAPIView, UserLogin, UserLogout, SearchBar
from app.viewsets import OTPViewSet

router = DefaultRouter()

# Email Verification Endpoint
router.register(r"user-otp", OTPViewSet, basename="user-otp")
router.register(r"course", CourseViewSets, basename="course")
router.register(r"user-conversations", ChatThreadViewSet, basename="chat")
router.register(r"chat-messages", ChatMessageViewSet, basename="chat-thread")
router.register(r"schedule", ScheduleViewSet, basename="schedule-view")
router.register(r"availability", AvailabilityViewSet, basename="availability-view")


# router.register(r"course", ModuleViewSets, basename="module")

urlpatterns = [
    path("", include(router.urls)),
    path('tutor/', include('app.tutor.urls')),
    path('register-user/', UserRegistrationAPIView.as_view()),
    path('user-login/', UserLogin.as_view()),
    path('user-logout/', UserLogout.as_view()),
    path('search/', SearchBar.as_view()),


]

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app.Course.viewsets import CourseViewSets
from app.chat.viewsets import ChatThreadViewSet, ChatMessageViewSet
from app.views import UserRegistrationAPIView, UserLogin, UserLogout, SearchBar
from app.viewsets import OTPViewSet

router = DefaultRouter()

# Email Verification Endpoint
router.register(r"user-otp", OTPViewSet, basename="user-otp")
router.register(r"course", CourseViewSets, basename="course")
router.register(r"user-conversations", ChatThreadViewSet, basename="chat")
router.register(r"chat-messages", ChatMessageViewSet)


# router.register(r"course", ModuleViewSets, basename="module")

urlpatterns = [
    path("", include(router.urls)),
    path('tutor/', include('app.Tutor.urls')),
    path('register-user/', UserRegistrationAPIView.as_view()),
    path('user-login/', UserLogin.as_view()),
    path('user-logout/', UserLogout.as_view()),
    path('search/', SearchBar.as_view()),


]

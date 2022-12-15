from django.urls import path, include

from app.Tutor.views import TutorProfileView

urlpatterns = [
    path('', TutorProfileView.as_view()),
]
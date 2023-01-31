from django.urls import path, include

from app.tutor.views import TutorProfileView

urlpatterns = [
    path('', TutorProfileView.as_view()),
]
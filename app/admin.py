from django.contrib import admin

# Register your models here.
from app.Course.models import Course
from app.Tutee.models import TuteeProfile
from app.Tutor.models import TutorProfile
from app.chat.models import ChatThread, ChatMessage
from app.submodels import UserVerificationModel


class TutorProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TutorProfile._meta.fields]
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name", "phone_number",
                     "nationality")


class TuteeProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TuteeProfile._meta.fields]
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name", "phone_number",
                     "nationality")


class UserVerificationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserVerificationModel._meta.fields]


class CourseAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Course._meta.fields]


admin.site.register(ChatThread)
admin.site.register(ChatMessage)
admin.site.register(TutorProfile, TutorProfileAdmin)
admin.site.register(TuteeProfile, TuteeProfileAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(UserVerificationModel, UserVerificationAdmin)

from django.contrib import admin

# Register your models here.
from app.Tutor.models import TutorProfile


class TutorProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TutorProfile._meta.fields]
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name", "phone_number",
                     "nationality")


admin.site.register(TutorProfile, TutorProfileAdmin)

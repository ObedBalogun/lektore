import contextlib
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib import admin
from django.apps import apps
from django.db import models



class ListAdminMixin:
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]

        self.search_fields = [
            field.name
            for field in model._meta.fields
            if isinstance(field, (models.CharField, models.TextField))
        ]

        super().__init__(model, admin_site)

app_models = apps.get_models()


class CustomAdminSite(AdminSite):
    site_header = 'Lektore Dashboard'
    site_title = 'Lektore Admin'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with contextlib.suppress(admin.sites.AlreadyRegistered):
            for model in app_models:
                admin_class = type(
                    f"{model.__name__}Admin",
                    (ListAdminMixin, admin.ModelAdmin),
                    {},
                )
                self.register(model, admin_class)



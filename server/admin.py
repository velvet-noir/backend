from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Application,
    ApplicationServer,
    Server,
    ServerSpecification,
)


class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "image", "price", "is_active")
    ordering = ("id",)


class ServiceSpecificationAdmin(admin.ModelAdmin):
    list_display = ("get_service_name", "processor", "ram", "disk", "internet_speed")
    ordering = ("id",)

    def get_service_name(self, obj):
        return f"Характеристика: {obj.server.name}"

    get_service_name.short_description = "Server"


class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "get_status_name",
        "created_at",
        "updated_at",
        "user_creator",
        "user_moderator",
    )
    ordering = ("created_at",)

    def get_status_name(self, obj):
        return obj.get_status_display()

    get_status_name.short_description = "Status"


class ApplicationServerAdmin(admin.ModelAdmin):
    list_display = ("id", "application", "get_service_name")

    def get_service_name(self, obj):
        return f"Характеристика: {obj.server.name}"


admin.site.register(Server, ServiceAdmin)
admin.site.register(ServerSpecification, ServiceSpecificationAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(ApplicationServer, ApplicationServerAdmin)

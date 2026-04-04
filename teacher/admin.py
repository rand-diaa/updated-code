from django.contrib import admin

from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "email", "status")
    list_filter = ("status",)
    search_fields = ("user__username", "user__first_name", "user__last_name")

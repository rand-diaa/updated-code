from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "id", "user", "email", "academic_year")
    search_fields = ("student_id", "user__username", "user__first_name", "user__last_name")
    list_filter = ("academic_year",)

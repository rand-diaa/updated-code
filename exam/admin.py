from django.contrib import admin

from .models import Course, Question, Result, StudentExamAnswer


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "course_name", "academic_year")
    search_fields = ("course_name",)
    list_filter = ("academic_year",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "course", "marks", "question", "answer")
    list_filter = ("course",)
    search_fields = ("question",)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "exam", "bundle", "marks", "date")
    list_filter = ("exam", "date")


@admin.register(StudentExamAnswer)
class StudentExamAnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "bundle", "question", "is_correct", "submitted_at")
    list_filter = ("is_correct", "bundle")

from django.urls import path
from admin_panel import views

urlpatterns = [
    path('adminclick', views.adminclick_view),
    path('adminlogin', views.admin_login_view, name='adminlogin'),
    path('admin-dashboard', views.admin_dashboard_view,name='admin-dashboard'),
    path('admin-teacher', views.admin_teacher_view,name='admin-teacher'),
    path('admin-view-teacher', views.admin_view_teacher_view,name='admin-view-teacher'),
    path('delete-teacher/<int:pk>', views.delete_teacher_view,name='delete-teacher'),
    path('admin-view-pending-teacher', views.admin_view_pending_teacher_view,name='admin-view-pending-teacher'),
    path('approve-teacher/<int:pk>', views.approve_teacher_view,name='approve-teacher'),
    path('reject-teacher/<int:pk>', views.reject_teacher_view,name='reject-teacher'),

    path('admin-student', views.admin_student_view,name='admin-student'),
    path('admin-view-student', views.admin_view_student_view,name='admin-view-student'),
    path('admin-view-student-marks', views.admin_view_student_marks_view,name='admin-view-student-marks'),
    path('admin-view-marks/<int:pk>', views.admin_view_marks_view,name='admin-view-marks'),
    path('admin-check-marks/<int:pk>', views.admin_check_marks_view,name='admin-check-marks'),
    path('delete-student/<int:pk>', views.delete_student_view,name='delete-student'),

    path('admin-exam', views.admin_exam_view,name='admin-exam'),
    path('admin-manage-exam', views.admin_manage_exam_view,name='admin-manage-exam'),
    path(
        'admin-exam-bundle-results/<int:pk>',
        views.admin_exam_bundle_results_view,
        name='admin-exam-bundle-results',
    ),
    path('set-exam-schedule/<int:pk>', views.admin_set_exam_schedule_view, name='set-exam-schedule'),
    path('clear-exam-schedule/<int:pk>', views.admin_clear_exam_schedule_view, name='clear-exam-schedule'),
    path(
        'end-scheduled-exam-session/<int:pk>',
        views.admin_end_scheduled_exam_session_view,
        name='end-scheduled-exam-session',
    ),
    path('start-exam/<int:pk>', views.admin_start_exam_view,name='start-exam'),
    path('stop-exam/<int:pk>', views.admin_stop_exam_view,name='stop-exam'),
    path('admin-view-pending-bundle', views.admin_view_pending_bundle_view,name='admin-view-pending-bundle'),
    path('admin-view-bundle-questions/<int:pk>', views.admin_view_bundle_questions_view,name='admin-view-bundle-questions'),
    path('approve-bundle/<int:pk>', views.approve_bundle_view,name='approve-bundle'),
    path('reject-bundle/<int:pk>', views.reject_bundle_view,name='reject-bundle'),

    path('admin-question', views.admin_question_view,name='admin-question'),
    path('admin-view-question', views.admin_view_question_view,name='admin-view-question'),
    path('delete-question/<int:pk>', views.delete_question_view,name='delete-question'),
]




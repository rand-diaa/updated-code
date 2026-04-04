from django.urls import path
from student import views
from django.contrib.auth.views import LoginView

urlpatterns = [
path('studentclick', views.studentclick_view),
path('studentlogin', LoginView.as_view(template_name='student/studentlogin.html'),name='studentlogin'),
path('studentsignup', views.student_signup_view,name='studentsignup'),
path('student-dashboard', views.student_dashboard_view,name='student-dashboard'),
path('student-courses', views.student_courses_view, name='student-courses'),
path('course/<int:course_id>', views.student_course_detail_view, name='student-course-detail'),
path('student-exam', views.student_grades_view, name='student-exam'),  # kept URL, now shows grades
path('student-grades', views.student_grades_view, name='student-grades'),
path('student-profile', views.student_profile_view, name='student-profile'),
path('student-start-exam/<int:pk>', views.student_start_exam_view,name='student-start-exam'),
path('submit-exam/<int:pk>', views.student_submit_exam_view, name='student-submit-exam'),
]
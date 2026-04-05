from django.urls import path,include
from django.contrib import admin
from exam import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Django admin (always available)
    path('teacher/',include('teacher.urls')),
    path('student/',include('student.urls')),
    path('',include('admin_panel.urls')),  # Admin panel URLs
    
    path('',views.home_view,name=''),
    path('logout', views.logout_view, name='logout'),
    path('afterlogin', views.afterlogin_view,name='afterlogin'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

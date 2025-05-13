from django.urls import path
from . import views

urlpatterns = [
    # --- Giriş ve Çıkış ---
    path('login/<str:role>/', views.login_view, name='login_view'), 
    path('logout/', views.logout_view, name='logout'),

    # --- Öğrenci ---
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher/grades/', views.teacher_grades_view, name='teacher_grades'),
    path('student/course/<int:enrollment_id>/', views.student_course_detail, name='student_course_detail'),
    path('student/course/<int:enrollment_id>/apply/', views.apply_for_resit, name='apply_for_resit'),
    path('student/announcements/', views.student_announcements, name='student_announcements'),
    path('student/schedule/', views.student_schedule, name='student_schedule'),

    # --- Öğretmen ---
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/course/<int:course_id>/', views.teacher_course_detail, name='teacher_course_detail'),
    path('teacher/resit-applications/', views.teacher_resit_applications, name='teacher_resit_applications'),
    path('teacher/announcements/', views.teacher_announcements, name='teacher_announcements'),
    path('teacher/schedule/', views.teacher_schedule, name='teacher_schedule'),
    path('teacher/course/<int:course_id>/enter-resit-grades/', views.teacher_enter_resit_grades_view, name='teacher_enter_resit_grades'),

    # --- Fakülte ---
    path('faculty/dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('faculty/announcement/<int:announcement_id>/delete/', views.delete_announcement, name='delete_announcement'),
    path('faculty/file/<int:file_id>/delete/', views.delete_uploaded_file, name='delete_uploaded_file'),
    path('faculty/announcement/<int:announcement_id>/edit/', views.edit_announcement, name='edit_announcement'),
    path('faculty/file/<int:file_id>/edit/', views.edit_uploaded_file, name='edit_uploaded_file'),
    path('faculty/resit-announcement/<int:resit_announcement_id>/delete/', views.delete_resit_announcement, name='delete_resit_announcement'),
    path('faculty/resit-announcement/<int:resit_announcement_id>/edit/', views.edit_resit_announcement, name='edit_resit_announcement'),

    path('stix/', views.stix_view, name='stix_page'),
    path('obs/', views.obs_view, name='obs_page'),
    path('alms/', views.alms_view, name='alms_page'),
    
    

]

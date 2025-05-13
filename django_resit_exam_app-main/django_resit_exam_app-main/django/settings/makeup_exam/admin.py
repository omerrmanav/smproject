from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Profile, Course, Enrollment, Announcement, UploadedFile, ResitExamAnnouncement, CourseSession, ResitGrade

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'User Role Profile' 
    fk_name = 'user'
    fields = ('role',) 

class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    list_select_related = ('profile',) 

    @admin.display(description='Role')
    def get_role(self, instance):
        try:
            return instance.profile.get_role_display()
        except Profile.DoesNotExist:
            return '-'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'course_name', 'credits', 'teacher', 'midterm_weight', 'final_weight', 'check_weights_sum')
    search_fields = ('course_code', 'course_name', 'teacher__username') 
    list_filter = ('credits', 'teacher') 
    list_editable = ('credits', 'midterm_weight', 'final_weight')
    
    autocomplete_fields = ['teacher']

    @admin.display(description='Weights Sum 100?', boolean=True)
    def check_weights_sum(self, obj):
         if obj.midterm_weight is not None and obj.final_weight is not None:
             return (obj.midterm_weight + obj.final_weight) == 100
         return False 

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'course',
        'midterm_grade',
        'final_grade',
        'calculated_score_display',
        'letter_grade_display',
        'makeup_eligibility_display',
        'applied_for_makeup'
    )
    list_filter = ('course', 'applied_for_makeup', 'student')
    search_fields = ('student__username', 'course__course_code', 'course__course_name')
    list_editable = ('midterm_grade', 'final_grade', 'applied_for_makeup')
    readonly_fields = ('calculated_score_display', 'letter_grade_display', 'makeup_eligibility_display')
    fieldsets = (
        (None, {'fields': ('student', 'course')}),
        ('Grades', {'fields': ('midterm_grade', 'final_grade')}),
        ('Calculated', {'fields': ('calculated_score_display', 'letter_grade_display', 'makeup_eligibility_display')}),
        ('Makeup Exam', {'fields': ('applied_for_makeup',)}),
    )
    autocomplete_fields = ['student', 'course']

    @admin.display(description='Final Score')
    def calculated_score_display(self, obj):
        score = obj.calculate_final_score()
        return score if score is not None else '-'

    @admin.display(description='Letter Grade')
    def letter_grade_display(self, obj):
        return obj.get_letter_grade()

    @admin.display(description='Eligible for Makeup?', boolean=True)
    def makeup_eligibility_display(self, obj):
        return obj.is_eligible_for_makeup()

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    list_filter = ('author', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('created_at',)
    autocomplete_fields = ['author']

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploader', 'uploaded_at', 'file')
    list_filter = ('uploader', 'uploaded_at')
    search_fields = ('title', 'uploader__username', 'file')
    readonly_fields = ('uploaded_at',)
    autocomplete_fields = ['uploader']


@admin.register(ResitExamAnnouncement)
class ResitExamAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'exam_datetime', 'exam_place', 'posted_by', 'posted_at')
    list_filter = ('course', 'posted_by', 'exam_datetime')
    search_fields = ('title', 'course__course_name', 'course__course_code', 'exam_place', 'additional_info')
    fieldsets = (
        (None, {'fields': ('title', 'course', 'posted_by')}),
        ('Exam Details', {'fields': ('exam_datetime', 'exam_place', 'additional_info')}),
        ('Attachment', {'fields': ('attached_file',)}),
    )
    def save_model(self, request, obj, form, change):
        if not obj.posted_by_id: 
            obj.posted_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(CourseSession)
class CourseSessionAdmin(admin.ModelAdmin):
    list_display = ('course', 'get_day_of_week_display', 'start_time', 'end_time', 'location')
    list_filter = ('day_of_week', 'course__course_code') 
    search_fields = ('course__course_name', 'location')

@admin.register(ResitGrade)
class ResitGradeAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'grade', 'get_student_name', 'get_course_code')
    search_fields = ('enrollment__student__username', 'enrollment__course__course_code')
    list_filter = ('enrollment__course',)

    @admin.display(description='Student')
    def get_student_name(self, obj):
        return obj.enrollment.student.username

    @admin.display(description='Course Code')
    def get_course_code(self, obj):
        return obj.enrollment.course.course_code
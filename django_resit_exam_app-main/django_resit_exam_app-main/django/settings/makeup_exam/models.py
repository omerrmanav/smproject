from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import os

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('faculty', 'Faculty'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"   

class Course(models.Model):
    course_code = models.CharField(max_length=10, unique=True, verbose_name="Course Code", help_text="CSE101")
    course_name = models.CharField(max_length=100, verbose_name="Course Name", help_text="Introduction to Computer Science")
    credits = models.PositiveIntegerField(default=3, verbose_name="Credits")

    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'profile__role': 'teacher'},
        related_name='taught_courses'
    )

    midterm_weight = models.PositiveSmallIntegerField(
        default=40,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    final_weight = models.PositiveSmallIntegerField(
        default=60,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"
    
class Enrollment(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'profile__role': 'student'}
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    midterm_grade = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    final_grade = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    applied_for_makeup = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'course')

    def calculate_final_score(self):
        if self.midterm_grade is not None and self.final_grade is not None:
            score = (self.midterm_grade * self.course.midterm_weight / 100.0) + \
                    (self.final_grade * self.course.final_weight / 100.0)
            return round(score)
        return None
    
    def get_letter_grade(self):
        score = self.calculate_final_score()
        if score is None:
            return '-'
       
        if score >= 90: return 'AA'
        elif score >= 85: return 'BA'
        elif score >= 80: return 'BB'
        elif score >= 70: return 'CB'
        elif score >= 60: return 'CC'
        elif score >= 50: return 'DC' 
        else: return 'FF'
    
    def is_eligible_for_makeup(self):
        letter_grade = self.get_letter_grade()
        return letter_grade in ['DC', 'FF']

    def __str__(self):
        return f"{self.student.username} - {self.course.course_name}"
    
class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'profile__role': 'faculty'}
    )

    def __str__(self):
        return self.title
    
def faculty_upload_path(instance, filename):
    return os.path.join('faculty_uploads', instance.uploader.username, filename)

class UploadedFile(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to=faculty_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True) 
    uploader = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'profile__role': 'faculty'}
    )

    def __str__(self):
        return self.title
    

def resit_exam_announcement_file_path(instance, filename):
    return os.path.join('resit_exam_files', str(instance.id) if instance.id else 'temp_resit_files', filename)

class ResitExamAnnouncement(models.Model):
    title = models.CharField(max_length=200, verbose_name="Resit Announcement Title")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="resit_exam_details", verbose_name="Related Course")
    exam_datetime = models.DateTimeField(verbose_name="Exam Date and Time")
    exam_place = models.CharField(max_length=200, verbose_name="Exam Place (e.g., Classroom A-101)")
    additional_info = models.TextField(blank=True, null=True, verbose_name="Additional Information / Rules")
    attached_file = models.FileField(
        upload_to=resit_exam_announcement_file_path,
        null=True,
        blank=True,
        verbose_name="Attach File (e.g., Exam Topics, Seating Plan)"
    )
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'profile__role': 'faculty'})
    posted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Resit Exam Announcement"
        verbose_name_plural = "Resit Exam Announcements"
        ordering = ['-posted_at']

    def __str__(self):
        return f"Resit for {self.course.course_code}: {self.title}"
    
class CourseSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sessions')
    DAY_CHOICES = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Classroom A-101, Online")

    class Meta:
        verbose_name = "Course Session"
        verbose_name_plural = "Course Sessions"
        ordering = ['day_of_week', 'start_time'] 

    def __str__(self):
        return f"{self.course.course_code} - {self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"
    
class ResitGrade(models.Model):
    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='resit_grade_entry',
        verbose_name="Enrollment for Resit"
    )
    grade = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Resit Exam Grade"
    )

    class Meta:
        verbose_name = "Resit Exam Grade"
        verbose_name_plural = "Resit Exam Grades"

    def __str__(self):
        return f"{self.enrollment.student.username} - {self.enrollment.course.course_code} Resit: {self.grade}"

    def calculate_new_average_with_resit(self):
        if self.enrollment.midterm_grade is not None and self.grade is not None:
            course = self.enrollment.course
            score = (self.enrollment.midterm_grade * course.midterm_weight / 100.0) + \
                    (self.grade * course.final_weight / 100.0)
            return round(score)
        return None

    def get_new_letter_grade_with_resit(self):
        score = self.calculate_new_average_with_resit()
        if score is None:
            return '-'
        if score >= 90: return 'AA'
        elif score >= 85: return 'BA'
        elif score >= 80: return 'BB'
        elif score >= 70: return 'CB'
        elif score >= 60: return 'CC'
        elif score >= 50: return 'DC' 
        else: return 'FF'
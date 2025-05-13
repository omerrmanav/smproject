from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseRedirect 
from django.contrib import messages 
from django.urls import reverse
import csv
import io
import os
import json

from .models import Profile, Course, Enrollment, Announcement, UploadedFile, CourseSession
from .forms import LoginForm, AnnouncementForm, UploadedFileForm, GradeEntryForm, CourseWeightForm, GradeUploadForm, ResitExamAnnouncement, SpecificResitAnnouncementForm

def user_is_role(user, role_name):
    try:
        return user.is_authenticated and user.profile.role == role_name
    except Profile.DoesNotExist:
        return False

def login_selection_view(request):
    if request.user.is_authenticated:
        return redirect_to_dashboard(request)
    return render(request, 'makeup_exam/login_selection.html')

def redirect_to_dashboard(request):
    user = request.user 
    if not user.is_authenticated:
         return redirect('login_selection')

    try:
        profile = user.profile
        role = profile.role
        if role == 'student':
            return redirect('student_dashboard')
        elif role == 'teacher':
            return redirect('teacher_dashboard')
        elif role == 'faculty':
            return redirect('faculty_dashboard')
        else:
            raise Profile.DoesNotExist 
    except Profile.DoesNotExist:
        messages.error(request, "Hesabınız için geçerli bir rol veya profil bulunamadı. Lütfen yönetici ile iletişime geçin.")
        auth_logout(request) 
        return redirect('login_selection') 

def login_view(request, role):
    if request.user.is_authenticated:
        return redirect_to_dashboard(request) 

    if role not in ['student', 'teacher', 'faculty']:
        messages.error(request, "Geçersiz rol seçimi.")
        return redirect('login_selection')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user_is_role(user, role): 
                    auth_login(request, user)
                    return redirect_to_dashboard(request)
                else:
                    messages.error(request, f"Bu kullanıcı '{role.capitalize()}' rolüne sahip değil.")
            else:
                messages.error(request, "Geçersiz kullanıcı adı veya şifre.")
        else:
             messages.error(request, "Lütfen kullanıcı adı ve şifre alanlarını doldurun.")
    else: 
        form = LoginForm()

    context = {
        'form': form,
        'role': role,
        'role_display': role.capitalize()
    }
    return render(request, 'makeup_exam/login_form.html', context)

def logout_view(request):
    auth_logout(request)
    messages.success(request, "Başarıyla çıkış yapıldı.")
    return redirect('login_selection') 

@login_required(login_url='login_selection') 
def student_dashboard(request):
    if not user_is_role(request.user, 'student'):
        messages.error(request, "Öğrenci paneline erişim yetkiniz yok.")
        auth_logout(request)
        return redirect('login_selection')
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    context = {
        'enrollments': enrollments,
        'page_title': 'Dashboard'
    }
    return render(request, 'makeup_exam/student/student_dashboard.html', context)

@login_required(login_url='login_selection')
def student_course_detail(request, enrollment_id):
    if not user_is_role(request.user, 'student'):
        messages.error(request, "Bu sayfaya erişim yetkiniz yok.")
        auth_logout(request)
        return redirect('login_selection')
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)
    context = {
        'enrollment': enrollment,
        'course': enrollment.course,
        'page_title': enrollment.course.course_name
    }
    return render(request, 'makeup_exam/student/student_course_detail.html', context)

@login_required(login_url='login_selection')
def student_announcements(request):
    if not user_is_role(request.user, 'student'):
        messages.error(request, "Bu sayfaya erişim yetkiniz yok.")
        auth_logout(request)
        return redirect('login_selection')
    
    announcements = Announcement.objects.order_by('-created_at')
    uploaded_files = UploadedFile.objects.order_by('-uploaded_at')
    resit_exam_announcements = ResitExamAnnouncement.objects.order_by('-posted_at')
    context = {
        'announcements': announcements,
        'uploaded_files': uploaded_files,
        'resit_exam_announcements': resit_exam_announcements,
        'page_title': 'Announcements'
    }
    return render(request, 'makeup_exam/student/student_announcements.html', context)

@login_required(login_url='login_selection')
def student_schedule(request):
    if not user_is_role(request.user, 'student'):
        messages.error(request, "Bu sayfaya erişim yetkiniz yok.")
        auth_logout(request)
        return redirect('login_selection')

    enrolled_courses = Course.objects.filter(enrollment__student=request.user).distinct()
    schedule_entries = CourseSession.objects.filter(course__in=enrolled_courses).select_related('course')

    schedule_data = []
    for entry in schedule_entries:
        schedule_data.append({
            'title': entry.course.course_code, 
            'day': entry.day_of_week, 
            'start_time': entry.start_time.strftime('%H:%M'),
            'end_time': entry.end_time.strftime('%H:%M'),
            'location': entry.location or ''
        })

    context = {
        'page_title': 'My Schedule',
        'schedule_data_json': json.dumps(schedule_data) 
    }
    return render(request, 'makeup_exam/schedule.html', context) 


@login_required(login_url='login_selection')
def teacher_dashboard(request):
    if not user_is_role(request.user, 'teacher'):
        messages.error(request, "Öğretmen paneline erişim yetkiniz yok.")
        auth_logout(request)
        return redirect('login_selection')
    courses = Course.objects.filter(teacher=request.user)
    context = {
        'courses': courses,
        'page_title': 'Dashboard'
    }
    return render(request, 'makeup_exam/teacher/teacher_dashboard.html', context)

@login_required(login_url='login_selection')
def teacher_grades_view(request):
    if not user_is_role(request.user, 'teacher'):
        messages.error(request, "Not giriş sayfasına erişim yetkiniz yok.")
        auth_logout(request)
        return redirect('login_selection')
    courses = Course.objects.filter(teacher=request.user)
    context = {
        'courses': courses,
        'page_title': 'Grades' 
    }
    return render(request, 'makeup_exam/teacher/teacher_grades.html', context)

@login_required(login_url='login_selection')
def teacher_course_detail(request, course_id):
    if not user_is_role(request.user, 'teacher'):
        messages.error(request, "Bu sayfaya erişim yetkiniz yok.")
        auth_logout(request)
        return redirect('login_selection')

    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    enrollments = Enrollment.objects.filter(course=course).select_related('student')

    session_key = f'upload_results_{course_id}' 
    upload_results = request.session.get(session_key, None)

    weight_form = CourseWeightForm(instance=course)
    grade_forms_list = [(enr, GradeEntryForm(initial={'midterm_grade': enr.midterm_grade, 'final_grade': enr.final_grade, 'enrollment_id': enr.id}, prefix=f'enroll_{enr.id}')) for enr in enrollments]
    upload_form = GradeUploadForm() 
    upload_results = None 

    if request.method == 'POST':
        if 'update_weights' in request.POST:
            weight_form = CourseWeightForm(request.POST, instance=course)
            if weight_form.is_valid():
                weight_form.save()
                messages.success(request, "Ders ağırlıkları başarıyla güncellendi.")
                return redirect('teacher_course_detail', course_id=course.id)
            else:
                messages.error(request, "Ağırlık formunda hatalar var. Lütfen kontrol edin.")
                for enrollment in enrollments:
                    form = GradeEntryForm(initial={'enrollment_id': enrollment.id}, prefix=f'enroll_{enrollment.id}')
                    grade_forms_list.append((enrollment, form))

        elif 'update_grades' in request.POST:
            form_valid = True
            updated_count = 0
            processed_enrollment_ids = set()
            temp_grade_forms = [] 

            for key in request.POST:
                if key.startswith('enroll_') and key.endswith('-enrollment_id'):
                    prefix = key.rsplit('-', 1)[0]
                    enrollment_id_str = request.POST.get(key)
                    try:
                        enrollment_id = int(enrollment_id_str)
                        if enrollment_id in processed_enrollment_ids: continue
                        processed_enrollment_ids.add(enrollment_id)
                        try: enrollment = next(e for e in enrollments if e.id == enrollment_id)
                        except StopIteration:
                            messages.warning(request, f"Geçersiz enrollment ID {enrollment_id}."); form_valid = False; continue

                        form = GradeEntryForm(request.POST, prefix=prefix)
                        if form.is_valid():
                            enrollment.midterm_grade = form.cleaned_data.get('midterm_grade')
                            enrollment.final_grade = form.cleaned_data.get('final_grade')
                            enrollment.save()
                            updated_count += 1
                            temp_grade_forms.append((enrollment, form))
                        else:
                            messages.error(request, f"Öğrenci {enrollment.student.username} için geçersiz not: {form.errors.as_text()}")
                            form_valid = False
                            temp_grade_forms.append((enrollment, form)) 
                    except (ValueError, TypeError):
                        messages.warning(request, f"Geçersiz ID formatı: {enrollment_id_str}"); form_valid = False

            if form_valid and updated_count > 0:
                messages.success(request, f"{updated_count} öğrencinin notları güncellendi.")
                return redirect('teacher_course_detail', course_id=course.id)
            elif not form_valid:
                 messages.error(request, "Not girişlerinde hatalar var. Lütfen kontrol edin.")
                 grade_forms_list = temp_grade_forms 
                 weight_form = CourseWeightForm(instance=course)
            else:
                 messages.info(request, "Kaydedilecek bir not değişikliği yapılmadı.")
                 weight_form = CourseWeightForm(instance=course)
                 for enrollment in enrollments:
                     form = GradeEntryForm(initial={'enrollment_id': enrollment.id}, prefix=f'enroll_{enrollment.id}')
                     grade_forms_list.append((enrollment, form))
        elif 'upload_grades' in request.POST:
            upload_form = GradeUploadForm(request.POST, request.FILES)
            if upload_form.is_valid():
                csv_file = request.FILES['csv_file']
                grade_type_to_update = upload_form.cleaned_data['grade_type'] 
                upload_results = [] 
                updated_count = 0
                errors_found = False

                if not csv_file.name.endswith('.csv'):
                    messages.error(request, "Lütfen geçerli bir CSV dosyası yükleyin.")
                else:
                    try:
                        
                        decoded_file = csv_file.read().decode('utf-8')
                        io_string = io.StringIO(decoded_file)
                        reader = csv.DictReader(io_string)

                        header = [h.lower().strip() for h in reader.fieldnames]
                        if 'username' not in header or 'grade' not in header:
                             raise ValueError("CSV file must contain 'username' and 'grade' columns.")

                        for row in reader:
                            username = row.get('username', '').strip()
                            grade_str = row.get('grade', '').strip()
                            result = {'username': username, 'grade_str': grade_str, 'status': '', 'message': ''}

                            if not username or not grade_str:
                                result['status'] = 'Skipped'
                                result['message'] = 'Missing username or grade.'
                                errors_found = True
                                upload_results.append(result)
                                continue

                            try:
                                grade = int(grade_str)
                                if not (0 <= grade <= 100):
                                    raise ValueError("Grade must be between 0 and 100.")

                                try:
                                    enrollment = Enrollment.objects.get(course=course, student__username=username)

                                    if grade_type_to_update == 'midterm':
                                        enrollment.midterm_grade = grade
                                    elif grade_type_to_update == 'final':
                                        enrollment.final_grade = grade

                                    enrollment.save()
                                    result['status'] = 'Success'
                                    result['message'] = f'{grade_type_to_update.capitalize()} grade set to {grade}.'
                                    updated_count += 1

                                except Enrollment.DoesNotExist:
                                    result['status'] = 'Not Found'
                                    result['message'] = 'Student not enrolled in this course.'
                                    errors_found = True
                                except User.DoesNotExist: 
                                     result['status'] = 'User Not Found'
                                     result['message'] = 'Student username not found in the system.'
                                     errors_found = True

                            except ValueError as ve:
                                result['status'] = 'Error'
                                result['message'] = f'Invalid grade format: {ve}'
                                errors_found = True

                            upload_results.append(result)

                        if updated_count > 0:
                            messages.success(request, f"{updated_count} student grades successfully updated via CSV.")
                        if errors_found:
                            messages.warning(request, "Some rows in the CSV file could not be processed. Please check the results below.")
                        elif updated_count == 0:
                             messages.info(request, "CSV file processed, but no grades were updated (students might not be enrolled or data was invalid).")

                    except ValueError as ve: 
                         messages.error(request, f"Error processing CSV header: {ve}")
                         upload_results = None 
                    except Exception as e: 
                        messages.error(request, f"An error occurred while processing the CSV file: {e}")
                        upload_results = None

            else: 
                messages.error(request, "Please select a grade type and upload a valid CSV file.")

    if weight_form is None: 
        weight_form = CourseWeightForm(instance=course) 

    if not grade_forms_list: 
        for enrollment in enrollments:
             form = GradeEntryForm(
                 initial={
                     'midterm_grade': enrollment.midterm_grade,
                     'final_grade': enrollment.final_grade,
                     'enrollment_id': enrollment.id
                 },
                 prefix=f'enroll_{enrollment.id}'
             )
             grade_forms_list.append((enrollment, form))

    context = {
        'course': course,
        'student_form_pairs': grade_forms_list, 
        'weight_form': weight_form,      
        'upload_form': upload_form,           
        'upload_results': upload_results,          
        'page_title': f"Course Details & Grades: {course.course_code}"
    }
    return render(request, 'makeup_exam/teacher/teacher_course_detail.html', context)


@login_required(login_url='login_selection')
def teacher_announcements(request):
    if not user_is_role(request.user, 'teacher'):
        messages.error(request, "Bu sayfaya erişim yetkiniz yok.")
        auth_logout(request)
        return redirect('login_selection')
    announcements = Announcement.objects.order_by('-created_at')
    uploaded_files = UploadedFile.objects.order_by('-uploaded_at')
    resit_exam_announcements = ResitExamAnnouncement.objects.order_by('-posted_at')

    context = {
        'announcements': announcements, 
        'uploaded_files': uploaded_files, 
        'resit_exam_announcements': resit_exam_announcements,
        'page_title': 'Announcements'
    }
    return render(request, 'makeup_exam/teacher/teacher_announcements.html', context)

@login_required(login_url='login_selection')
def teacher_schedule(request):
    if not user_is_role(request.user, 'teacher'):
        messages.error(request, "Bu sayfaya erişim yetkiniz yok.")
        auth_logout(request)
        return redirect('login_selection')

    teacher_courses = Course.objects.filter(teacher=request.user)
    schedule_entries = CourseSession.objects.filter(course__in=teacher_courses).select_related('course')

    schedule_data = []
    for entry in schedule_entries:
        schedule_data.append({
            'title': entry.course.course_code,
            'day': entry.day_of_week,
            'start_time': entry.start_time.strftime('%H:%M'),
            'end_time': entry.end_time.strftime('%H:%M'),
            'location': entry.location or ''
        })

    context = {
        'page_title': 'Teaching Schedule',
        'schedule_data_json': json.dumps(schedule_data) 
    }
    return render(request, 'makeup_exam/schedule.html', context)

@login_required(login_url='login_selection')
def faculty_dashboard(request):
    if not user_is_role(request.user, 'faculty'):
        messages.error(request, "Fakülte paneline erişim yetkiniz yok.")
        auth_logout(request)
        return redirect('login_selection')

    general_announcement_form = AnnouncementForm(prefix='general_announcement') 
    specific_resit_form = SpecificResitAnnouncementForm(prefix='specific_resit')
    file_form = UploadedFileForm(prefix='file')

    if request.method == 'POST':
        if 'submit_general_announcement' in request.POST:
            general_announcement_form = AnnouncementForm(request.POST, prefix='general_announcement') 
            if general_announcement_form.is_valid():
                announcement = general_announcement_form.save(commit=False)
                announcement.author = request.user
                announcement.save()
                messages.success(request, 'General announcement published successfully.')
                return redirect('faculty_dashboard')
            else:
                 messages.error(request, 'Error in general announcement form.')
                 specific_resit_form = SpecificResitAnnouncementForm(prefix='specific_resit')
                 file_form = UploadedFileForm(prefix='file')

        elif 'submit_specific_resit_announcement' in request.POST:
            specific_resit_form = SpecificResitAnnouncementForm(request.POST, request.FILES, prefix='specific_resit')
            if specific_resit_form.is_valid():
                resit_announcement = specific_resit_form.save(commit=False)
                resit_announcement.posted_by = request.user 
                resit_announcement.save()
                messages.success(request, 'Resit exam announcement published successfully.')
                return redirect('faculty_dashboard')
            else:
                messages.error(request, 'Error in resit exam announcement form.')
                general_announcement_form = AnnouncementForm(prefix='general_announcement') 
                file_form = UploadedFileForm(prefix='file')

        elif 'submit_file' in request.POST:
            file_form = UploadedFileForm(request.POST, request.FILES, prefix='file')
            if file_form.is_valid():
                uploaded_file = file_form.save(commit=False)
                uploaded_file.uploader = request.user
                uploaded_file.save()
                messages.success(request, 'File uploaded successfully.')
                return redirect('faculty_dashboard')
            else:
                messages.error(request, 'Error in file upload form.')
                general_announcement_form = AnnouncementForm(prefix='general_announcement') 
                specific_resit_form = SpecificResitAnnouncementForm(prefix='specific_resit')

    general_announcements = Announcement.objects.order_by('-created_at') 
    resit_exam_announcements = ResitExamAnnouncement.objects.order_by('-posted_at') 
    uploaded_files = UploadedFile.objects.order_by('-uploaded_at')

    context = {
        'general_announcements': general_announcements,
        'resit_exam_announcements': resit_exam_announcements,
        'uploaded_files': uploaded_files,
        'general_announcement_form': general_announcement_form, 
        'specific_resit_form': specific_resit_form,
        'file_form': file_form,
        'page_title': 'Faculty Dashboard'
    }
    return render(request, 'makeup_exam/faculty/faculty_dashboard.html', context)

@login_required(login_url='login_selection')
def delete_resit_announcement(request, resit_announcement_id):
    if not user_is_role(request.user, 'faculty'): messages.error(request, "Unauthorized access."); return redirect_to_dashboard(request)
    resit_ann = get_object_or_404(ResitExamAnnouncement, id=resit_announcement_id, posted_by=request.user)
    try:
        title = resit_ann.title
        if resit_ann.attached_file and hasattr(resit_ann.attached_file, 'path') and os.path.exists(resit_ann.attached_file.path): 
            os.remove(resit_ann.attached_file.path)
        resit_ann.delete(); messages.success(request, f"Resit announcement '{title}' deleted.")
    except Exception as e: messages.error(request, f"Error deleting resit announcement: {e}")
    return redirect('faculty_dashboard')

@login_required(login_url='login_selection')
def edit_resit_announcement(request, resit_announcement_id):
    if not user_is_role(request.user, 'faculty'): messages.error(request, "Unauthorized access."); return redirect_to_dashboard(request)
    resit_ann = get_object_or_404(ResitExamAnnouncement, id=resit_announcement_id, posted_by=request.user)
    if request.method == 'POST':
        form = SpecificResitAnnouncementForm(request.POST, request.FILES, instance=resit_ann, prefix='specific_resit_edit')
        if form.is_valid():
            form.save(); messages.success(request, f"Resit announcement '{resit_ann.title}' updated.")
            return redirect('faculty_dashboard')
        else: messages.error(request, "Error updating resit announcement.")
    else: form = SpecificResitAnnouncementForm(instance=resit_ann, prefix='specific_resit_edit')
    context = {'form': form, 'resit_announcement': resit_ann, 'page_title': f"Edit Resit Announcement: {resit_ann.title}"}
    return render(request, 'makeup_exam/faculty/edit_resit_announcement.html', context)

@login_required(login_url='login_selection')
def apply_for_resit(request, enrollment_id):
    """Öğrencinin belirli bir ders için bütünlemeye başvurmasını sağlar."""
    if not user_is_role(request.user, 'student'):
        messages.error(request, "Bu işlem için yetkiniz yok.")
        auth_logout(request)
        return redirect('login_selection')
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)

    if request.method == 'POST':
        if enrollment.is_eligible_for_makeup() and not enrollment.applied_for_makeup:
            enrollment.applied_for_makeup = True
            enrollment.save()
            messages.success(request, f"'{enrollment.course.course_name}' dersi için bütünleme sınavına başarıyla başvurdunuz.")
        elif enrollment.applied_for_makeup:
            messages.warning(request, "Bu dersin bütünleme sınavına zaten başvurdunuz.")
        else:
            messages.error(request, "Bu dersin bütünleme sınavına başvurmaya uygun değilsiniz.")
        return redirect('student_course_detail', enrollment_id=enrollment.id)
    else:
        messages.error(request, "Geçersiz istek yöntemi.")
        return redirect('student_dashboard') 

@login_required(login_url='login_selection')
def teacher_resit_applications(request):
    if not user_is_role(request.user, 'teacher'):
        messages.error(request, "Bu sayfaya erişim yetkiniz yok.")
        auth_logout(request)
        return redirect('login_selection')

    teacher_courses = Course.objects.filter(teacher=request.user)

    resit_applications = Enrollment.objects.filter(
        course__in=teacher_courses,
        applied_for_makeup=True 
    ).select_related('student', 'course').order_by('course__course_code', 'student__username')

    context = {
        'applications': resit_applications,
        'page_title': 'Resit Exam Applications'
    }
    return render(request, 'makeup_exam/teacher/teacher_resit_applications.html', context)


@login_required(login_url='login_selection')
def stix_view(request):
    context = {'page_title': 'STIX'}
    return render(request, 'makeup_exam/stix.html', context)

@login_required(login_url='login_selection')
def obs_view(request):
    context = {'page_title': 'OBS'}
    return render(request, 'makeup_exam/obs.html', context)

@login_required(login_url='login_selection')
def alms_view(request):
    context = {'page_title': 'ALMS'}
    return render(request, 'makeup_exam/alms.html', context)

@login_required(login_url='login_selection')
def delete_announcement(request, announcement_id):
    if not user_is_role(request.user, 'faculty'):
        messages.error(request, "Bu işlem için yetkiniz yok.")
        return redirect_to_dashboard(request)

    announcement = get_object_or_404(Announcement, id=announcement_id)

    try:
        announcement_title = announcement.title 
        announcement.delete()
        messages.success(request, f"'{announcement_title}' başlıklı duyuru başarıyla silindi.")
    except Exception as e:
        messages.error(request, f"Duyuru silinirken bir hata oluştu: {e}")

    return redirect('faculty_dashboard')


@login_required(login_url='login_selection')
def delete_uploaded_file(request, file_id):
    if not user_is_role(request.user, 'faculty'):
        messages.error(request, "Bu işlem için yetkiniz yok.")
        return redirect_to_dashboard(request)

    uploaded_file = get_object_or_404(UploadedFile, id=file_id)

    try:
        file_title = uploaded_file.title
        
        uploaded_file.delete()
        messages.success(request, f"'{file_title}' başlıklı dosya başarıyla silindi.")
    except Exception as e:
        messages.error(request, f"Dosya silinirken bir hata oluştu: {e}")

    return redirect('faculty_dashboard')


@login_required(login_url='login_selection')
def edit_announcement(request, announcement_id):
    if not user_is_role(request.user, 'faculty'):
        messages.error(request, "Bu işlem için yetkiniz yok.")
        return redirect_to_dashboard(request)

    announcement = get_object_or_404(Announcement, id=announcement_id) 

    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement, prefix='announcement') 
        if form.is_valid():
            form.save()
            messages.success(request, f"'{announcement.title}' başlıklı duyuru başarıyla güncellendi.")
            return redirect('faculty_dashboard') 
        else:
            messages.error(request, "Duyuru formunda hatalar var. Lütfen kontrol edin.")
    else: 
        form = AnnouncementForm(instance=announcement, prefix='announcement')

    context = {
        'form': form,
        'announcement': announcement, 
        'page_title': f"Edit Announcement: {announcement.title}"
    }
    return render(request, 'makeup_exam/faculty/edit_announcement.html', context)

@login_required(login_url='login_selection')
def edit_uploaded_file(request, file_id):
    if not user_is_role(request.user, 'faculty'):
        messages.error(request, "Bu işlem için yetkiniz yok.")
        return redirect_to_dashboard(request)

    uploaded_file = get_object_or_404(UploadedFile, id=file_id) 

    if request.method == 'POST':
        form = UploadedFileForm(request.POST, request.FILES, instance=uploaded_file, prefix='file') 
        if form.is_valid():
            form.save()
            messages.success(request, f"'{uploaded_file.title}' başlıklı dosya başarıyla güncellendi.")
            return redirect('faculty_dashboard') 
        else:
            messages.error(request, "Dosya formunda hatalar var. Lütfen kontrol edin.")
    else: 
        form = UploadedFileForm(instance=uploaded_file, prefix='file')

    context = {
        'form': form,
        'uploaded_file': uploaded_file,
        'page_title': f"Edit File: {uploaded_file.title}"
    }
    return render(request, 'makeup_exam/faculty/edit_uploaded_file.html', context)

from .forms import ResitGradeEntryForm 
from .models import Course, Enrollment, ResitGrade 
from django.forms import inlineformset_factory 

@login_required(login_url='login_selection')
def teacher_enter_resit_grades_view(request, course_id):
    if not user_is_role(request.user, 'teacher'):
        messages.error(request, "Bu sayfaya erişim yetkiniz yok.")
        auth_logout(request)
        return redirect('login_selection')

    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    applied_enrollments = Enrollment.objects.filter(course=course, applied_for_makeup=True).select_related('student', 'resit_grade_entry')

    student_resit_forms_data = [] 

    if request.method == 'POST':
        updated_count = 0
        error_found_in_form = False
        for enrollment in applied_enrollments:
            form_prefix = f'resit_enroll_{enrollment.id}'
            resit_grade_instance = getattr(enrollment, 'resit_grade_entry', None)
            
            form = ResitGradeEntryForm(request.POST, instance=resit_grade_instance, prefix=form_prefix)
            if form.is_valid():
                if form.cleaned_data.get('grade') is not None: 
                    resit_grade_entry = form.save(commit=False)
                    resit_grade_entry.enrollment = enrollment 
                    resit_grade_entry.save()
                    updated_count += 1
                elif resit_grade_instance and form.cleaned_data.get('grade') is None: 
                    resit_grade_instance.delete()
                    updated_count +=1 
            else:
                messages.error(request, f"Error for {enrollment.student.username}: {form.errors.as_text()}")
                error_found_in_form = True
            
            current_resit_instance = getattr(enrollment, 'resit_grade_entry', None)
            student_resit_forms_data.append((enrollment, ResitGradeEntryForm(instance=current_resit_instance, prefix=form_prefix), current_resit_instance))


        if not error_found_in_form and updated_count > 0:
            messages.success(request, f"{updated_count} student resit grades processed.")
            return redirect('teacher_enter_resit_grades', course_id=course.id)
        elif not error_found_in_form and updated_count == 0:
            messages.info(request, "No resit grades were changed.")

    else:
        for enrollment in applied_enrollments:
            resit_grade_instance = getattr(enrollment, 'resit_grade_entry', None)
            form = ResitGradeEntryForm(instance=resit_grade_instance, prefix=f'resit_enroll_{enrollment.id}')
            student_resit_forms_data.append((enrollment, form, resit_grade_instance))

    context = {
        'course': course,
        'student_forms_data': student_resit_forms_data,
        'page_title': f"Enter Resit Grades for {course.course_code}"
    }
    return render(request, 'makeup_exam/teacher/teacher_enter_resit_grades.html', context)

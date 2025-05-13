from django import forms
from .models import Announcement, UploadedFile, Course, ResitExamAnnouncement, ResitGrade

# Basit bir giriş formu
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

# Fakülte için duyuru formu
class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control mb-2'}),
            'content': forms.Textarea(attrs={'class': 'form-control mb-2', 'rows': 4}),
        }

# Fakülte için dosya yükleme formu
class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control mb-2'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control mb-2'}),
        }

# Öğretmen için not giriş formu (Tek öğrenci için)
# Daha sonra ModelFormSet ile toplu giriş daha verimli olur.
class GradeEntryForm(forms.Form):
     midterm_grade = forms.IntegerField(
         required=False, # Boş olabilir
         min_value=0,
         max_value=100,
         widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'})
     )
     final_grade = forms.IntegerField(
         required=False, # Boş olabilir
         min_value=0,
         max_value=100,
         widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'})
     )
     # Hangi enrollment kaydı için olduğunu bilmek için gizli alan
     enrollment_id = forms.IntegerField(widget=forms.HiddenInput())

class CourseWeightForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['midterm_weight', 'final_weight']
        labels = {
            'midterm_weight': 'Vize Ağırlığı (%)',
            'final_weight': 'Final Ağırlığı (%)',
        }
        widgets = {
            # Daha küçük inputlar ve min/max değerleri
            'midterm_weight': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0', 'max': '100'}),
            'final_weight': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0', 'max': '100'}),
        }

    # Ağırlıkların toplamının 100 olup olmadığını kontrol et
    def clean(self):
        cleaned_data = super().clean()
        midterm = cleaned_data.get("midterm_weight")
        final = cleaned_data.get("final_weight")

        # Alanların None olup olmadığını kontrol et (formda boş bırakılmış olabilirler)
        if midterm is not None and final is not None:
            if midterm + final != 100:
                # Genel form hatası ekle
                raise forms.ValidationError(
                    "Vize ve Final ağırlıklarının toplamı 100 olmalıdır.",
                    code='weights_mismatch'
                )
        # Alanlardan biri boşsa validasyon yapma (veya zorunlu yap)
        # else:
        #     raise forms.ValidationError("Lütfen hem vize hem de final ağırlığını girin.")

        return cleaned_data

class GradeUploadForm(forms.Form):
    # Hangi not türünün yükleneceğini seçmek için
    GRADE_TYPE_CHOICES = (
        ('midterm', 'Midterm Grade'),
        ('final', 'Final Grade'),
        # ('resit', 'Resit Grade'), # Modelde varsa eklenebilir
    )
    grade_type = forms.ChoiceField(
        choices=GRADE_TYPE_CHOICES,
        required=True,
        label="Select Grade Type to Upload",
        widget=forms.Select(attrs={'class': 'form-select form-select-sm mb-2'})
    )
    # Dosya yükleme alanı
    csv_file = forms.FileField(
        required=True,
        label="Upload CSV File",
        help_text="CSV file must have 'username' and 'grade' columns.",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm', 'accept': '.csv'}) # Sadece .csv kabul et
    )

class SpecificResitAnnouncementForm(forms.ModelForm): # Adını değiştirdim
    exam_datetime = forms.DateTimeField(
        label="Exam Date and Time",
        required=True, # Bu alan zorunlu olsun
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )
    class Meta:
        model = ResitExamAnnouncement
        # posted_by ve posted_at otomatik ayarlanacak
        fields = [
            'title',
            'course',
            'exam_datetime',
            'exam_place',
            'additional_info',
            'attached_file'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'SE101 Resit Exam Information'}),
            'course': forms.Select(attrs={'class': 'form-select mb-2'}),
            'exam_place': forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Classroom A-101'}),
            'additional_info': forms.Textarea(attrs={'class': 'form-control mb-2', 'rows': 3, 'placeholder': 'Include exam rules or other important information.'}),
            'attached_file': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm mb-2'}),
        }
        labels = {
            'additional_info': 'Additional Information / Rules (Optional)',
            'attached_file': 'Attach File (Optional)',
        }

class ResitGradeEntryForm(forms.ModelForm):
    class Meta:
        model = ResitGrade
        fields = ['grade'] # Sadece bütünleme notunu alacağız
        widgets = {
            'grade': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0', 'max': '100', 'placeholder': 'Enter Resit Grade'}),
        }
        labels = {
            'grade': 'Resit Exam Grade'
        }
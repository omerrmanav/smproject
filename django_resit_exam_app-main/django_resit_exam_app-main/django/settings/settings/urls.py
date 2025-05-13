from django.contrib import admin
from django.urls import path, include 
from django.conf import settings
from django.conf.urls.static import static
from makeup_exam import views as makeup_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', makeup_views.login_selection_view, name='login_selection'),
    
    path('', include('makeup_exam.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


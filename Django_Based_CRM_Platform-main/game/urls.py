from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from game import settings
from django.conf.urls.static import static

urlpatterns = [

    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/accounts')),
    path('accounts/', include('accounts.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

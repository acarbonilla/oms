from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler403, handler404, handler500

# For media, static, and image
from django.conf import settings
from django.conf.urls.static import static

from c2.views import custom_404, custom_403, custom_500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('members.urls')),
    path('c2/', include('c2.urls')),
    path('danao/', include('danao.urls')),
    path('core/', include('core.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404 = custom_404
handler403 = custom_403
handler500 = custom_500

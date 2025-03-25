from django.contrib import admin

from .models import C2Standard, C2RecentImage, C2Facility, C2User

admin.site.register(C2Standard)
admin.site.register(C2RecentImage)
admin.site.register(C2Facility)
admin.site.register(C2User)
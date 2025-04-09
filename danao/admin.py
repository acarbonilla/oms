from django.contrib import admin
from django.utils.html import mark_safe

from .models import (DanaoStandard, DanaoRecentImage, DanaoFacility, DanaoUser, DanaoTechActivities,
                     DanaoTechActivityImage)


# This is for QR code
class DanaoRecentImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'status')  # ❌ Removed `show_qr_code`
    search_fields = ('title', 'uploaded_by__name')
    list_filter = ('status',)


admin.site.register(DanaoRecentImage, DanaoRecentImageAdmin)


# ✅ Ensure QR codes are only shown in C2FacilityAdmin
class DanaoFacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'show_qr_code')

    def show_qr_code(self, obj):
        if obj.qr_code:
            return mark_safe(f'<img src="{obj.qr_code.url}" width="100" />')
        return "No QR Code"

    show_qr_code.short_description = "QR Code"


admin.site.register(DanaoTechActivityImage)
admin.site.register(DanaoTechActivities)
admin.site.register(DanaoFacility, DanaoFacilityAdmin)
admin.site.register(DanaoStandard)
admin.site.register(DanaoUser)

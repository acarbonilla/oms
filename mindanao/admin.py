from django.contrib import admin
from django.utils.html import mark_safe

from .models import (MindanaoStandard, MindanaoRecentImage, MindanaoFacility, MindanaoUser, MindanaoTechActivities,
                     MindanaoTechActivityImage)


# This is for QR code
class MindanaoRecentImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'status')  # ❌ Removed `show_qr_code`
    search_fields = ('title', 'uploaded_by__name')
    list_filter = ('status',)


admin.site.register(MindanaoRecentImage,MindanaoRecentImageAdmin)


# ✅ Ensure QR codes are only shown in C2FacilityAdmin
class MindanaoFacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'show_qr_code')

    def show_qr_code(self, obj):
        if obj.qr_code:
            return mark_safe(f'<img src="{obj.qr_code.url}" width="100" />')
        return "No QR Code"

    show_qr_code.short_description = "QR Code"


admin.site.register(MindanaoTechActivityImage)
admin.site.register(MindanaoTechActivities)
admin.site.register(MindanaoFacility,MindanaoFacilityAdmin)
admin.site.register(MindanaoStandard)
admin.site.register(MindanaoUser)

from django.contrib import admin
from django.utils.html import mark_safe

from .models import C2Standard, C2RecentImage, C2Facility, C2User, C2TechActivities, C2TechActivityImage


# This is for QR code
class C2RecentImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'status')  # ❌ Removed `show_qr_code`
    search_fields = ('title', 'uploaded_by__name')
    list_filter = ('status',)


admin.site.register(C2RecentImage, C2RecentImageAdmin)


# ✅ Ensure QR codes are only shown in C2FacilityAdmin
class C2FacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'show_qr_code')

    def show_qr_code(self, obj):
        if obj.qr_code:
            return mark_safe(f'<img src="{obj.qr_code.url}" width="100" />')
        return "No QR Code"

    show_qr_code.short_description = "QR Code"


admin.site.register(C2TechActivityImage)
admin.site.register(C2TechActivities)
admin.site.register(C2Facility, C2FacilityAdmin)
admin.site.register(C2Standard)
admin.site.register(C2User)

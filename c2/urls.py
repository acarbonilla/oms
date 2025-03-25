from django.urls import path
from .views import (empMember, amMember, amAssessment, upload_recent_image_qr, update_recent_image,
                    recent_image_detail, evMember, standard_image_ev, failed_list, generate_pdf,
                    generate_selected_pdf, standard_image_ev_details,
                    )

urlpatterns = [
    path('', evMember, name='evMember'),
    path('empMember', empMember, name='empMember'),
    path('amMember/', amMember, name='amMember'),
    path('assessment/', amAssessment, name='assessment'),
    # Upload
    path("c2/facility/<int:facility_id>/upload/", upload_recent_image_qr, name="facility_qr_upload"),  # ✅ Correct
    # Update or Edit
    path('update_recent_image/<str:pk>/', update_recent_image, name='update_recent_image'),
    # Details
    path('recent-image/<int:pk>/', recent_image_detail, name='recent_image_detail'),
    # Standard Image For EV group
    path('standard_image_ev/', standard_image_ev, name='standard_image_ev'),
    path("standard-image/<int:pk>/", standard_image_ev_details, name="standard_image_ev_details"),  # ✅ Details Page

    # Failed List
    path("failed-list/", failed_list, name="failed_list"),

    # PDF
    path("download-pdf/", generate_pdf, name="download_pdf"),
    path("download-selected-pdf/", generate_selected_pdf, name="download_selected_pdf"),
]


from django.urls import path
from .views import (empMember, amMember, amAssessment, upload_recent_image_qr, update_recent_image,
                    recent_image_detail, evMember, standard_image_ev, failed_list, generate_pdf,
                    generate_selected_pdf, standard_image_ev_details, pass_list, not_visited_facilities_list,
                    access_denied, trigger_500, tech_act_upload, activity_list, activity_detail, facility_list,
                    generate_qr_code, tech_activity_download, tech_activity_pdf
                    )

# app_name = 'c2'

urlpatterns = [
    path('', evMember, name='evMember'),
    path('empMember/', empMember, name='empMember'),
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

    # This is for Technical Activities Form tech_activity_upload
    path('tech-activity/upload/', tech_act_upload, name='tech_act_upload'),
    path('tech-activity/list/', activity_list, name='activity_list'),
    path('tech-activity/detail/<int:activity_id>/', activity_detail, name='activity_detail'),
    path('tech-activity/download/', tech_activity_download, name='tech_activity_download'),
    path('tech-activity/pdf/', tech_activity_pdf, name='tech_activity_pdf'),

    # Failed List
    path("failed-list/", failed_list, name="failed_list"),

    # Pass List
    path('pass/', pass_list, name='pass_list'),

    # Not Visited List
    path('not-visited/', not_visited_facilities_list, name='not_visited_facilities_list'),

    # Forbidden
    path("access-denied/", access_denied, name="access_denied"),

    # PDF
    path("download-pdf/", generate_pdf, name="download_pdf"),
    path("download-selected-pdf/", generate_selected_pdf, name="download_selected_pdf"),

    # This is for downloading the QR code from Facility
    path('facilities/', facility_list, name='facility_list'),
    path('facility/<int:facility_id>/download_qr/', generate_qr_code, name='download_qr_code'),

    path("test-500/", trigger_500),  # Go to /test-500/ to see the 500 error page

]

from django.urls import path
from .views import (empMemberMindanao, amMemberMindanao, amAssessmentMindanao, upload_recent_image_qrMindanao,
                    update_recent_imageMindanao,
                    recent_image_detailMindanao, evMemberMindanao, standard_image_evMindanao,
                    failed_listMindanao,
                    generate_pdfMindanao,
                    generate_selected_pdfMindanao, standard_image_ev_detailsMindanao, pass_listMindanao,
                    not_visited_facilities_listMindanao,
                    access_denied, tech_act_uploadMindanao, activity_listMindanao, activity_detailMindanao,
                    facility_listMindanao,
                    generate_qr_codeMindanao, mindanao_tech_activity_download,
                    mindanao_tech_activity_pdf, tech_activity_update_mindanao
                    )

# app_name = 'mindanao'
urlpatterns = [
    path('', evMemberMindanao, name='evMemberMindanao'),
    path('empMember/', empMemberMindanao, name='empMemberMindanao'),
    path('amMember/', amMemberMindanao, name='amMemberMindanao'),
    path('assessment/', amAssessmentMindanao, name='assessmentMindanao'),

    # Upload
    path("mindanao/facility/<int:facility_id>/upload/", upload_recent_image_qrMindanao,
         name="facility_qr_uploadMindanao"),  # ✅ Correct

    # Update or Edit
    path('update_recent_image/<str:pk>/', update_recent_imageMindanao, name='update_recent_imageMindanao'),

    # Details
    path('recent-image/<int:pk>/', recent_image_detailMindanao, name='recent_image_detailMindanao'),

    # Standard Image For EV group
    path('standard_image_ev/', standard_image_evMindanao, name='standard_image_evMindanao'),
    path("standard-image/<int:pk>/", standard_image_ev_detailsMindanao, name="standard_image_ev_detailsMindanao"),
    # ✅ Details Page

    # This is for Technical Activities Form tech_activity_upload
    path('tech-act/upload/', tech_act_uploadMindanao, name='tech_act_uploadMindanao'),
    path('tech-act/upload/<int:pk>/', tech_act_uploadMindanao, name='tech_act_upload_with_pkMindanao'),
    path('activities/', activity_listMindanao, name="activity_listMindanao"),
    path("activity/<int:activity_id>/", activity_detailMindanao, name="activity_detailMindanao"),
    path('tech-activity/download/', mindanao_tech_activity_download, name='mindanao_tech_activity_download'),
    path('tech-activity/pdf/', mindanao_tech_activity_pdf, name='mindanao_tech_activity_pdf'),
    path('tech-activity/<int:pk>/update/', tech_activity_update_mindanao, name='tech_activity_update_mindanao'),

    # Failed List
    path("failed-list/", failed_listMindanao, name="failed_listMindanao"),

    # Pass List
    path('pass/', pass_listMindanao, name='pass_listMindanao'),

    # Not Visited List
    path('not-visited/', not_visited_facilities_listMindanao, name='not_visited_facilities_listMindanao'),

    # Forbidden
    path("access-denied/", access_denied, name="access_denied"),

    # PDF
    path("download-pdf/", generate_pdfMindanao, name="download_pdfMindanao"),
    path("download-selected-pdf/", generate_selected_pdfMindanao, name="download_selected_pdfMindanao"),

    # This is for downloading the QR code from Facility
    path('facilities/', facility_listMindanao, name='facility_listMindanao'),
    path('facility/<int:facility_id>/download_qr/', generate_qr_codeMindanao, name='download_qr_codeMindanao'),

]

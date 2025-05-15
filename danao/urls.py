from django.urls import path
from danao.views import (empMemberDanao, amMemberDanao, amAssessmentDanao, upload_recent_image_qrDanao,
                         update_recent_imageDanao,
                         recent_image_detailDanao, evMemberDanao, standard_image_evDanao, failed_listDanao,
                         generate_pdfDanao,
                         generate_selected_pdfDanao, standard_image_ev_detailsDanao, pass_listDanao,
                         not_visited_facilities_listDanao,
                         access_denied, tech_act_uploadDanao, activity_listDanao, activity_detailDanao,
                         facility_listDanao,
                         generate_qr_codeDanao, danao_tech_activity_download,
                         danao_tech_activity_pdf, tech_activity_update_danao
                         )


# app_name = 'danao'
urlpatterns = [
    path('', evMemberDanao, name='evMemberDanao'),
    path('empMember/', empMemberDanao, name='empMemberDanao'),
    path('amMember/', amMemberDanao, name='amMemberDanao'),
    path('assessment/', amAssessmentDanao, name='assessmentDanao'),

    # Upload
    path("danao/facility/<int:facility_id>/upload/", upload_recent_image_qrDanao, name="facility_qr_uploadDanao"),  # ✅ Correct

    # Update or Edit
    path('update_recent_image/<str:pk>/', update_recent_imageDanao, name='update_recent_imageDanao'),

    # Details
    path('recent-image/<int:pk>/', recent_image_detailDanao, name='recent_image_detailDanao'),

    # Standard Image For EV group
    path('standard_image_ev/', standard_image_evDanao, name='standard_image_evDanao'),
    path("standard-image/<int:pk>/", standard_image_ev_detailsDanao, name="standard_image_ev_detailsDanao"),
    # ✅ Details Page

    # This is for Technical Activities Form tech_activity_upload
    path('tech-act/upload/', tech_act_uploadDanao, name='tech_act_uploadDanao'),
    path('tech-act/upload/<int:pk>/', tech_act_uploadDanao, name='tech_act_upload_with_pkDanao'),
    path('activities/', activity_listDanao, name="activity_listDanao"),
    path("activity/<int:activity_id>/", activity_detailDanao, name="activity_detailDanao"),
    path('tech-activity/download/', danao_tech_activity_download, name='danao_tech_activity_download'),
    path('tech-activity/pdf/', danao_tech_activity_pdf, name='danao_tech_activity_pdf'),
    path('tech-activity/<int:pk>/update/', tech_activity_update_danao, name='tech_activity_update_danao'),

    # Failed List
    path("failed-list/", failed_listDanao, name="failed_listDanao"),

    # Pass List
    path('pass/', pass_listDanao, name='pass_listDanao'),

    # Not Visited List
    path('not-visited/', not_visited_facilities_listDanao, name='not_visited_facilities_listDanao'),

    # Forbidden
    path("access-denied/", access_denied, name="access_denied"),

    # PDF
    path("download-pdf/", generate_pdfDanao, name="download_pdfDanao"),
    path("download-selected-pdf/", generate_selected_pdfDanao, name="download_selected_pdfDanao"),

    # This is for downloading the QR code from Facility
    path('facilities/', facility_listDanao, name='facility_listDanao'),
    path('facility/<int:facility_id>/download_qr/', generate_qr_codeDanao, name='download_qr_codeDanao'),

]

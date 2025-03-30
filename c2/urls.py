# from django.conf.urls import handler403, handler404, handler500
from django.urls import path
from .views import (empMember, amMember, amAssessment, upload_recent_image_qr, update_recent_image,
                    recent_image_detail, evMember, standard_image_ev, failed_list, generate_pdf,
                    generate_selected_pdf, standard_image_ev_details, pass_list, not_visited_facilities_list,
                    access_denied, trigger_500, tech_act_upload, activity_list, activity_detail
                    )

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
    path('tech-act/upload/', tech_act_upload, name='tech_act_upload'),
    path('tech-act/upload/<int:pk>/', tech_act_upload, name='tech_act_upload_with_pk'),
    path('activities/', activity_list, name="activity_list"),
    path("activity/<int:activity_id>/", activity_detail, name="activity_detail"),

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

    path("test-500/", trigger_500),  # Go to /test-500/ to see the 500 error page
]

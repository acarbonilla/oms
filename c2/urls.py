from django.urls import path
from .views import empMember, amMember, amAssessment, upload_recent_image, update_recent_image, recent_image_detail

urlpatterns = [
    path('', empMember, name='empMember'),
    path('amMember/', amMember, name='amMember'),
    path('assessment/', amAssessment, name='assessment'),
    path('upload-recent/', upload_recent_image, name='upload_recent_image'),
    # Update or Edit
    path('update_recent_image/<str:pk>/', update_recent_image, name='update_recent_image'),
    # Details
    path('recent-image/<int:pk>/', recent_image_detail, name='recent_image_detail'),
]
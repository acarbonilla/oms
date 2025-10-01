import os
from django.conf import settings
import re
from django.core.files.base import ContentFile

from django.contrib.auth.models import User
from django.db import models

from core.models import StandardImage, RecentImage, SBU
from django.db.models import OuterRef, Subquery  # Query for only one and most updated

# QR Code

import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

# Naming every upload image
from django.utils.text import slugify

# Editor for text field
from ckeditor.fields import RichTextField


def upload_to_technical(instance, filename):
    folder = settings.IMAGE_ENV
    return os.path.join(f"img/{folder}/technical_images", filename)


def upload_to_qrcodes(instance, filename):
    sanitized_name = instance.name.replace(" ", "_").lower()
    return f"img/{os.getenv('IMAGE_ENV', 'production')}/qrcodes/qr_{sanitized_name}.png"


class C2User(models.Model):
    position = (
        ("AM", "AM"), ("EMP", "EMP"), ("EV", "EV")
    )
    sbu = models.ForeignKey(SBU, on_delete=models.CASCADE)
    name = models.OneToOneField(User, on_delete=models.CASCADE, related_name="users")
    position = models.CharField(
        max_length=20,
        choices=position,
        verbose_name='Position',
        default='EMP'

    )
    facility = models.ForeignKey('C2Facility', on_delete=models.SET_NULL, null=True, blank=True)  # ✅ NEW

    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


# It is used only 1 output per facility on Standard app here in models.py. No repeated of location even if uploaded
# many times
class C2StandardManager(models.Manager):
    def latest_per_facility(self):
        """Returns only the latest C2Standard per facility."""
        latest_standard = C2Standard.objects.filter(
            facility=OuterRef('facility')
        ).order_by('-updated', '-id').values('id')[:1]

        return self.filter(id=Subquery(latest_standard))


# This is a path function for C2Standard
def standard_image_upload_path(instance, filename):
    """Generates a unique filename based on facility name and an incrementing number."""
    facility_name = slugify(instance.facility.name)  # Convert facility name to a safe format

    # Define base directory for images
    folder = settings.IMAGE_ENV
    base_dir = os.path.join(settings.MEDIA_ROOT, f"img/{folder}/standard_images")
    # Ensure the directory exists
    os.makedirs(base_dir, exist_ok=True)

    # Find existing files for this facility
    existing_files = [
        f for f in os.listdir(base_dir)
        if f.startswith(facility_name)
    ]

    # Get next number (increment by 1)
    next_number = len(existing_files) + 1
    new_filename = f"{facility_name}_{next_number}.png"

    return os.path.join(f"img/{folder}/standard_images", new_filename)


class C2Standard(StandardImage):
    facility = models.ForeignKey('C2Facility', on_delete=models.SET_NULL, null=True, related_name="standards")
    standard_image = models.ImageField(upload_to=standard_image_upload_path)
    objects = C2StandardManager()  # Attach custom manager

    def __str__(self):
        return f"{self.facility}"


# This is naming every upload image
def recent_image_upload_path(instance, filename):
    """Generates a unique filename based on facility name and an incrementing number."""

    facility_name = slugify(instance.s_image.facility.name)
    facility_name = re.sub(r'[^a-zA-Z0-9_-]', '', facility_name)  # Remove unsafe characters

    # Correct base directory setup
    folder = settings.IMAGE_ENV
    base_dir = os.path.join(settings.MEDIA_ROOT, f"img/{folder}/recent_images")

    # Ensure the directory exists
    os.makedirs(base_dir, exist_ok=True)

    # Find existing files
    existing_files = [
        f for f in os.listdir(base_dir) if f.startswith(facility_name)
    ]

    # Get next number (increment by 1)
    next_number = len(existing_files) + 1

    # Get correct file extension
    ext = filename.split(".")[-1]
    new_filename = f"{facility_name}_{next_number}.{ext}"

    # return os.path.join("img/development/recent_images", new_filename)
    return os.path.join(f"img/{folder}/recent_images", new_filename)


# This is for Development Only


class C2RecentImage(RecentImage):
    STATUS_CHOICES = [
        ("Pass", "Pass"),
        ("Failed", "Failed"),
        ("Pending", "Pending")
    ]
    s_image = models.ForeignKey(C2Standard, on_delete=models.SET_NULL, null=True, )
    recent_image = models.ImageField(upload_to=recent_image_upload_path)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    uploaded_by = models.ForeignKey(C2User, on_delete=models.CASCADE, related_name="uploaded_images")
    remark_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="remarked_images")


class C2Facility(models.Model):
    name = models.CharField(max_length=50, verbose_name="Facility")
    qr_code = models.ImageField(upload_to=upload_to_qrcodes, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    def get_qr_url(self):
        """Builds a dynamic URL for this facility based on BASE_URL."""
        return f"{settings.BASE_URL}/c2/c2/facility/{self.id}/upload/"

    def generate_qr_code(self):
        """Generate and save QR code for this facility."""
        sanitized_name = self.name.replace(" ", "_").lower()
        filename = f"qr_{sanitized_name}.png"

        # ✅ Use dynamic BASE_URL
        qr_url = self.get_qr_url()
        qr = qrcode.make(qr_url)

        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        # ✅ Delete old QR code if it exists
        if self.qr_code:
            self.qr_code.delete(save=False)

        # ✅ Save the new QR code
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        """Override save method to generate QR code on creation."""
        super().save(*args, **kwargs)  # Save first to get an ID
        if not self.qr_code:  # Generate only if QR does not exist
            self.generate_qr_code()
            super().save(*args, **kwargs)  # Save again with QR code

    def __str__(self):
        return self.name


class C2TechActivities(models.Model):
    name = models.CharField(max_length=100, verbose_name="Activity")
    location = models.CharField(max_length=100)
    uploaded_by = models.ForeignKey(C2User, on_delete=models.CASCADE, related_name="uploaded_images_by")
    remarks = RichTextField(blank=True, null=True)
    remark_by = models.ForeignKey(C2User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tech_remarks')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated']

    def __str__(self):
        return f"{self.name}"


class C2TechActivityImage(models.Model):
    activity = models.ForeignKey(C2TechActivities, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=upload_to_technical)
    label = models.CharField(max_length=200, blank=True, null=True, verbose_name="Image Label/Context")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.activity.name}" + (f" - {self.label}" if self.label else "")

# Need to change when. This is for Production
# image = models.ImageField(upload_to="img/production/technical_images")

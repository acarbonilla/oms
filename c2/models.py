import os
from django.conf import settings

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


class C2Standard(StandardImage):
    facility = models.ForeignKey('C2Facility', on_delete=models.SET_NULL, null=True, related_name="standards")
    # standard_image = models.ImageField(upload_to="img/development/standard_images/")
    standard_image = models.ImageField(upload_to="img/production/standard_images/")
    objects = C2StandardManager()  # Attach custom manager

    def __str__(self):
        return f"{self.facility}"


# This is naming every upload image
def recent_image_upload_path(instance, filename):
    """Generates a unique filename based on facility name and an incrementing number."""
    facility_name = slugify(instance.s_image.facility.name)  # Convert facility name to a safe format

    # This is for server-setup
    # base_dir = os.path.join(settings.MEDIA_ROOT, "img/production/recent_images")  # This is for server-setup
    base_dir = "img/production/recent_images"
    # Ensure the directory exists
    os.makedirs(base_dir, exist_ok=True)  # Creates the directory if it does not exist for Server

    # This is for Development setup
    # base_dir = "img/development/recent_images"  # This setup is for development

    # Find existing files for this facility
    existing_files = [
        f for f in os.listdir(os.path.join("media", base_dir))
        if f.startswith(facility_name)
    ]

    # Get next number (increment by 1)
    next_number = len(existing_files) + 1
    new_filename = f"{facility_name}_{next_number}.png"

    return os.path.join(base_dir, new_filename)


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


def technical_activities_path(instance, filename):
    """Generates a unique filename based on facility name and an incrementing number."""
    facility_name = slugify(instance.location.name)  # Convert facility name to a safe format

    # This is for Server Setup
    # base_dir = os.path.join(settings.MEDIA_ROOT, "media/img/technical_images")  # Use absolute path

    # This is for Development setup
    base_dir = "media/img/technical_images"

    # Ensure directory exists before listing
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    existing_files = [f for f in os.listdir(base_dir) if f.startswith(facility_name)]
    next_number = len(existing_files) + 1
    return os.path.join("img/technical_images", f"{facility_name}_{next_number}.png")


class C2Facility(models.Model):
    name = models.CharField(max_length=50, verbose_name="Facility")
    # qr_code = models.ImageField(upload_to="img/development/qrcodes/", blank=True, null=True)  # Ready for Development
    qr_code = models.ImageField(upload_to="img/production/qrcodes/", blank=True, null=True) # Ready for Production
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    def generate_qr_code(self):
        """Generate and save QR code for this facility."""

        # ✅ Convert facility name to a safe filename
        sanitized_name = self.name.replace(" ", "_").lower()
        filename = f"qr_{sanitized_name}.png"

        # ✅ Generate the QR code with the facility URL
        qr_url = f"https://192.168.1.20/c2/c2/facility/{self.id}/upload/"
        # qr_url = f"http://127.0.0.1:8000/c2/c2/facility/{self.id}/upload/"
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
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated']

    def __str__(self):
        return f"{self.name}"


class C2TechActivityImage(models.Model):
    activity = models.ForeignKey(C2TechActivities, on_delete=models.CASCADE, related_name="images")
    # image = models.ImageField(upload_to="img/development/technical_images")
    image = models.ImageField(upload_to="img/production/technical_images")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.activity.name}"

# Need to change when. This is for Production
# image = models.ImageField(upload_to="img/production/technical_images")

from django.contrib.auth.models import User
from django.db import models

from core.models import StandardImage, RecentImage, SBU
from django.db.models import OuterRef, Subquery  # Query for only one and most updated


class C2User(models.Model):
    position = (
        ("AM", "AM"), ("EMP", "EMP")
    )
    sbu = models.ForeignKey(SBU, on_delete=models.CASCADE)
    name = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField(
        max_length=20,
        choices=position,
        verbose_name='Position',
        default='EMP'

    )

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
    facility = models.ForeignKey('C2Facility', on_delete=models.CASCADE)
    standard_image = models.ImageField(upload_to="img/standard_images/")

    objects = C2StandardManager()  # Attach custom manager

    def __str__(self):
        return f"{self.facility}"


class C2RecentImage(RecentImage):
    STATUS_CHOICES = [
        ("Pass", "Pass"),
        ("Failed", "Failed"),
        ("Pending", "Pending")
    ]
    facility = models.ForeignKey('C2Facility', on_delete=models.CASCADE)  # Remove Redundant from s_image.
    s_image = models.ForeignKey(C2Standard, on_delete=models.CASCADE)
    recent_image = models.ImageField(upload_to="img/recent_images/")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    uploaded_by = models.ForeignKey(C2User, on_delete=models.CASCADE)
    remark_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # Need to add who is the AM update

    def __str__(self):
        return f"{self.title} - {self.status}"


class C2Facility(models.Model):
    name = models.CharField(max_length=50, verbose_name="Facility")

    def __str__(self):
        return f"{self.name}"

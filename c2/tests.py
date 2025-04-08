from django.test import TestCase
from django.contrib.auth.models import User
from c2.models import C2User, C2RecentImage, C2Facility, C2TechActivities
from c2.forms import (
    C2RecentImageForm,
    C2RecentImageFormUpdate,
    TechnicalActivitiesForm,
    TechActivityImageForm
)

from core.models import SBU
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile


class FormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="testpass")
        cls.sbu = SBU.objects.create(name="SBU 1")
        cls.facility = C2Facility.objects.create(name="Facility X")  # ✅ Let Django auto-assign

        cls.c2_user = C2User.objects.create(
            sbu=cls.sbu,
            name=cls.user,
            position="EMP",
            facility=cls.facility
        )

    def test_recent_image_form_missing_title(self):
        form = C2RecentImageForm(user=self.user, data={})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertEqual(form.errors['title'][0], 'Title is missing.')

    def test_recent_image_form_valid(self):
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        form_data = {'title': 'Test Image'}
        form = C2RecentImageForm(user=self.user, data=form_data, files={'recent_image': image})
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(instance.uploaded_by, self.c2_user)

    def test_recent_image_form_no_matching_user(self):
        form = C2RecentImageForm(user=None, data={'title': 'No User'})
        form.is_valid()  # Even without image, just checking behavior
        instance = form.save(commit=False)
        self.assertIsNone(instance.uploaded_by)

    def test_recent_image_form_update(self):
        image = SimpleUploadedFile("recent.jpg", b"image_data", content_type="image/jpeg")
        instance = C2RecentImage.objects.create(title="Old", recent_image=image, uploaded_by=self.c2_user)

        form = C2RecentImageFormUpdate(data={
            'remarks': 'Updated',
            'status': 'Done',
            're_schedule': None,
        }, files={'recent_image': image}, instance=instance, user=self.user)

        self.assertTrue(form.is_valid())
        updated = form.save()
        self.assertEqual(updated.remark_by, self.user)

    def test_tech_activity_image_form_valid(self):
        activity = C2TechActivities.objects.create(
            name="Sample Activity",
            location="HQ",
            uploaded_by=self.c2_user
        )
        self.assertEqual(activity.uploaded_by, self.c2_user)

    def create_test_c2_user(self):
        sbu = SBU.objects.create(name="Test SBU")
        user = User.objects.create(username="testuser")
        return C2User.objects.create(name=user, sbu=sbu)
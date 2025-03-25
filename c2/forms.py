from django import forms
from django.contrib.auth.models import User

from .models import C2RecentImage, C2User


class C2RecentImageForm(forms.ModelForm):
    class Meta:
        model = C2RecentImage
        fields = ['facility', 'title', 's_image', 'recent_image']  # Remove 'facility'

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            c2_user = C2User.objects.get(name=user)  # Get the corresponding C2User instance
            self.instance.uploaded_by = c2_user  # Automatically assign uploaded_by
        except C2User.DoesNotExist:
            self.instance.uploaded_by = None  # Prevent errors if user is not found

        # Add custom styling to widgets
        self.fields['facility'].widget.attrs.update({'class': 'form-control'}) # Remove
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['s_image'].widget.attrs.update({'class': 'form-control'})
        self.fields['recent_image'].widget.attrs.update({'class': 'form-control'})


class C2RecentImageFormUpdate(forms.ModelForm):

    class Meta:
        model = C2RecentImage
        fields = ['remarks', 're_schedule', 'recent_image', 'status', 'remark_by']

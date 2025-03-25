from django import forms
from django.contrib.auth.models import User

from .models import C2RecentImage, C2User


class C2RecentImageForm(forms.ModelForm):
    class Meta:
        model = C2RecentImage
        fields = ['title', 'recent_image']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user  # ✅ Store user but don't assign it yet

        # Add custom styling
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['recent_image'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        """Override save() to assign `uploaded_by` before saving."""
        instance = super().save(commit=False)  # ✅ Create object but don't save yet

        if self.user:  # ✅ Ensure user exists before assignment
            try:
                c2_user = C2User.objects.get(name=self.user)
                instance.uploaded_by = c2_user
            except C2User.DoesNotExist:
                instance.uploaded_by = None  # ✅ Prevent errors if user is missing

        if commit:
            instance.save()  # ✅ Save only if commit=True

        return instance


class C2RecentImageFormUpdate(forms.ModelForm):
    class Meta:
        model = C2RecentImage
        fields = ['remarks', 're_schedule', 'recent_image', 'status']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # ✅ Get the user from views
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:  # ✅ Auto-assign remark_by if user exists
            instance.remark_by = self.user
        if commit:
            instance.save()
        return instance

from django import forms
from .models import (MindanaoRecentImage, MindanaoUser, MindanaoTechActivities, MindanaoTechActivityImage)


class MindanaoRecentImageForm(forms.ModelForm):
    title = forms.CharField(
        required=True,
        error_messages={'required': 'Title is missing.'}
    )

    class Meta:
        model = MindanaoRecentImage
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
                mindanao_user = MindanaoUser.objects.get(name=self.user)
                instance.uploaded_by = mindanao_user
            except MindanaoUser.DoesNotExist:
                instance.uploaded_by = None  # ✅ Prevent errors if user is missing

        if commit:
            instance.save()  # ✅ Save only if commit=True

        return instance


class MindanaoRecentImageFormUpdate(forms.ModelForm):
    class Meta:
        model = MindanaoRecentImage
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


class MindanaoTechnicalActivitiesForm(forms.ModelForm):
    class Meta:
        model = MindanaoTechActivities
        fields = ['name', 'location', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # No need to modify 'uploaded_by' here; handled in the view

    def clean_remarks(self):
        """Clean and decode HTML entities in remarks field."""
        remarks = self.cleaned_data.get('remarks')
        if remarks:
            import html

            # Decode all HTML entities in one pass
            decoded_remarks = html.unescape(remarks)

            return decoded_remarks
        return remarks


class MindanaoTechActivityImageForm(forms.ModelForm):
    class Meta:
        model = MindanaoTechActivityImage
        fields = ['image']

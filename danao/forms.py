from django import forms
from django.contrib.auth.models import User

from .models import DanaoRecentImage, DanaoUser, DanaoTechActivities, DanaoFacility, DanaoTechActivityImage


class DanaoRecentImageForm(forms.ModelForm):
    title = forms.CharField(
        required=True,
        error_messages={'required': 'Title is missing.'}
    )

    class Meta:
        model = DanaoRecentImage
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
                danao_user = DanaoUser.objects.get(name=self.user)
                instance.uploaded_by = danao_user
            except DanaoUser.DoesNotExist:
                instance.uploaded_by = None  # ✅ Prevent errors if user is missing

        if commit:
            instance.save()  # ✅ Save only if commit=True

        return instance


class DanaoRecentImageFormUpdate(forms.ModelForm):
    class Meta:
        model = DanaoRecentImage
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


class DanaoTechnicalActivitiesForm(forms.ModelForm):
    class Meta:
        model = DanaoTechActivities
        fields = ['name', 'location', 'remarks', 'potential_risk', 'probability_of_occurrence', 'impact', 'levels_of_priority']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'potential_risk': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'probability_of_occurrence': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'impact': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'levels_of_priority': forms.RadioSelect(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # No need to modify 'uploaded_by' here; handled in the view
        
        # Add custom styling and attributes for risk assessment fields
        self.fields['potential_risk'].required = False
        self.fields['potential_risk'].empty_label = "Select a risk type..."
        
        self.fields['probability_of_occurrence'].required = False
        self.fields['impact'].required = False
        self.fields['levels_of_priority'].required = False
        
        # Add custom CSS classes for better styling
        self.fields['name'].widget.attrs.update({'class': 'form-control form-control-lg'})
        self.fields['location'].widget.attrs.update({'class': 'form-control form-control-lg'})

    def clean_remarks(self):
        """Clean and decode HTML entities in remarks field."""
        remarks = self.cleaned_data.get('remarks')
        if remarks:
            import html
            
            # Decode all HTML entities in one pass
            decoded_remarks = html.unescape(remarks)
            
            return decoded_remarks
        return remarks


class DanaoTechActivityImageForm(forms.ModelForm):
    class Meta:
        model = DanaoTechActivityImage
        fields = ['image', 'label']
        widgets = {
            'label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter image label/context (optional)',
                'maxlength': '200'
            }),
        }

from django import forms
from .models import Pet, PetInquiry


class ReportPetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['name', 'species','breed','gender',  'age','color', 'description', 'image','location','contact_phone', 'status', 'animal_condition', 'last_seen_location', 'medical_attention_needed']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
             'species': forms.TextInput(attrs={'placeholder': 'Dog, Cat, etc.'}),
            'gender': forms.Select(choices=[('Male','Male'),('Female','Female')]),
            'animal_condition': forms.Select(attrs={'class': 'form-control'}),
        }


class ContactMessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows':4}), max_length=2000)


class ImageCheckForm(forms.Form):
    image = forms.ImageField(required=True)


class PetSearchForm(forms.Form):
    """Form for searching found pets by various criteria."""
    species = forms.CharField(
        max_length=50, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Dog, Cat, Bird'
        })
    )
    breed = forms.CharField(
        max_length=50, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Golden Retriever, Persian'
        })
    )
    color = forms.CharField(
        max_length=50, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Brown, Black, White'
        })
    )
    location = forms.CharField(
        max_length=255, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Downtown, Park Area'
        })
    )
    gender = forms.ChoiceField(
        choices=[('', 'Any Gender'), ('Male', 'Male'), ('Female', 'Female')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    age_min = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min age'
        })
    )
    age_max = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max age'
        })
    )


class PetInquiryForm(forms.ModelForm):
    """Form for users to inquire about specific pets."""
    class Meta:
        model = PetInquiry
        fields = ['inquiry_message', 'contact_email', 'contact_phone']
        widgets = {
            'inquiry_message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Please describe why you think this might be your pet...'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890 (optional)'
            })
        }
        labels = {
            'inquiry_message': 'Your Message',
            'contact_email': 'Contact Email',
            'contact_phone': 'Contact Phone (Optional)'
        }

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')
    phone_number = forms.CharField(max_length=15, required=True, help_text='Required. Enter a valid phone number.')
    user_type = forms.ChoiceField(
        choices=Profile.USER_TYPE_CHOICES,
        required=True,
        help_text='Select your role in the pet rescue community.'
    )

    class Meta:
        model = User
        fields = ("username", "email", "user_type", "phone_number", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create profile with user_type and phone number
            Profile.objects.create(
                user=user,
                user_type=self.cleaned_data['user_type'],
                phone_number=self.cleaned_data['phone_number']
            )
        return user

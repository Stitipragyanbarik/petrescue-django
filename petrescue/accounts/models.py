from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Profile(models.Model):
    USER_TYPE_CHOICES = [
        ('adopter', 'Adopter'),
        ('rescuer', 'Rescuer'),
        ('pet_owner', 'Pet Owner'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='adopter',
        help_text="Select your role in the pet rescue community"
    )
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")]
    )

    def __str__(self):
        return f"{self.user.username}'s profile ({self.get_user_type_display()})"

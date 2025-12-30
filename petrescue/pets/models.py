from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.utils import timezone
from datetime import timedelta


def default_expiry():
    return timezone.now() + timedelta(days=7)


User = get_user_model()


class Pet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets')
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=50, blank=True)
    breed = models.CharField(max_length=50, blank=True) 
    gender = models.CharField(max_length=10, choices=[('Male','Male'),('Female','Female')], default='Male')
    age = models.PositiveIntegerField(null=True, blank=True)
    color = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    # Image of the pet (optional)
    image = models.ImageField(upload_to='pets/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    # status: lost (reported by owner), found (reported by rescuer), or adoption (available for adoption)
    STATUS_CHOICES = [
        ('lost', 'Lost'),
        ('found', 'Found'),
        ('adoption', 'Available for Adoption'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='lost')
    
    # approval status for admin moderation
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending')
    
    # contact phone for owners/rescuers to be displayed when match occurs
    contact_phone = models.CharField(max_length=30, blank=True)
    # store a perceptual hash (hex) to speed up matching
    image_hash = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    # report date when the pet was reported
    report_date = models.DateTimeField(auto_now_add=True)
    # animal condition choices
    CONDITION_CHOICES = [
        ('healthy', 'Healthy'),
        ('injured', 'Injured'),
        ('sick', 'Sick'),
        ('critical', 'Critical'),
    ]
    animal_condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='healthy')
    # additional fields
    last_seen_location = models.CharField(max_length=255, blank=True)
    medical_attention_needed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.owner.username})"

    def save(self, *args, **kwargs):
        """Override save to compute perceptual hash for the image when available.

        This centralizes hash computation so any code that saves a Pet will have
        the `image_hash` populated if `Pillow` and `imagehash` are installed.
        If the libraries are not available or hashing fails, we silently skip
        hashing to keep the save operation robust.
        """
        # Call parent save first so `image` file is persisted when uploading
        super().save(*args, **kwargs)

        # Only compute if image exists and hash not already set
        if self.image and (not self.image_hash):
            try:
                from PIL import Image
                import imagehash
            except Exception:
                return

            try:
                # open the image from the storage path and compute phash
                with Image.open(self.image.path) as im:
                    h = imagehash.phash(im)
                    self.image_hash = h.__str__()
                    # Save again to persist the hash
                    super().save(update_fields=['image_hash'])
            except Exception:
                # If hashing fails, leave image_hash blank and continue
                return


class MatchRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('owner_approved', 'Owner Approved'),
        ('owner_rejected', 'Owner Rejected'),
        ('rescuer_confirmed', 'Rescuer Confirmed'),
    ]

    pet = models.ForeignKey('Pet', on_delete=models.CASCADE, related_name='match_requests')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    found_pet = models.ForeignKey('Pet', on_delete=models.CASCADE, related_name='found_matches', null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    reason = models.CharField(max_length=255, blank=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expiry)

    def __str__(self):
        return f"MatchRequest({self.pet} reporter={self.reporter} status={self.status})"
class ContactRequest(models.Model):
    """A mediated contact channel created when owner approves a match.

    Reporter (rescuer) can send messages which are forwarded to owner by the system.
    Owner can view messages in the site or reply which will be forwarded to reporter.
    """
    match_request = models.OneToOneField(MatchRequest, on_delete=models.CASCADE, related_name='contact_request')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"ContactRequest(match={self.match_request.id})"


class ContactMessage(models.Model):
    contact_request = models.ForeignKey(ContactRequest, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent_via_email = models.BooleanField(default=False)

    def __str__(self):
        return f"ContactMessage({self.contact_request.id} from={self.sender.username})"


class PetSearchQuery(models.Model):
    """Model to track user search queries for lost pets."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_queries')
    species = models.CharField(max_length=50, blank=True)
    breed = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male','Male'),('Female','Female')], blank=True)
    age_min = models.PositiveIntegerField(null=True, blank=True)
    age_max = models.PositiveIntegerField(null=True, blank=True)
    search_date = models.DateTimeField(auto_now_add=True)
    results_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-search_date']
    
    def __str__(self):
        return f"Search by {self.user.username} on {self.search_date.strftime('%Y-%m-%d')}"


class AdminNotification(models.Model):
    """Model for admin notifications about user activities and system events."""
    NOTIFICATION_TYPES = [
        ('search_inquiry', 'Search Inquiry'),
        ('potential_match', 'Potential Match Found'),
        ('contact_request', 'Contact Request'),
        ('new_pet_report', 'New Pet Report'),
        ('match_approved', 'Match Approved by Owner'),
        ('match_rejected', 'Match Rejected by Owner'),
    ]
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='triggered_notifications', null=True, blank=True)
    pet = models.ForeignKey('Pet', on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    search_query = models.ForeignKey(PetSearchQuery, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    match_request = models.ForeignKey(MatchRequest, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type}: {self.title}"


class PetInquiry(models.Model):
    """Model to track inquiries made by users about specific pets."""
    inquirer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pet_inquiries')
    pet = models.ForeignKey('Pet', on_delete=models.CASCADE, related_name='inquiries')
    inquiry_message = models.TextField()
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=30, blank=True)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('responded', 'Responded'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['inquirer', 'pet']  # Prevent duplicate inquiries
    
    def __str__(self):
        return f"Inquiry by {self.inquirer.username} about {self.pet.name}"

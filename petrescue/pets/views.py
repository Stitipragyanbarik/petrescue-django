# dling File Creation

# - Noticed the file doesn't exist, so create_file will be used instead of edit_file.  
# - Preparing to create a new file at petrescue/pets/templates/pets/admin_pending.html with HTML content.

# ## Extending File Content

# - Adding HTML structure for an admin dashboard to display pending pet reports within a container div.
# - Including a header and conditional rendering for a list of pending pets with their details.

# - Each pet report card shows the pet's name, status, and owner information like username and email.
# - Displaying optional fields like species, age, description, contact phone, and pet image with default values if missing.

# Assistant: Now I need to update the admin_pending view to handle the POST requests for approve/reject actions.<edit_file>
# <path>petrescue/pets/views.py</path>
# <content">@login_required
# def admin_pending(request):
#     """Admin view to manage pending pet reports."""
#     # Check if user is admin (you might want to use Django's admin permissions)
#     if not request.user.is_superuser:
#         return render(request, 'pets/admin_pending.html', {'error': 'Access denied. Admin privileges required.'})

#     if request.method == 'POST':
#         pet_id = request.POST.get('pet_id')
#         action = request.POST.get('action')

#         try:
#             pet = Pet.objects.get(id=pet_id, approval_status='pending')
#             if action == 'approve':
#                 pet.approval_status = 'approved'
#                 messages.success(request, f'Pet "{pet.name}" has been approved.')
#             elif action == 'reject':
#                 pet.approval_status = 'rejected'
#                 messages.success(request, f'Pet "{pet.name}" has been rejected.')
#             pet.save()
#         except Pet.DoesNotExist:
#             messages.error(request, 'Pet not found or already processed.')

#         return redirect('pets:admin_pending')

#     # Get pending reports
#     pending_pets = Pet.objects.filter(approval_status='pending').order_by('-created_at')

#     # Get stats
#     total_pets = Pet.objects.count()
#     approved_pets = Pet.objects.filter(approval_status='approved').count()
#     rejected_pets = Pet.objects.filter(approval_status='rejected').count()
#     pending_count = pending_pets.count()

#     return render(request, 'pets/admin_pending.html', {
#         'pending_pets': pending_pets,
#         'total_pets': total_pets,
#         'approved_pets': approved_pets,
#         'rejected_pets': rejected_pets,
#         'pending_count': pending_count,
#     })
#             if pet.status == 'lost' and pet.image_hash:
#                 dataset_matches = Pet.objects.filter(status='available').exclude(image_hash__isnull=True).exclude(image_hash='')
#                 present = False
#                 for candidate in dataset_matches:
#                     try:
#                         d = imagehash.hex_to_hash(candidate.image_hash) - imagehash.hex_to_hash(pet.image_hash)
#                         if d is not None and d <= 8:
#                             present = True
#                             break
#                     except Exception:
#                         continue
#                 if present:
#                     messages.info(request, 'The uploaded image is present in the dataset.')
#                 else:
#                     messages.info(request, 'The uploaded image is not present in the dataset.')

#             # if the report is a "found" report, try to match against lost pets
#             if pet.status == 'found':
#                 matches = []
#                 # Only attempt matching when imagehash is available and we have hashes
#                 if imagehash is not None and pet.image_hash:
#                     for candidate in Pet.objects.filter(status='lost').exclude(id=pet.id).exclude(image_hash__isnull=True):
#                         try:
#                             d = imagehash.hex_to_hash(candidate.image_hash) - imagehash.hex_to_hash(pet.image_hash)
#                         except Exception:
#                             d = None
#                         if d is not None and d <= 8:  # threshold, tune as needed
#                             matches.append(candidate)

#                 # If no phash matches found, attempt an OpenCV-based descriptor matcher
#                 if not matches:
#                     try:
#                         from .utils import opencv_orb_match_score
#                         # build a list of candidate lost pets that have images
#                         candidates = Pet.objects.filter(status='lost').exclude(id=pet.id).exclude(image__isnull=True)
#                         scored = []
#                         for c in candidates:
#                             if not c.image:
#                                 continue
#                             score = opencv_orb_match_score(pet.image.path, c.image.path)
#                             if score is None:
#                                 continue
#                             scored.append((score, c))
#                         # sort by descending score and take top 10
#                         scored.sort(reverse=True, key=lambda t: t[0])
#                         matches = [c for _, c in scored[:10] if _ and _ > 10]
#                     except Exception:
#                         # if OpenCV is not installed or an error occurs, skip
#                         pass

#                 # Final fallback: embedding-based matcher (TensorFlow MobileNetV2)
#                 if not matches:
#                     try:
#                         from pets.embeddings import find_similar_embeddings
#                         emb_dir = os.path.join(settings.MEDIA_ROOT, 'embeddings')
#                         sims = find_similar_embeddings(pet.image.path, emb_dir, top_k=10)
#                         emb_matches = []
#                         for score, fname in sims:
#                             # fname format: pet_<id>.npy
#                             try:
#                                 pid = int(fname.split('_')[1].split('.')[0])
#                                 candidate = Pet.objects.filter(id=pid, status='lost').first()
#                                 if candidate:
#                                     emb_matches.append(candidate)
#                             except Exception:
#                                 continue
#                         if emb_matches:
#                             matches = emb_matches
#                     except Exception:
#                         pass

#                 # If any matches found, create MatchRequest entries and notify owners
#                 if matches:
#                     from .models import MatchRequest
#                     from django.template.loader import render_to_string
#                     from django.core.mail import send_mail
#                     from django.urls import reverse

#                     created_requests = []
#                     for candidate in matches:
#                         mr = MatchRequest.objects.create(
#                             pet=candidate,
#                             reporter=request.user,
#                             found_pet=pet,
#                             confidence=None,
#                             reason='automatched'
#                         )
#                         created_requests.append((mr, candidate))

#                         # send email to owner with approve/reject links
#                         approve_url = request.build_absolute_uri(reverse('pets:match_approve', args=[str(mr.token)]))
#                         reject_url = request.build_absolute_uri(reverse('pets:match_reject', args=[str(mr.token)]))
#                         subject = f"Possible match found for your pet {candidate.name}"
#                         message = render_to_string('pets/match_email.txt', {
#                             'owner': candidate.owner,
#                             'pet': candidate,
#                             'reporter': request.user,
#                             'found_pet': pet,
#                             'approve_url': approve_url,
#                             'reject_url': reject_url,
#                         })
#                         # send via console backend in development
#                         send_mail(subject, message, None, [candidate.owner.email])

#                     # show rescuer a confirmation page that owners were notified
#                     return render(request, 'pets/match_sent.html', {'pet': pet, 'created_requests': created_requests})

#                 return render(request, 'pets/match_results.html', {'pet': pet, 'matches': matches})

#             return redirect('home')
#     else:
#         form = ReportPetForm()

#     return render(request, 'pets/report_pet.html', {'form': form})


# def match_approve(request, token):
#     from .models import MatchRequest
#     mr = get_object_or_404(MatchRequest, token=token)
#     # Only the pet owner may approve
#     if request.user.is_authenticated and request.user == mr.pet.owner:
#         mr.status = 'owner_approved'
#         mr.save()
#         # Create a mediated contact request (do NOT expose owner contact directly)
#         from .models import ContactRequest
#         cr = ContactRequest.objects.create(match_request=mr)
#         # Notify reporter that owner approved and provide link to contact form
#         from django.core.mail import send_mail
#         from django.urls import reverse
#         contact_url = request.build_absolute_uri(reverse('pets:contact_request', args=[cr.id]))
#         subject = f"Owner approved contact for pet {mr.pet.name}"
#         body = f"The owner approved your match request. Please contact the owner via the secure relay: {contact_url}"
#         if mr.reporter.email:
#             send_mail(subject, body, None, [mr.reporter.email])
#         return render(request, 'pets/match_confirm.html', {'match': mr, 'contact_request': cr})
#     else:
#         return render(request, 'pets/match_confirm.html', {'match': mr, 'error': 'You must be the pet owner and logged in to approve.'})


# def match_reject(request, token):
#     from .models import MatchRequest
#     mr = get_object_or_404(MatchRequest, token=token)
#     if request.user.is_authenticated and request.user == mr.pet.owner:
#         mr.status = 'owner_rejected'
#         mr.save()
#         return render(request, 'pets/match_rejected.html', {'match': mr})
#     else:
#         return render(request, 'pets/match_rejected.html', {'match': mr, 'error': 'You must be the pet owner and logged in to reject.'})



# @login_required
# def contact_request_view(request, cr_id):
#     """Reporter uses this view to send a message to the owner via the relay."""
#     from .models import ContactRequest, ContactMessage
#     cr = get_object_or_404(ContactRequest, id=cr_id)
#     # Only allow the reporter (match_request.reporter) to send via this endpoint
#     if request.user != cr.match_request.reporter:
#         return render(request, 'pets/contact_request.html', {'error': 'Not authorized to view this contact request.'})

#     if request.method == 'POST':
#         text = request.POST.get('message', '').strip()
#         if text:
#             # create message in the contact thread
#             msg = ContactMessage.objects.create(contact=cr, sender=request.user, message=text)
#             # forward to owner via email (relay) if owner's email exists
#             owner_email = cr.match_request.pet.owner.email
#             if owner_email:
#                 from django.core.mail import send_mail
#                 subject = f"Message regarding your pet {cr.match_request.pet.name}"
#                 body = f"You have a new message from a rescuer:\n\n{text}\n\nReply in the site when logged in."
#                 send_mail(subject, body, None, [owner_email])
#         return render(request, 'pets/contact_request.html', {'contact': cr, 'sent': True})

#     return render(request, 'pets/contact_request.html', {'contact': cr})


# @login_required
# def contact_owner_view(request, cr_id):
#     """Owner can view messages for a contact request."""
#     from .models import ContactRequest
#     cr = get_object_or_404(ContactRequest, id=cr_id)
#     if request.user != cr.match_request.pet.owner:
#         return render(request, 'pets/contact_owner.html', {'error': 'Not authorized.'})
#     # owner can also post replies via this view (simple implementation)
#     from .forms import ContactMessageForm
#     from .models import ContactMessage
#     if request.method == 'POST':
#         form = ContactMessageForm(request.POST)
#         if form.is_valid():
#             msg = form.cleaned_data['message']
#             ContactMessage.objects.create(contact=cr, sender=request.user, message=msg)
#             # optionally email reporter
#             reporter_email = cr.match_request.reporter.email
#             if reporter_email:
#                 from django.core.mail import send_mail
#                 send_mail(f"Reply regarding your report for {cr.match_request.pet.name}", msg, None, [reporter_email])
#             return render(request, 'pets/contact_owner.html', {'contact': cr, 'sent': True})
#     else:
#         form = ContactMessageForm()
#     return render(request, 'pets/contact_owner.html', {'contact': cr, 'form': form})


# @login_required
# def owner_inbox(request):
#     """List mediated contact requests for the logged-in pet owner."""
#     from .models import ContactRequest
#     # list contact requests where the owner of the matched pet is the current user
#     contacts = ContactRequest.objects.filter(match_request__pet__owner=request.user).order_by('-created_at')
#     return render(request, 'pets/owner_inbox.html', {'contacts': contacts})


# def image_check(request):
#     """Upload an image and check whether it (or a visually similar image) exists in the database.

#     Attempts a perceptual hash comparison when `imagehash` is available, falling
#     back to filename/path checks otherwise. Shows matches and provides a link
#     back to the site home page.
#     """
#     from .forms import ImageCheckForm
#     from .models import Pet

#     matches = []
#     uploaded_hash = None
#     uploaded_name = None

#     if request.method == 'POST':
#         form = ImageCheckForm(request.POST, request.FILES)
#         if form.is_valid():
#             img = form.cleaned_data['image']
#             uploaded_name = getattr(img, 'name', '')

#             # Try to compute perceptual hash if possible
#             try:
#                 from PIL import Image
#                 import imagehash
#             except Exception:
#                 imagehash = None

#             temp_path = None
#             try:
#                 # Save to a temp location under MEDIA_ROOT so we can open by path
#                 tmp_dir = None
#                 try:
#                     tmp_dir = os.path.join(settings.MEDIA_ROOT, 'tmp_checks')
#                     os.makedirs(tmp_dir, exist_ok=True)
#                     temp_path = os.path.join(tmp_dir, uploaded_name)
#                     with open(temp_path, 'wb') as f:
#                         for chunk in img.chunks():
#                             f.write(chunk)
#                 except Exception:
#                     temp_path = None

#                 if imagehash is not None and temp_path:
#                     try:
#                         with Image.open(temp_path) as im:
#                             h = imagehash.phash(im)
#                             uploaded_hash = h.__str__()
#                     except Exception:
#                         uploaded_hash = None

#                 # If we have a hash, search by hamming distance in dataset (status='available')
#                 if uploaded_hash:
#                     for candidate in Pet.objects.filter(status='available').exclude(image_hash__isnull=True).exclude(image_hash=''):
#                         try:
#                             d = imagehash.hex_to_hash(candidate.image_hash) - imagehash.hex_to_hash(uploaded_hash)
#                         except Exception:
#                             d = None
#                         if d is not None and d <= 8:
#                             matches.append({'pet': candidate, 'distance': d})

#                 # Also try to find exact filename matches (useful when importing files)
#                 if not matches and uploaded_name:
#                     qs = Pet.objects.filter(image__icontains=uploaded_name)
#                     for c in qs:
#                         matches.append({'pet': c, 'distance': None})

#             finally:
#                 # Don't remove files here; keep tmp for debugging. Optionally clean up.
#                 pass
#         else:
#             messages.error(request, 'Please upload a valid image file.')
#     else:
#         form = ImageCheckForm()

#     return render(request, 'pets/image_check.html', {
#         'form': form,
#         'matches': matches,
#         'uploaded_hash': uploaded_hash,
#         'uploaded_name': uploaded_name,
#     })



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Pet
from .forms import ReportPetForm
import os


# -------------------------------------------
# ADMIN PENDING VIEW (FIXED & CLEAN)
# -------------------------------------------
@login_required
def admin_pending(request):
    """Admin view to manage pending pet reports."""
    if not request.user.is_superuser:
        return render(request, 'pets/admin_pending.html', {
            'error': 'Access denied. Admin privileges required.'
        })

    if request.method == 'POST':
        pet_id = request.POST.get('pet_id')
        action = request.POST.get('action')

        try:
            pet = Pet.objects.get(id=pet_id, approval_status='pending')

            if action == 'approve':
                pet.approval_status = 'approved'
                messages.success(request, f'Pet "{pet.name}" has been approved.')

            elif action == 'reject':
                pet.approval_status = 'rejected'
                messages.success(request, f'Pet "{pet.name}" has been rejected.')

            pet.save()

        except Pet.DoesNotExist:
            messages.error(request, 'Pet not found or already processed.')

        return redirect('pets:admin_pending')

    pending_pets = Pet.objects.filter(approval_status='pending').order_by('-created_at')

    return render(request, 'pets/admin_pending.html', {
        'pending_pets': pending_pets,
        'total_pets': Pet.objects.count(),
        'approved_pets': Pet.objects.filter(approval_status='approved').count(),
        'rejected_pets': Pet.objects.filter(approval_status='rejected').count(),
        'pending_count': pending_pets.count(),
    })


# -------------------------------------------
# REPORT PET VIEW (FULL + MATCHING LOGIC)
# -------------------------------------------
@login_required
def report_pet(request):
    from pets.models import MatchRequest
    from pets.forms import ImageCheckForm

    try:
        import imagehash
        from PIL import Image
    except:
        imagehash = None

    if request.method == 'POST':
        form = ReportPetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user
            pet.approval_status = 'pending'
            pet.save()

            # ------------------------------
            # IMAGE HASH CHECKING (LOST PET)
            # ------------------------------
            if pet.status == 'lost' and pet.image_hash and imagehash:
                dataset_matches = Pet.objects.filter(
                    status='available'
                ).exclude(image_hash__isnull=True).exclude(image_hash='')

                present = False
                for candidate in dataset_matches:
                    try:
                        d = imagehash.hex_to_hash(candidate.image_hash) - imagehash.hex_to_hash(pet.image_hash)
                        if d is not None and d <= 8:
                            present = True
                            break
                    except:
                        continue

                if present:
                    messages.info(request, 'The uploaded image is present in the database.')
                else:
                    messages.info(request, 'The uploaded image is NOT present in the database.')

            # ------------------------------
            # AUTOMATCHING FOR FOUND PETS
            # ------------------------------
            if pet.status == 'found':
                matches = []

                # Hash match (phash)
                if imagehash is not None and pet.image_hash:
                    lost_pets = Pet.objects.filter(status='lost').exclude(image_hash__isnull=True)
                    for candidate in lost_pets:
                        try:
                            d = imagehash.hex_to_hash(candidate.image_hash) - imagehash.hex_to_hash(pet.image_hash)
                            if d is not None and d <= 8:
                                matches.append(candidate)
                        except:
                            pass

                # ORB Matching fallback
                if not matches:
                    try:
                        from pets.utils import opencv_orb_match_score
                        candidates = Pet.objects.filter(status='lost').exclude(image__isnull=True)
                        scored = []
                        for c in candidates:
                            if not c.image:
                                continue
                            score = opencv_orb_match_score(pet.image.path, c.image.path)
                            if score and score > 10:
                                scored.append((score, c))

                        scored.sort(reverse=True)
                        matches = [c for score, c in scored[:10]]
                    except:
                        pass

                # Embedding matching fallback
                if not matches:
                    try:
                        from pets.embeddings import find_similar_embeddings
                        emb_dir = os.path.join(settings.MEDIA_ROOT, 'embeddings')
                        results = find_similar_embeddings(pet.image.path, emb_dir, top_k=10)

                        emb_matches = []
                        for score, fname in results:
                            pid = int(fname.split('_')[1].split('.')[0])
                            c = Pet.objects.filter(id=pid, status='lost').first()
                            if c:
                                emb_matches.append(c)

                        if emb_matches:
                            matches = emb_matches

                    except:
                        pass

                # If any matches found, create MatchRequest + email owners
                if matches:
                    from django.template.loader import render_to_string
                    from django.core.mail import send_mail
                    from django.urls import reverse

                    created = []
                    for candidate in matches:
                        mr = MatchRequest.objects.create(
                            pet=candidate,
                            reporter=request.user,
                            found_pet=pet,
                            confidence=None,
                            reason='automatched'
                        )
                        created.append(mr)

                        approve_url = request.build_absolute_uri(reverse('pets:match_approve', args=[mr.token]))
                        reject_url = request.build_absolute_uri(reverse('pets:match_reject', args=[mr.token]))

                        message = render_to_string('pets/match_email.txt', {
                            'owner': candidate.owner,
                            'pet': candidate,
                            'found_pet': pet,
                            'reporter': request.user,
                            'approve_url': approve_url,
                            'reject_url': reject_url,
                        })

                        send_mail(
                            f"Possible match found for your pet {candidate.name}",
                            message,
                            None,
                            [candidate.owner.email]
                        )

                    return render(request, 'pets/match_sent.html', {
                        'pet': pet,
                        'created_requests': created
                    })

                return render(request, 'pets/match_results.html', {
                    'pet': pet,
                    'matches': matches
                })

            return redirect('home')
    else:
        form = ReportPetForm()

    return render(request, 'pets/report_pet.html', {'form': form})


# -------------------------------------------
# MATCH APPROVE / REJECT
# -------------------------------------------
def match_approve(request, token):
    from pets.models import MatchRequest, ContactRequest
    mr = get_object_or_404(MatchRequest, token=token)

    if request.user.is_authenticated and request.user == mr.pet.owner:
        mr.status = 'owner_approved'
        mr.save()

        cr = ContactRequest.objects.create(match_request=mr)

        from django.core.mail import send_mail
        from django.urls import reverse

        contact_url = request.build_absolute_uri(reverse('pets:contact_request', args=[cr.id]))
        send_mail(
            f"Owner approved contact for {mr.pet.name}",
            f"Contact the owner here: {contact_url}",
            None,
            [mr.reporter.email]
        )

        return render(request, 'pets/match_confirm.html', {'match': mr, 'contact_request': cr})

    return render(request, 'pets/match_confirm.html', {'match': mr, 'error': 'Not authorized'})


def match_reject(request, token):
    from pets.models import MatchRequest
    mr = get_object_or_404(MatchRequest, token=token)

    if request.user.is_authenticated and request.user == mr.pet.owner:
        mr.status = 'owner_rejected'
        mr.save()
        return render(request, 'pets/match_rejected.html', {'match': mr})

    return render(request, 'pets/match_rejected.html', {'match': mr, 'error': 'Not authorized'})


# -------------------------------------------
# CONTACT RELAY VIEWS
# -------------------------------------------
@login_required
def contact_request_view(request, cr_id):
    from pets.models import ContactRequest, ContactMessage
    cr = get_object_or_404(ContactRequest, id=cr_id)

    if request.user != cr.match_request.reporter:
        return render(request, 'pets/contact_request.html', {'error': 'Not authorized'})

    if request.method == 'POST':
        text = request.POST.get('message', '').strip()
        if text:
            ContactMessage.objects.create(contact=cr, sender=request.user, message=text)

            # Email relay to owner
            owner_email = cr.match_request.pet.owner.email
            if owner_email:
                from django.core.mail import send_mail
                send_mail(
                    f"Message about your pet {cr.match_request.pet.name}",
                    text,
                    None,
                    [owner_email]
                )

        return render(request, 'pets/contact_request.html', {'contact': cr, 'sent': True})

    return render(request, 'pets/contact_request.html', {'contact': cr})


@login_required
def contact_owner_view(request, cr_id):
    from pets.models import ContactRequest, ContactMessage
    from pets.forms import ContactMessageForm

    cr = get_object_or_404(ContactRequest, id=cr_id)

    if request.user != cr.match_request.pet.owner:
        return render(request, 'pets/contact_owner.html', {'error': 'Not authorized'})

    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            msg = form.cleaned_data['message']
            ContactMessage.objects.create(contact=cr, sender=request.user, message=msg)

            reporter_email = cr.match_request.reporter.email
            if reporter_email:
                from django.core.mail import send_mail
                send_mail(f"Reply regarding {cr.match_request.pet.name}", msg, None, [reporter_email])

            return render(request, 'pets/contact_owner.html', {'contact': cr, 'sent': True})
    else:
        form = ContactMessageForm()

    return render(request, 'pets/contact_owner.html', {'contact': cr, 'form': form})


# -------------------------------------------
# OWNER INBOX
# -------------------------------------------
@login_required
def owner_inbox(request):
    from pets.models import ContactRequest
    contacts = ContactRequest.objects.filter(
        match_request__pet__owner=request.user
    ).order_by('-created_at')

    return render(request, 'pets/owner_inbox.html', {'contacts': contacts})


# -------------------------------------------
# IMAGE CHECK TOOL
# -------------------------------------------
def image_check(request):
    from pets.forms import ImageCheckForm

    matches = []
    uploaded_hash = None
    uploaded_name = None

    if request.method == 'POST':
        form = ImageCheckForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.cleaned_data['image']
            uploaded_name = img.name

            try:
                from PIL import Image
                import imagehash
            except:
                imagehash = None

            temp_path = None
            try:
                tmp_dir = os.path.join(settings.MEDIA_ROOT, 'tmp_checks')
                os.makedirs(tmp_dir, exist_ok=True)

                temp_path = os.path.join(tmp_dir, uploaded_name)
                with open(temp_path, 'wb') as f:
                    for chunk in img.chunks():
                        f.write(chunk)

                # phash
                if imagehash:
                    try:
                        with Image.open(temp_path) as im:
                            uploaded_hash = str(imagehash.phash(im))
                    except:
                        uploaded_hash = None

                if uploaded_hash:
                    for candidate in Pet.objects.filter(status='available').exclude(image_hash=''):
                        try:
                            d = imagehash.hex_to_hash(candidate.image_hash) - imagehash.hex_to_hash(uploaded_hash)
                            if d is not None and d <= 8:
                                matches.append({'pet': candidate, 'distance': d})
                        except:
                            pass
                
                if not matches:
                    qs = Pet.objects.filter(image__icontains=uploaded_name)
                    for c in qs:
                        matches.append({'pet': c, 'distance': None})

            except:
                pass
    else:
        form = ImageCheckForm()
    
    return render(request, 'pets/image_check.html', {
        'form': form,
        'matches': matches,
        'uploaded_hash': uploaded_hash,
        'uploaded_name': uploaded_name,
    })


# -------------------------------------------
# PET LISTING VIEWS BY CATEGORY
# -------------------------------------------

def lost_pets(request):
    """Display all approved lost pets."""
    pets = Pet.objects.filter(
        status='lost', 
        approval_status='approved'
    ).order_by('-created_at')
    
    return render(request, 'pets/lost_pets.html', {
        'pets': pets,
        'page_title': 'Lost Pets',
        'page_description': 'Help reunite these lost pets with their families'
    })


def found_pets(request):
    """Display all approved found pets."""
    pets = Pet.objects.filter(
        status='found', 
        approval_status='approved'
    ).order_by('-created_at')
    
    return render(request, 'pets/found_pets.html', {
        'pets': pets,
        'page_title': 'Found Pets',
        'page_description': 'These pets have been found and are looking for their owners'
    })


def adoption_pets(request):
    """Display all approved pets available for adoption."""
    pets = Pet.objects.filter(
        status='adoption', 
        approval_status='approved'
    ).order_by('-created_at')
    
    return render(request, 'pets/adoption_pets.html', {
        'pets': pets,
        'page_title': 'Pets Available for Adoption',
        'page_description': 'Give these wonderful pets a loving home'
    })


# -------------------------------------------
# PET SEARCH AND INQUIRY VIEWS
# -------------------------------------------

@login_required
def search_pets(request):
    """Search for both lost and found pets based on user criteria."""
    from .forms import PetSearchForm
    from .models import PetSearchQuery, AdminNotification
    from django.db.models import Q
    
    form = PetSearchForm()
    pets = []
    search_performed = False
    
    if request.method == 'POST':
        form = PetSearchForm(request.POST)
        if form.is_valid():
            search_performed = True
            
            # Build search query - include both lost and found pets that are approved
            query = Q(approval_status='approved') & (Q(status='lost') | Q(status='found'))
            
            # Add filters based on form data
            if form.cleaned_data.get('species'):
                query &= Q(species__icontains=form.cleaned_data['species'])
            
            if form.cleaned_data.get('breed'):
                query &= Q(breed__icontains=form.cleaned_data['breed'])
            
            if form.cleaned_data.get('color'):
                query &= Q(color__icontains=form.cleaned_data['color'])
            
            if form.cleaned_data.get('location'):
                query &= Q(location__icontains=form.cleaned_data['location'])
            
            if form.cleaned_data.get('gender'):
                query &= Q(gender=form.cleaned_data['gender'])
            
            if form.cleaned_data.get('age_min'):
                query &= Q(age__gte=form.cleaned_data['age_min'])
            
            if form.cleaned_data.get('age_max'):
                query &= Q(age__lte=form.cleaned_data['age_max'])
            
            # Execute search and separate results by status
            all_pets = Pet.objects.filter(query).order_by('-created_at')
            pets = {
                'found': all_pets.filter(status='found'),
                'lost': all_pets.filter(status='lost'),
                'total_count': all_pets.count()
            }
            
            # Save search query for tracking
            search_query = PetSearchQuery.objects.create(
                user=request.user,
                species=form.cleaned_data.get('species', ''),
                breed=form.cleaned_data.get('breed', ''),
                color=form.cleaned_data.get('color', ''),
                location=form.cleaned_data.get('location', ''),
                gender=form.cleaned_data.get('gender', ''),
                age_min=form.cleaned_data.get('age_min'),
                age_max=form.cleaned_data.get('age_max'),
                results_count=pets['total_count']
            )
            
            # Create admin notification for search inquiry
            AdminNotification.objects.create(
                notification_type='search_inquiry',
                title=f'New Pet Search by {request.user.username}',
                message=f'User {request.user.username} searched for pets with criteria: {form.cleaned_data}. Found {pets["total_count"]} results.',
                user=request.user,
                search_query=search_query
            )
    
    return render(request, 'pets/search_pets.html', {
        'form': form,
        'pets': pets,
        'search_performed': search_performed,
        'page_title': 'Search for Your Lost Pet',
        'page_description': 'Search through reported pets to see if your lost pet has been found or reported by others'
    })


@login_required
def pet_inquiry(request, pet_id):
    """Allow users to inquire about a specific pet."""
    from .forms import PetInquiryForm
    from .models import PetInquiry, AdminNotification
    from django.contrib import messages
    
    pet = get_object_or_404(Pet, id=pet_id, status='found', approval_status='approved')
    
    # Check if user already made an inquiry about this pet
    existing_inquiry = PetInquiry.objects.filter(inquirer=request.user, pet=pet).first()
    
    if request.method == 'POST':
        if existing_inquiry:
            messages.warning(request, 'You have already made an inquiry about this pet.')
            return redirect('pets:pet_inquiry', pet_id=pet.id)
        
        form = PetInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.inquirer = request.user
            inquiry.pet = pet
            inquiry.save()
            
            # Create admin notification
            AdminNotification.objects.create(
                notification_type='contact_request',
                title=f'New Pet Inquiry from {request.user.username}',
                message=f'User {request.user.username} made an inquiry about {pet.name} (ID: {pet.id}). Contact: {inquiry.contact_email}',
                user=request.user,
                pet=pet
            )
            
            messages.success(request, 'Your inquiry has been submitted successfully. The admin will review it and facilitate contact with the pet finder.')
            return redirect('pets:found_pets')
    else:
        form = PetInquiryForm()
    
    return render(request, 'pets/pet_inquiry.html', {
        'form': form,
        'pet': pet,
        'existing_inquiry': existing_inquiry,
        'page_title': f'Inquire about {pet.name}',
        'page_description': f'Send an inquiry about {pet.name} to see if this is your lost pet'
    })


@login_required
def admin_notifications(request):
    """Admin view to see all notifications."""
    from .models import AdminNotification
    
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    # Mark notifications as read when viewed
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        if notification_id:
            try:
                notification = AdminNotification.objects.get(id=notification_id)
                notification.is_read = True
                notification.save()
                messages.success(request, 'Notification marked as read.')
            except AdminNotification.DoesNotExist:
                messages.error(request, 'Notification not found.')
        return redirect('pets:admin_notifications')
    
    notifications = AdminNotification.objects.all().order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    return render(request, 'pets/admin_notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count,
        'page_title': 'Admin Notifications',
        'page_description': 'Manage system notifications and user activities'
    })


@login_required
def admin_inquiries(request):
    """Admin view to manage pet inquiries."""
    from .models import PetInquiry
    
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    if request.method == 'POST':
        inquiry_id = request.POST.get('inquiry_id')
        action = request.POST.get('action')
        
        try:
            inquiry = PetInquiry.objects.get(id=inquiry_id)
            if action == 'mark_responded':
                inquiry.status = 'responded'
                inquiry.save()
                messages.success(request, f'Inquiry marked as responded.')
            elif action == 'close':
                inquiry.status = 'closed'
                inquiry.save()
                messages.success(request, f'Inquiry closed.')
        except PetInquiry.DoesNotExist:
            messages.error(request, 'Inquiry not found.')
        
        return redirect('pets:admin_inquiries')
    
    inquiries = PetInquiry.objects.all().order_by('-created_at')
    pending_count = inquiries.filter(status='pending').count()
    
    return render(request, 'pets/admin_inquiries.html', {
        'inquiries': inquiries,
        'pending_count': pending_count,
        'page_title': 'Pet Inquiries Management',
        'page_description': 'Manage user inquiries about found pets'
    })

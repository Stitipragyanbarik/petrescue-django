from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .forms import CustomUserCreationForm
from .utils import (
    generate_otp, 
    send_otp_sms, 
    store_otp_in_session, 
    verify_otp_from_session, 
    clear_otp_session,
    format_phone_number
)


def home(request):
    return render(request, 'accounts/home.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out successfully.')
    return redirect('home')


def register(request):
    if request.method == 'POST':
        # Check if this is OTP verification step
        if 'verify_otp' in request.POST:
            return handle_otp_verification(request)
        
        # Check if this is requesting OTP step
        if 'request_otp' in request.POST:
            return handle_otp_request(request)
        
        # Regular form submission (initial registration)
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            # Store form data in session for later use after OTP verification
            request.session['registration_data'] = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'user_type': form.cleaned_data['user_type'],
                'phone_number': form.cleaned_data['phone_number'],
                'password1': form.cleaned_data['password1'],
                'password2': form.cleaned_data['password2'],
            }
            
            # Format and generate OTP
            phone_number = format_phone_number(form.cleaned_data['phone_number'])
            otp = generate_otp()
            
            # Send OTP
            if send_otp_sms(phone_number, otp):
                store_otp_in_session(request, phone_number, otp)
                messages.info(request, f'OTP sent to {phone_number}. Please verify to complete registration.')
                return render(request, 'accounts/register.html', {
                    'form': form, 
                    'show_otp': True,
                    'phone_number': phone_number
                })
            else:
                messages.error(request, 'Failed to send OTP. Please try again.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
        # Clear any existing registration data
        if 'registration_data' in request.session:
            del request.session['registration_data']
        clear_otp_session(request)

    return render(request, 'accounts/register.html', {'form': form})


def handle_otp_request(request):
    """Handle OTP resend request"""
    registration_data = request.session.get('registration_data')
    if not registration_data:
        messages.error(request, 'Registration session expired. Please start over.')
        return redirect('register')
    
    phone_number = format_phone_number(registration_data['phone_number'])
    otp = generate_otp()
    
    if send_otp_sms(phone_number, otp):
        store_otp_in_session(request, phone_number, otp)
        messages.info(request, f'New OTP sent to {phone_number}.')
    else:
        messages.error(request, 'Failed to send OTP. Please try again.')
    
    # Recreate form with stored data
    form = CustomUserCreationForm(initial=registration_data)
    return render(request, 'accounts/register.html', {
        'form': form, 
        'show_otp': True,
        'phone_number': phone_number
    })


def handle_otp_verification(request):
    """Handle OTP verification"""
    registration_data = request.session.get('registration_data')
    if not registration_data:
        messages.error(request, 'Registration session expired. Please start over.')
        return redirect('register')
    
    entered_otp = request.POST.get('otp', '').strip()
    phone_number = format_phone_number(registration_data['phone_number'])
    
    if not entered_otp:
        messages.error(request, 'Please enter the OTP.')
        form = CustomUserCreationForm(initial=registration_data)
        return render(request, 'accounts/register.html', {
            'form': form, 
            'show_otp': True,
            'phone_number': phone_number
        })
    
    is_valid, message = verify_otp_from_session(request, entered_otp, phone_number)
    
    if is_valid:
        # OTP verified, create user
        form = CustomUserCreationForm(registration_data)
        if form.is_valid():
            user = form.save()
            
            # Clear session data
            if 'registration_data' in request.session:
                del request.session['registration_data']
            clear_otp_session(request)
            
            # Log in the user
            login(request, user)
            messages.success(request, 'Registration successful! Phone number verified.')
            return redirect('home')
        else:
            messages.error(request, 'Registration data is invalid. Please start over.')
            return redirect('register')
    else:
        messages.error(request, message)
        form = CustomUserCreationForm(initial=registration_data)
        return render(request, 'accounts/register.html', {
            'form': form, 
            'show_otp': True,
            'phone_number': phone_number
        })


@csrf_exempt
def send_otp_ajax(request):
    """AJAX endpoint for sending OTP"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone_number = data.get('phone_number', '').strip()
            
            if not phone_number:
                return JsonResponse({'success': False, 'message': 'Phone number is required.'})
            
            formatted_phone = format_phone_number(phone_number)
            otp = generate_otp()
            
            if send_otp_sms(formatted_phone, otp):
                store_otp_in_session(request, formatted_phone, otp)
                return JsonResponse({
                    'success': True, 
                    'message': f'OTP sent to {formatted_phone}',
                    'phone_number': formatted_phone
                })
            else:
                return JsonResponse({'success': False, 'message': 'Failed to send OTP. Please try again.'})
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid request data.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'An error occurred. Please try again.'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})




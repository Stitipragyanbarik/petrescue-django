from django.urls import path
from . import views

app_name = 'pets'

urlpatterns = [
    path('report/', views.report_pet, name='report_pet'),
    path('admin/pending/', views.admin_pending, name='admin_pending'),
    path('match/<uuid:token>/approve/', views.match_approve, name='match_approve'),
    path('match/<uuid:token>/reject/', views.match_reject, name='match_reject'),
    path('contact/<int:cr_id>/', views.contact_request_view, name='contact_request'),
    path('contact/<int:cr_id>/owner/', views.contact_owner_view, name='contact_owner'),
    path('contact/inbox/', views.owner_inbox, name='owner_inbox'),
    path('image-check/', views.image_check, name='image_check'),
    # Pet listing views
    path('lost/', views.lost_pets, name='lost_pets'),
    path('found/', views.found_pets, name='found_pets'),
    path('adoption/', views.adoption_pets, name='adoption_pets'),
    # Pet Search and Inquiry URLs
    path('search/', views.search_pets, name='search_pets'),
    path('inquiry/<int:pet_id>/', views.pet_inquiry, name='pet_inquiry'),
    path('admin/notifications/', views.admin_notifications, name='admin_notifications'),
    path('admin/inquiries/', views.admin_inquiries, name='admin_inquiries'),
]

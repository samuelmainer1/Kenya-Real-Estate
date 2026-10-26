from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.db import models
from .choices import price_choices, bedroom_choices, state_choices
from .models import Listing, Booking
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, time
import json

def index(request):
    listings = Listing.objects.public().order_by('-list_date')
    
    # Get counts for category buttons
    total_count = listings.count()
    sale_count = listings.filter(property_type='sale').count()
    rent_count = listings.filter(property_type='rent').count()
    airbnb_count = listings.filter(property_type='airbnb').count()
    
    paginator = Paginator(listings, 6)
    page = request.GET.get('page')
    paged_listings = paginator.get_page(page)
    
    context = {
        'listings': paged_listings,
        'bedroom_choices': bedroom_choices,
        'price_choices': price_choices,
        'state_choices': state_choices,
        'total_count': total_count,
        'sale_count': sale_count,
        'rent_count': rent_count,
        'airbnb_count': airbnb_count,
    }
    
    return render(request, 'listings/listings.html', context)


def listing_by_slug(request, slug):
    if not slug:
        raise Http404("Listing not found.")

    listing = Listing.objects.public().filter(slug=slug).first()

    if listing is None:
        # Slug not found: fall back to a title/slug similarity match so old
        # links keep working, otherwise 404 cleanly (never 500).
        similar_listing = Listing.objects.public().filter(
            Q(title__icontains=slug.replace('-', ' ')) |
            Q(slug__icontains=slug),
        ).first()

        if similar_listing:
            return redirect('listing', slug=similar_listing.slug)

        raise Http404("Listing not found.")
    
    # Get related listings using the model method
    related_listings = listing.get_related_listings(limit=4)
    
    # Get available time slots for booking
    available_times = [
        '09:00', '10:00', '11:00', '12:00', 
        '13:00', '14:00', '15:00', '16:00', '17:00'
    ]
    
    context = {
        'listing': listing,
        'related_listings': related_listings,
        'available_times': available_times
    }
    
    return render(request, 'listings/listing.html', context)


@login_required
def create_booking(request, listing_id):
    if request.method == 'POST':
        listing = get_object_or_404(Listing, id=listing_id, is_published=True, realtor__is_verified=True)
        client_email = request.POST.get('client_email')
        client_phone = request.POST.get('client_phone')
        
        if not client_email or not client_phone:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('listing', slug=listing.slug)
        
        if listing.property_type == 'airbnb':
            # Handle Airbnb booking
            check_in_date = request.POST.get('check_in_date')
            check_out_date = request.POST.get('check_out_date')
            check_in_time = request.POST.get('check_in_time', '15:00')
            check_out_time = request.POST.get('check_out_time', '11:00')

            if not check_in_date or not check_out_date:
                messages.error(request, 'Please select check-in and check-out dates.')
                return redirect('listing', slug=listing.slug)

            # Validate check-in is before check-out
            try:
                check_in = datetime.strptime(check_in_date, '%Y-%m-%d').date()
                check_out = datetime.strptime(check_out_date, '%Y-%m-%d').date()
                if check_in >= check_out:
                    messages.error(request, 'Check-out date must be after check-in date.')
                    return redirect('listing', slug=listing.slug)
            except ValueError:
                messages.error(request, 'Invalid date format.')
                return redirect('listing', slug=listing.slug)

            # Validate dates are not in the past
            from datetime import date as date_class
            today = date_class.today()
            check_in_date_obj = datetime.strptime(check_in_date, '%Y-%m-%d').date()
            check_out_date_obj = datetime.strptime(check_out_date, '%Y-%m-%d').date()

            if check_in_date_obj < today:
                messages.error(request, 'Check-in date cannot be in the past.')
                return redirect('listing', slug=listing.slug)

            if check_out_date_obj <= check_in_date_obj:
                messages.error(request, 'Check-out date must be after check-in date.')
                return redirect('listing', slug=listing.slug)

            # Convert to datetime for proper comparison
            check_in_datetime = datetime.combine(
                datetime.strptime(check_in_date, '%Y-%m-%d').date(),
                datetime.strptime(check_in_time, '%H:%M').time()
            )
            check_out_datetime = datetime.combine(
                datetime.strptime(check_out_date, '%Y-%m-%d').date(),
                datetime.strptime(check_out_time, '%H:%M').time()
            )
            
            # Check for overlapping bookings - more precise logic
            overlapping_bookings = Booking.objects.filter(
                listing=listing,
                status__in=['pending', 'confirmed']
            ).exclude(
                # Exclude if new booking ends before existing starts
                Q(check_out_date__lt=check_in_date) |
                Q(check_out_date=check_in_date, check_out_time__lte=check_in_time) |
                # Exclude if new booking starts after existing ends
                Q(check_in_date__gt=check_out_date) |
                Q(check_in_date=check_out_date, check_in_time__gte=check_out_time)
            ).exists()
            
            if overlapping_bookings:
                messages.error(request, 'This property is not available for the selected dates and times.')
                return redirect('listing', slug=listing.slug)
            
            booking = Booking.objects.create(
                listing=listing,
                client=request.user,
                client_email=client_email,
                client_phone=client_phone,
                booking_type='airbnb',
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                check_in_time=check_in_time,
                check_out_time=check_out_time
            )

            messages.success(request, f'Airbnb booking confirmed from {check_in_date} {check_in_time} to {check_out_date} {check_out_time}.')
        else:
            # Handle regular viewing booking
            date = request.POST.get('date')
            time = request.POST.get('time')

            if not date or not time:
                messages.error(request, 'Please select date and time.')
                return redirect('listing', slug=listing.slug)

            existing_booking = Booking.objects.filter(
                listing=listing,
                date=date,
                time=time,
                booking_type='viewing'
            ).exists()

            if existing_booking:
                messages.error(request, 'This time slot is already booked.')
                return redirect('listing', slug=listing.slug)

            booking = Booking.objects.create(
                listing=listing,
                client=request.user,
                client_email=client_email,
                client_phone=client_phone,
                booking_type='viewing',
                date=date,
                time=time
            )

            messages.success(request, f'Property viewing booked for {date} at {time}.')
        
        return redirect('listing', slug=listing.slug)
    
    return redirect('listings')

def get_available_times(request, listing_id):
    """AJAX endpoint to get available times for a specific date"""
    if request.method == 'GET':
        date = request.GET.get('date')
        if not date:
            return JsonResponse({'error': 'Date is required'}, status=400)
        
        listing = get_object_or_404(Listing, id=listing_id, is_published=True, realtor__is_verified=True)
        
        # All possible time slots
        all_times = [
            '09:00', '10:00', '11:00', '12:00', 
            '13:00', '14:00', '15:00', '16:00', '17:00'
        ]
        
        # Get booked times for this date
        booked_times = Booking.objects.filter(
            listing=listing,
            date=date
        ).values_list('time', flat=True)
        
        # Convert time objects to strings
        booked_time_strings = [t.strftime('%H:%M') for t in booked_times]
        
        # Filter out booked times
        available_times = [t for t in all_times if t not in booked_time_strings]
        
        return JsonResponse({'available_times': available_times})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def get_available_dates(request, listing_id):
    """AJAX endpoint for Airbnb availability"""
    if request.method == 'GET':
        listing = get_object_or_404(Listing, id=listing_id, is_published=True, realtor__is_verified=True)
        
        if listing.property_type != 'airbnb':
            return JsonResponse({'error': 'Not an Airbnb property'}, status=400)
        
        # Get booked date ranges
        bookings = Booking.objects.filter(
            listing=listing,
            status__in=['pending', 'confirmed']
        ).values('check_in_date', 'check_out_date')
        
        unavailable_ranges = [
            {
                'start': booking['check_in_date'].isoformat(),
                'end': booking['check_out_date'].isoformat()
            }
            for booking in bookings if booking['check_in_date'] and booking['check_out_date']
        ]
        
        return JsonResponse({'unavailable_ranges': unavailable_ranges})

def listing_legacy_by_id(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    return HttpResponseRedirect(reverse('listing', kwargs={'slug': listing.slug}))


def search(request):
    queryset_list = Listing.objects.public().order_by('-list_date')
    
    # Get counts for each property type for the category buttons
    total_count = queryset_list.count()
    sale_count = queryset_list.filter(property_type='sale').count()
    rent_count = queryset_list.filter(property_type='rent').count()
    airbnb_count = queryset_list.filter(property_type='airbnb').count()
    
    # Store original counts before filtering
    property_counts = {
        'sale': sale_count,
        'rent': rent_count,
        'airbnb': airbnb_count,
    }
    
    # Keywords - search in title and description
    if 'keywords' in request.GET:
        keywords = request.GET['keywords']
        if keywords:
            queryset_list = queryset_list.filter(
                Q(title__icontains=keywords) | Q(description__icontains=keywords)
            )
    
    # Property Type
    if 'property_type' in request.GET:
        property_type = request.GET['property_type']
        if property_type:
            queryset_list = queryset_list.filter(property_type=property_type)
    
    # City
    if 'city' in request.GET:
        city = request.GET['city']
        if city:
            queryset_list = queryset_list.filter(city__iexact=city)
    
    # State
    if 'state' in request.GET:
        state = request.GET['state']
        if state:
            queryset_list = queryset_list.filter(state__iexact=state)
    
    # Bedrooms
    if 'bedrooms' in request.GET:
        bedrooms = request.GET['bedrooms']
        if bedrooms:
            queryset_list = queryset_list.filter(bedrooms__lte=bedrooms)
    
    # Price
    if 'price' in request.GET:
        price = request.GET['price']
        if price:
            queryset_list = queryset_list.filter(price__lte=price)
    
    context = {
        'state_choices': state_choices,
        'bedroom_choices': bedroom_choices,
        'price_choices': price_choices,
        'property_type_choices': Listing.PROPERTY_TYPES,
        'listings': queryset_list,
        'values': request.GET,
        'total_count': total_count,
        'property_counts': property_counts,
    }
    
    return render(request, 'listings/search.html', context)

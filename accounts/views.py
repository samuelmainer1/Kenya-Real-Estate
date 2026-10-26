from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q

from contacts.models import Contact
from listings.models import Booking
from testimonials.models import Testimonial

def register(request):
    if request.method == 'POST':
        # Get form values
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        # Check if passwords match
        if password == password2:
            # Check username
            if User.objects.filter(username=username).exists():
                messages.error(request, 'That username is taken')
                return redirect('register')
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'That email is being used')
                    return redirect('register')
                else:
                    # Looks good
                    user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
                    user.save()
                    messages.success(request, 'You are now registered and can log in')
                    return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
    else:
        return render(request, 'accounts/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
            return render(request, 'accounts/login.html')
    else:
        return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You are now logged out')
    return redirect('index')

@login_required
def dashboard(request):
    """Client dashboard: bookings, inquiries and reviews in one place.

    The previous version passed a single unfiltered ``bookings`` list to the
    template and filtered with ``{% if booking.booking_type == ... %}`` inside
    the loop. That rendered every booking in *both* tables, and the "you have
    no bookings yet" alerts never appeared because the condition tested the
    unfiltered list. The querysets are split here instead, so each section only
    ever sees its own rows.
    """
    bookings = (
        Booking.objects.filter(client=request.user)
        .select_related('listing', 'listing__realtor')
        .order_by('-created_at')
    )

    viewings = bookings.filter(booking_type='viewing')
    stays = bookings.filter(booking_type='airbnb')

    today = date.today()

    # The next thing happening, so the client sees the most relevant item first.
    next_viewing = viewings.filter(
        status__in=['pending', 'confirmed'], date__gte=today,
    ).order_by('date', 'time').first()

    next_stay = stays.filter(
        status__in=['pending', 'confirmed'], check_in_date__gte=today,
    ).order_by('check_in_date').first()

    upcoming = [
        b for b in (next_viewing, next_stay) if b is not None
    ]

    stats = bookings.aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='pending')),
        confirmed=Count('id', filter=Q(status='confirmed')),
        cancelled=Count('id', filter=Q(status='cancelled')),
    )

    context = {
        'viewings': viewings,
        'stays': stays,
        'next_up': upcoming,
        'stats': stats,
        'inquiries': (
            Contact.objects.filter(user=request.user)
            .order_by('-contact_date')[:5]
        ),
        'inquiry_count': Contact.objects.filter(user=request.user).count(),
        'testimonials': (
            Testimonial.objects.filter(client=request.user)
            .select_related('listing')
            .order_by('-created_at')[:5]
        ),
        'testimonial_count': Testimonial.objects.filter(client=request.user).count(),
        'today': today,
        # Tell base.html to render flash messages without the extra .container.
        'full_bleed_alerts': True,
    }

    return render(request, 'accounts/dashboard.html', context)


@login_required
def cancel_booking(request, booking_id):
    """Let a client withdraw their own pending/confirmed booking.

    Staff can still use the admin for anything else. Guard rails:
    * only the owner may cancel (404 for anyone else, so IDs are not probeable),
    * a completed stay ("checked_out") can never be cancelled,
    * cancellation is a status change, not a delete, so the record survives.
    """
    booking = get_object_or_404(Booking, id=booking_id, client=request.user)

    if request.method != 'POST':
        return redirect('dashboard')

    if booking.status not in ('pending', 'confirmed'):
        messages.error(request, 'This booking can no longer be cancelled.')
        return redirect('dashboard')

    if booking.booking_type == 'airbnb' and booking.check_in_date:
        if booking.check_in_date <= date.today():
            messages.error(
                request,
                'This stay has already started. Please contact us to change it.',
            )
            return redirect('dashboard')

    booking.status = 'cancelled'
    booking.save(update_fields=['status'])
    messages.success(request, 'Your booking has been cancelled.')
    return redirect('dashboard')


@login_required
def profile(request):
    """Update the client's own name/email. Username changes stay in the admin."""
    if request.method == 'POST':
        first_name = (request.POST.get('first_name') or '').strip()[:150]
        last_name = (request.POST.get('last_name') or '').strip()[:150]
        email = (request.POST.get('email') or '').strip()[:254]

        if email and User.objects.filter(email__iexact=email).exclude(pk=request.user.pk).exists():
            messages.error(request, 'That email is already used by another account.')
            return redirect('profile')

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save(update_fields=['first_name', 'last_name', 'email'])
        messages.success(request, 'Your profile has been updated.')
        return redirect('profile')

    return render(request, 'accounts/profile.html', {
        'today': date.today(),
        'full_bleed_alerts': True,
    })



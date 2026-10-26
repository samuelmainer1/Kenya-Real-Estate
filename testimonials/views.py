from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Testimonial
from .forms import TestimonialForm
from listings.models import Listing

def testimonials_list(request):
    """Display approved testimonials"""
    testimonials = Testimonial.objects.filter(status='approved').order_by('-created_at')
    featured_testimonials = testimonials.filter(is_featured=True)[:3]
    
    paginator = Paginator(testimonials, 6)  # Show 6 testimonials per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'testimonials': page_obj,
        'featured_testimonials': featured_testimonials,
    }
    return render(request, 'testimonials/testimonials_list.html', context)

def listing_testimonials(request, slug):
    """Display testimonials for a specific listing"""
    listing = get_object_or_404(Listing, slug=slug)
    testimonials = Testimonial.objects.filter(
        listing=listing, 
        status='approved'
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(testimonials, 6)
    page = request.GET.get('page')
    paged_testimonials = paginator.get_page(page)
    
    # Get featured testimonials for this listing
    featured_testimonials = testimonials.filter(is_featured=True)[:3]
    
    context = {
        'listing': listing,
        'testimonials': paged_testimonials,
        'featured_testimonials': featured_testimonials,
    }
    
    return render(request, 'testimonials/listing_testimonials.html', context)

@login_required
def add_testimonial(request, slug):
    """Allow authenticated users to add testimonials for a specific listing"""
    listing = get_object_or_404(Listing, slug=slug)
    
    # Check if user already reviewed this listing
    existing_review = Testimonial.objects.filter(
        listing=listing,
        client=request.user  # Changed from 'user' to 'client'
    ).first()
    
    if existing_review:
        messages.warning(request, 'You have already reviewed this property.')
        return redirect('listing', slug=slug)
    
    if request.method == 'POST':
        form = TestimonialForm(request.POST)
        if form.is_valid():
            testimonial = form.save(commit=False)
            testimonial.listing = listing
            testimonial.client = request.user  # Changed from 'user' to 'client'
            testimonial.save()
            
            messages.success(request, 'Thank you for your review! It will be published after approval.')
            return redirect('listing', slug=slug)
    else:
        # Pre-fill with user data if available
        initial_data = {
            'name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        }
        form = TestimonialForm(initial=initial_data)
    
    context = {
        'form': form,
        'listing': listing,
    }
    return render(request, 'testimonials/add_testimonial.html', context)

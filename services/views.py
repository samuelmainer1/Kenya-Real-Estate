from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Service

def services_list(request):
    """Display all active services"""
    services = Service.objects.filter(is_active=True).order_by('order', 'title')
    featured_services = services.filter(is_featured=True)[:6]
    
    # Pagination
    paginator = Paginator(services, 9)
    page = request.GET.get('page')
    paged_services = paginator.get_page(page)
    
    context = {
        'services': paged_services,
        'featured_services': featured_services,
    }
    return render(request, 'services/services_list.html', context)

def service_detail(request, slug):
    """Display single service detail"""
    service = get_object_or_404(Service, slug=slug, is_active=True)
    related_services = Service.objects.filter(
        is_active=True
    ).exclude(id=service.id).order_by('order')[:3]
    
    context = {
        'service': service,
        'related_services': related_services,
    }
    return render(request, 'services/service_detail.html', context)
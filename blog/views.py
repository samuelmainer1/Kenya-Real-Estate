from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from .models import Blog, BlogCategory, BlogComment, BlogSubscription
from django.utils import timezone
from django.contrib import messages
from .utils import send_blog_notification

# Blog listing with search, category filter, pagination, recent articles, subscriptionpython3 manage.py shell
def blog_list(request):
    # Auto-publish any scheduled blogs that are due
    now = timezone.now()
    Blog.objects.filter(scheduled_at__lte=now, published=False).update(published=True)
    
    query = request.GET.get('search', '')
    category_id = request.GET.get('category')
    blogs = Blog.objects.filter(published=True)
    
    if query:
        blogs = blogs.filter(Q(title__icontains=query) | Q(short_description__icontains=query) | Q(description__icontains=query))
    if category_id:
        blogs = blogs.filter(category_id=category_id)
    
    blogs = blogs.order_by('-posted_at')
    paginator = Paginator(blogs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categories = BlogCategory.objects.all()
    recent_blogs = Blog.objects.filter(published=True).order_by('-posted_at')[:5]
    
    # Subscription
    if request.method == 'POST' and 'email' in request.POST:
        email = request.POST.get('email')
        if email:
            subscription, created = BlogSubscription.objects.get_or_create(
                email=email,
                defaults={'is_active': True}
            )
            if created:
                messages.success(request, 'Successfully subscribed to blog updates!')
            elif not subscription.is_active:
                subscription.is_active = True
                subscription.save()
                messages.success(request, 'Welcome back! You are now subscribed again.')
            else:
                messages.info(request, 'You are already subscribed to our blog updates.')
    
    return render(request, 'blog/blog_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'recent_blogs': recent_blogs,
        'query': query,
        'category_id': category_id,
    })

# Blog detail with comments, like, previous/next, subscription
def blog_detail(request, slug):
    # Auto-publish any scheduled blogs that are due
    now = timezone.now()
    Blog.objects.filter(scheduled_at__lte=now, published=False).update(published=True)

    blog = get_object_or_404(Blog, slug=slug, published=True)
    previous_blog = Blog.objects.filter(published=True, posted_at__lt=blog.posted_at).order_by('-posted_at').first()
    next_blog = Blog.objects.filter(published=True, posted_at__gt=blog.posted_at).order_by('posted_at').first()
    recent_blogs = Blog.objects.filter(published=True).order_by('-posted_at')[:5]

    # Get related blogs by category (excluding current blog)
    related_blogs = Blog.objects.filter(
        published=True,
        category=blog.category
    ).exclude(id=blog.id).order_by('-posted_at')[:3]

    # Like
    if request.method == 'POST' and 'like' in request.POST:
        if request.user.is_authenticated:
            blog.likes.add(request.user)
            return redirect('blog_detail', slug=slug)
    # Comment
    if request.method == 'POST' and 'content' in request.POST:
        if request.user.is_authenticated:
            BlogComment.objects.create(blog=blog, user=request.user, content=request.POST['content'])
            return redirect('blog_detail', slug=slug)
    # Subscription
    if request.method == 'POST' and 'email' in request.POST:
        email = request.POST.get('email')
        if email:
            subscription, created = BlogSubscription.objects.get_or_create(
                email=email,
                defaults={'is_active': True}
            )
            if created:
                messages.success(request, 'Successfully subscribed to blog updates!')
            elif not subscription.is_active:
                subscription.is_active = True
                subscription.save()
                messages.success(request, 'Welcome back! You are now subscribed again.')
            else:
                messages.info(request, 'You are already subscribed to our blog updates.')
    return render(request, 'blog/blog_detail.html', {
        'blog': blog,
        'previous_blog': previous_blog,
        'next_blog': next_blog,
        'recent_blogs': recent_blogs,
        'related_blogs': related_blogs,
    })

def unsubscribe_blog(request, token):
    try:
        subscription = BlogSubscription.objects.get(unsubscribe_token=token)
        subscription.is_active = False
        subscription.save()
        messages.success(request, 'You have been successfully unsubscribed from blog updates.')
    except BlogSubscription.DoesNotExist:
        messages.error(request, 'Invalid unsubscribe link.')
    
    return render(request, 'blog/unsubscribe.html')

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import User, UserProfile
from .serializers import RegisterSerializer


def placeholder_view(request):
    """Placeholder view for development"""
    return JsonResponse({'message': 'Accounts API placeholder'})


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        role = request.POST.get('role', 'student')
        
        # Basic validation
        if not all([username, email, first_name, last_name, password, password_confirm]):
            messages.error(request, 'All fields are required.')
            return render(request, 'registration/register.html')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'registration/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'registration/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'registration/register.html')
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                role=role
            )
            
            # UserProfile will be created automatically by signal
            
            # Log in the user
            login(request, user)
            messages.success(request, f'Welcome {user.get_full_name()}! Your account has been created successfully.')
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'registration/register.html')
    
    return render(request, 'registration/register.html')


@login_required
def profile_view(request):
    """User profile view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update profile
        profile.phone = request.POST.get('phone', '')
        profile.bio = request.POST.get('bio', '')
        profile.preferred_language = request.POST.get('preferred_language', 'uz')
        profile.notifications_enabled = 'notifications_enabled' in request.POST
        profile.email_notifications = 'email_notifications' in request.POST
        profile.save()
        
        # Update user info
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    return render(request, 'accounts/profile.html', {'profile': profile})


def dashboard_view(request):
    """User dashboard view"""
    if not request.user.is_authenticated:
        return redirect('home')
    
    from examinations.models import Test, TestAttempt, Category
    
    context = {
        'user': request.user,
        'available_tests': Test.objects.filter(status='published', is_active=True)[:6],
        'categories': Category.objects.filter(is_active=True)[:4],
    }
    
    if request.user.role == 'student':
        # Get student's test attempts and results
        context['recent_attempts'] = TestAttempt.objects.filter(
            user=request.user
        ).order_by('-started_at')[:5]
        
    elif request.user.role == 'teacher':
        # Get teacher's tests and statistics
        context['my_tests'] = Test.objects.filter(
            created_by=request.user
        ).order_by('-created_at')[:5]
        
    elif request.user.role == 'admin':
        # Get admin statistics
        context['total_tests'] = Test.objects.count()
        context['total_attempts'] = TestAttempt.objects.count()
        context['total_users'] = User.objects.count()
    
    return render(request, 'accounts/dashboard.html', context)

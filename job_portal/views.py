from django.shortcuts import render
from apps.jobs.models import Job

def home(request):
    # Get featured jobs first, then fill with latest jobs if needed
    featured_jobs = Job.objects.filter(is_featured=True).order_by('-posted_at')
    latest_jobs = Job.objects.exclude(is_featured=True).order_by('-posted_at')
    
    # Combine featured and latest jobs, limit to 6 total
    all_jobs = list(featured_jobs) + list(latest_jobs)
    display_jobs = all_jobs[:6]
    
    context = {
        'latest_jobs': display_jobs,
        'featured_count': featured_jobs.count()
    }
    return render(request, 'home.html', context)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Task
from .forms import TaskForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST


def task_list(request):
    # Optimize database queries by pre-fetching foreign key user data
    task_list_qs = Task.objects.select_related('assigned_to', 'created_by').all().order_by('-created_date')
    
    # Search and Filter logic
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        task_list_qs = task_list_qs.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
    
    if status_filter:
        task_list_qs = task_list_qs.filter(status=status_filter)

    # Pagination: 5 tasks per page
    paginator = Paginator(task_list_qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'tasks/task_list.html', context)

def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'tasks/task_detail.html', {'object': task})

def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            # If a user is logged in, use them; otherwise, default to the first superuser/user in the database
            if request.user.is_authenticated:
                task.created_by = request.user
            else:
                default_user = User.objects.first()
                if default_user:
                    task.created_by = default_user
                else:
                    # Fallback if no user exists at all
                    return redirect('admin:index')
            task.save()
            messages.success(request, "Task created successfully!")
            return redirect('tasks:task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})

def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully!")
            return redirect('tasks:task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form})

def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        messages.warning(request, "Task deleted successfully!")
        return redirect('tasks:task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'object': task})

@require_POST
def task_toggle_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.status != 'Completed':
        task.status = 'Completed'
        task.save()
        return JsonResponse({'status': 'success', 'new_status': task.status})
    return JsonResponse({'status': 'no_change', 'new_status': task.status})
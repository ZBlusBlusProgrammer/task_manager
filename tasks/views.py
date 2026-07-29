from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Task
from .forms import TaskForm

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

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user  # Securely stamp the logged-in user
            task.save()
            messages.success(request, "Task created successfully!")
            return redirect('tasks:task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
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

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        messages.warning(request, "Task deleted successfully!")
        return redirect('tasks:task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'object': task})

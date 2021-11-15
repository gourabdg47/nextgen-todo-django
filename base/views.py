from django.shortcuts import redirect, render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Task


class CustomLoginView(LoginView):
    
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authentication_user = True
    
    def get_success_url(self):
        return reverse_lazy('tasks')


class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authentication_user = True                     # Un-authenticated users are redirected
    success_url = reverse_lazy('tasks')
    
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)
    
    def get(self, *args, **kwargs):                                # Over-writing get so loggedin users can go to user register page
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)
    

class TaskList(LoginRequiredMixin, ListView):               # Looks for task_list.html by default
    model = Task
    context_object_name = 'tasks'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user = self.request.user)
        context['count'] = context['tasks'].filter(complete = False).count()
        
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(
                title__startswith = search_input
            )
        context['search_input'] = search_input
        return context
        
    
class TaskDetail(LoginRequiredMixin, DetailView):           # Looks for task_detail.html by default
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'
    
class TaskCreate(LoginRequiredMixin, CreateView):           # Looks for task_form.html by default
    model = Task
    fields = ['title', 'description', 'complete']           # Listing all the items from the model 'Task' class fields using {form} in "task_create.html"
    success_url = reverse_lazy('tasks')                     # 'tasks' is the url name
    
    def form_valid(self, form):                             # Here we overriding the default method so only logged in user can create tasks on there accound and not on other accounts
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)
    
    
class TaskUpdate(LoginRequiredMixin, UpdateView): 
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')


class DeleteView(LoginRequiredMixin, DeleteView):           # Looks for "task_confirm_delete.html" by deafult
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
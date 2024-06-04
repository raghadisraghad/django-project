from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import logout,login, authenticate ,authenticate
from django.views.generic.edit import CreateView
from ..forms import CustomUserChangeForm,TakeQuizForm, LearnerSignUpForm, InstructorSignUpForm, QuestionForm, BaseAnswerInlineFormSet, LearnerInterestsForm, LearnerCourse, UserForm, PostForm
from ..models import User,Module,Announcement
from django.views.generic import ListView, DetailView 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.utils import timezone


def dashboard(request):
    if not request.user.is_admin:
        return redirect('home')
    learner = User.objects.filter(is_learner=True).count()
    instructor = User.objects.filter(is_instructor=True).count()
    module = Module.objects.all().count()
    users = User.objects.all().count()
    context = {'learner':learner, 'module':module, 'instructor':instructor, 'users':users}

    return render(request, 'dashboard/admin/home.html', context)

def course(request):
    if not request.user.is_admin:
        return redirect('home')
    if request.method == 'POST':
        name = request.POST['name']
        color = request.POST['color']

        a = Module(name=name, color=color)
        a.save()
        messages.success(request, 'New Course Was Registed Successfully')
        return redirect('course')
    else:
        return render(request, 'dashboard/admin/course.html')

class InstructorSignUpView(CreateView):
    model = User
    form_class = InstructorSignUpForm
    template_name = 'dashboard/admin/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'instructor'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Instructor Was Added Successfully')
        return redirect('addinstructor')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    

class AdminLearner(CreateView):
    model = User
    form_class = LearnerSignUpForm
    template_name = 'dashboard/admin/learner_signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'learner'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Learner Was Added Successfully')
        return redirect('addlearner')
    
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    

class ListUserView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/admin/list_users.html'
    context_object_name = 'users'
    paginated_by = 10


    def get_queryset(self):
        return User.objects.order_by('-id')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    

class AdminDeleteAnnonce(SuccessMessageMixin, DeleteView):
    model = Announcement
    template_name = 'dashboard/admin/confirm_delete.html'
    success_url = reverse_lazy('adminListAnnonce')
    success_message = "Announcement Was Deleted Successfully"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    
class AdminAllAnnonce(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'dashboard/admin/tise_list.html'


    def get_queryset(self):
        return Announcement.objects.filter(posted_at__lt=timezone.now()).order_by('posted_at')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
class AdminCreateAnnonce(CreateView):
    model = Announcement
    form_class = PostForm
    template_name = 'dashboard/admin/post_form.html'
    success_url = reverse_lazy('allannonce')


    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

class ListAllAnnonce(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'dashboard/admin/list_tises.html'
    context_object_name = 'Annoncements'
    paginated_by = 10


    def get_queryset(self):
        return Announcement.objects.order_by('-id')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
class AdminDeleteUser(SuccessMessageMixin, DeleteView):
    model = User
    template_name = 'dashboard/admin/confirm_delete2.html'
    success_url = reverse_lazy('allusers')
    success_message = "User Was Deleted Successfully"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

def AdminProfile(request):
    if not request.user.is_admin:
        return redirect('home')
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('adminprofile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'dashboard/admin/user_profile.html', {'form': form})
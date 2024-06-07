from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.views import generic
#from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, DetailView 
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponse, Http404
#from .models import Customer, Profile
from ..forms import CustomUserChangeForm, TakeQuizForm, LearnerSignUpForm, InstructorSignUpForm, QuestionForm, BaseAnswerInlineFormSet, LearnerInterestsForm, TutorialForm, UserForm, PostForm
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.core import serializers
from django.conf import settings
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import auth
from datetime import datetime, date
from django.core.exceptions import ValidationError
import operator
import itertools
from django.db.models import Avg, Count, Sum
from django.forms import inlineformset_factory
from ..models import TakenQuiz, Quiz, Question, Answer, Learner, User,Course, Notes, Announcement,Tutorial
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

def home_learner(request):
    if not request.user.is_learner:
        return redirect('home')
    return render(request, 'dashboard/learner/home.html')

def LearnerProfile(request):
    if not request.user.is_learner:
        return redirect('home')
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('learnerprofile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'dashboard/learner/user_profile.html', {'form': form})


def LearnerUpdatePassword(request):
    if not request.user.is_learner:
        return redirect('home')
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('learnerprofile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'user_profile.html', {'form': form})

class LearnerAllAnnonce(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'dashboard/learner/tise_list.html'

    def get_queryset(self):
        return Announcement.objects.filter(posted_at__lt=timezone.now()).order_by('posted_at')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_learner:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
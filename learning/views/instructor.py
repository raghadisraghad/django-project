from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import logout,login, authenticate ,authenticate
from django.views.generic.edit import CreateView
from ..forms import TakeQuizForm, LearnerSignUpForm, InstructorSignUpForm, QuestionForm, BaseAnswerInlineFormSet, LearnerInterestsForm, LearnerCourse, UserForm, PostForm
from ..models import User,Module


def home_instructor(request):
    if not request.user.is_instructor:
        return redirect('home')
    
    learner = User.objects.filter(is_learner=True).count()
    instructor = User.objects.filter(is_instructor=True).count()
    module = Module.objects.all().count()
    users = User.objects.all().count()
    context = {'learner':learner, 'module':module, 'instructor':instructor, 'users':users}

    return render(request, 'dashboard/instructor/home.html', context)

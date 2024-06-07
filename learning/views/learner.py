from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import logout,login, authenticate ,authenticate
from django.views.generic.edit import CreateView
from ..forms import TakeQuizForm, LearnerSignUpForm, InstructorSignUpForm, QuestionForm, BaseAnswerInlineFormSet, LearnerInterestsForm, LearnerCourse, UserForm, PostForm
from ..models import User,Course

def home_learner(request):
    learner = User.objects.filter(is_learner=True).count()
    instructor = User.objects.filter(is_instructor=True).count()
    module = Course.objects.all().count()
    users = User.objects.all().count()

    context = {'learner':learner, 'module':module, 'instructor':instructor, 'users':users}

    return render(request, 'dashboard/learner/home.html', context)


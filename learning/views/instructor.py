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
from ..forms import CustomUserChangeForm, TakeQuizForm, LearnerSignUpForm, InstructorSignUpForm, QuestionForm, BaseAnswerInlineFormSet, LearnerInterestsForm, UserForm, PostForm
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


def home_instructor(request):
    if not request.user.is_instructor:
        return redirect('home')
    return render(request, 'dashboard/instructor/home.html')
    
    
class InstructorAllAnnonce(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'dashboard/instructor/tise_list.html'

    def get_queryset(self):
        return Announcement.objects.filter(posted_at__lt=timezone.now()).order_by('posted_at')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_instructor:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
class InstructorCreateAnnonce(CreateView):
    model = Announcement
    form_class = PostForm
    template_name = 'dashboard/instructor/post_form.html'
    success_url = reverse_lazy('instructorallannonce')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_instructor:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    

class QuizCreateView(CreateView):
    model = Quiz
    fields = ('name', 'course')
    template_name = 'dashboard/Instructor/quiz_add_form.html'


    def form_valid(self, form):
        quiz = form.save(commit=False)
        quiz.owner = self.request.user
        quiz.save()
        messages.success(self.request, 'Quiz created, Go A Head And Add Questions')
        return redirect('quiz_change', quiz.pk)
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_instructor:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class QuizUpateView(UpdateView):
    model = Quiz
    fields = ('name', 'course')
    template_name = 'dashboard/instructor/quiz_change_form.html'


    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()


    def get_success_url(self):
        return reverse('quiz_change', kwargs={'pk', self.object.pk})
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_instructor:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
        

def question_add(request, pk):
    if not request.user.is_instructor:
        return redirect('home')
    quiz = get_object_or_404(Quiz, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'You may now add answers/options to the question.')
            return redirect('question_change', quiz.pk, question.pk)
    else:
        form = QuestionForm()

    return render(request, 'dashboard/instructor/question_add_form.html', {'quiz': quiz, 'form': form})




def question_change(request, quiz_pk, question_pk):
    if not request.user.is_instructor:
        return redirect('home')
    quiz = get_object_or_404(Quiz, pk=quiz_pk, owner=request.user)
    question = get_object_or_404(Question, pk=question_pk, quiz=quiz)

    AnswerFormatSet = inlineformset_factory (
        Question,
        Answer,
        formset = BaseAnswerInlineFormSet,
        fields = ('text', 'is_correct'),
        min_num = 2,
        validate_min = True,
        max_num = 10,
        validate_max = True
        )

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormatSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                formset.save()
                formset.save()
            messages.success(request, 'Question And Answers Saved Successfully')
            return redirect('quiz_change', quiz.pk)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormatSet(instance=question)
    return render(request, 'dashboard/instructor/question_change_form.html', {
        'quiz':quiz,
        'question':question,
        'form':form,
        'formset':formset
        })        


class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'dashboard/instructor/quiz_change_list.html'


    def get_queryset(self):
        queryset = self.request.user.quizzes \
        .select_related('course') \
        .annotate(questions_count = Count('questions', distinct=True)) \
        .annotate(taken_count = Count('taken_quizzes', distinct=True))
        return queryset    
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_instructor:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class QuestionDeleteView(DeleteView):
    model = Question
    context_object_name = 'question'
    template_name = 'dashboard/instructor/question_delete_confirm.html'
    pk_url_kwarg = 'question_pk'

    def get_context_data(self, **kwargs):
        question = self.get_object()
        kwargs['quiz'] = question.quiz
        return super().get_context_data(**kwargs)


    def delete(self, request, *args, **kwargs):
        question = self.get_object()
        messages.success(request, 'The Question Was Deleted Successfully')
        return super().delete(request, *args, **kwargs)


    def get_queryset(self):
        return Question.objects.filter(quiz__owner=self.request.user)


    def get_success_url(self):
        question = self.get_object()
        return reverse('quiz_change', kwargs={'pk': question.quiz_id})    
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_instructor:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)



class QuizResultsView(DeleteView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'dashboard/instructor/quiz_results.html'


    def get_context_data(self, **kwargs):
        quiz = self.get_object()
        taken_quizzes =quiz.taken_quizzes.select_related('learner__user').order_by('-date')
        total_taken_quizzes = taken_quizzes.count()
        quiz_score = quiz.taken_quizzes.aggregate(average_score=Avg('score'))
        extra_context = {
        'taken_quizzes': taken_quizzes,
        'total_taken_quizzes': total_taken_quizzes,
        'quiz_score':quiz_score
        }

        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)


    def get_queryset(self):
        return self.request.user.quizzes.all()    
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_instructor:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class QuizDeleteView(DeleteView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'dashboard/instructor/quiz_delete_confirm.html'
    success_url = reverse_lazy('quiz_change_list')

    def delete(self, request, *args, **kwargs):
        quiz = self.get_object()
        messages.success(request, 'The quiz %s was deleted with success!' % quiz.name)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_instructor:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


def question_add(request, pk):
    if not request.user.is_instructor:
        return redirect('home')
    quiz = get_object_or_404(Quiz, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'You may now add answers/options to the question.')
            return redirect('question_change', quiz.pk, question.pk)
    else:
        form = QuestionForm()

    return render(request, 'dashboard/instructor/question_add_form.html', {'quiz': quiz, 'form': form})


class QuizUpdateView(UpdateView):
    model = Quiz
    fields = ('name', 'course', )
    context_object_name = 'quiz'
    template_name = 'dashboard/instructor/quiz_change_form.html'


    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        '''
        This method is an implicit object-level permission management
        This view will only match the ids of existing quizzes that belongs
        to the logged in user.
        '''
        return self.request.user.quizzes.all()

    def get_success_url(self):
        return reverse('quiz_change', kwargs={'pk': self.object.pk})
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_instructor:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

 
class CreatePost(CreateView):
    form_class = PostForm
    model = Announcement
    template_name = 'dashboard/instructor/post_form.html'
    success_url = reverse_lazy('llchat')


    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_instructor:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class TiseList(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'dashboard/instructor/tise_list.html'

    def get_queryset(self):
        return Announcement.objects.filter(posted_at__lt=timezone.now()).order_by('posted_at')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_instructor:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

def tutorial(request):
    if not request.user.is_instructor:
        return redirect('home')
    courses = Course.objects.only('id', 'name')
    context = {'courses':courses}

    return render(request, 'dashboard/instructor/tutorial.html', context)



def publish_tutorial(request):
    if not request.user.is_instructor:
        return redirect('home')
    if request.method == 'POST':
        title = request.POST['title']
        course_id = request.POST['course_id']
        content = request.POST['content']
        thumb = request.FILES['thumb']
        current_user = request.user
        author_id = current_user.id
        print(author_id)
        print(course_id)
        a = Tutorial(title=title, content=content, thumb=thumb, user_id=author_id, course_id=course_id)
        a.save()
        messages.success(request, 'Tutorial was published successfully!')
        return redirect('tutorial')
    else:
        messages.error(request, 'Tutorial was not published successfully!')
        return redirect('tutorial')



def itutorial(request):
    if not request.user.is_instructor:
        return redirect('home')
    tutorials = Tutorial.objects.all().order_by('-created_at')
    tutorials = {'tutorials':tutorials}
    return render(request, 'dashboard/instructor/list_tutorial.html', tutorials)


class ITutorialDetail(LoginRequiredMixin, DetailView):
    model = Tutorial
    template_name = 'dashboard/instructor/tutorial_detail.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_instructor:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)



class LNotesList(ListView):
    model = Notes
    template_name = 'dashboard/instructor/list_notes.html'
    context_object_name = 'notes'
    paginate_by = 4

    def get_queryset(self):
        return Notes.objects.order_by('-id')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_instructor:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


def iadd_notes(request):
    if not request.user.is_instructor:
        return redirect('home')
    courses = Course.objects.only('id', 'name')
    context = {'courses':courses}
    return render(request, 'dashboard/instructor/add_notes.html', context)


def publish_notes(request):
    if not request.user.is_instructor:
        return redirect('home')
    if request.method == 'POST':
        title = request.POST['title']
        course_id = request.POST['course_id']
        cover = request.FILES['cover']
        file = request.FILES['file']
        current_user = request.user
        user_id = current_user.id

        a = Notes(title=title, cover=cover, file=file, user_id=user_id, course_id=course_id)
        a.save()
        messages.success = (request, 'Notes Was Published Successfully')
        return redirect('lnotes')
    else:
        messages.error = (request, 'Notes Was Not Published Successfully')
        return redirect('iadd_notes')


def update_file(request, pk):
    if not request.user.is_instructor:
        return redirect('home')
    if request.method == 'POST':
        file = request.FILES['file']
        file_name = request.FILES['file'].name

        fs = FileSystemStorage()
        file = fs.save(file.name, file)
        fileurl = fs.url(file)
        file = file_name
        print(file)

        Notes.objects.filter(id = pk).update(file = file)
        messages.success = (request, 'Notes was updated successfully!')
        return redirect('lnotes')
    else:
        return render(request, 'dashboard/instructor/update.html')

def InstructorProfile(request):
    if not request.user.is_instructor:
        return redirect('home')
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('instructorprofile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'dashboard/instructor/user_profile.html', {'form': form})


def UpdatePassword(request):
    if not request.user.is_instructor:
        return redirect('home')
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('instructorprofile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'user_profile.html', {'form': form})
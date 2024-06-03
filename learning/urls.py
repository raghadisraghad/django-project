from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required



urlpatterns = [

# Shared URLs
path('', views.home, name='home'),
path('lsign/', views.LearnerSignUpView.as_view(), name='lsign'),
path('login_form/', views.login_form, name='login_form'),
path('login/', views.loginView, name='login'),
path('logout/', views.logoutView, name='logout'),


# Admin URLs
path('dashboard/', login_required(views.dashboard), name='dashboard'),
path('course/', login_required(views.course), name='course'),
path('isign/', login_required(views.InstructorSignUpView.as_view()), name='isign'),
path('addlearner/', login_required(views.AdminLearner.as_view()), name='addlearner'),
path('apost/', login_required(views.AdminCreatePost.as_view()), name='apost'),
path('alpost/', login_required(views.AdminListTise.as_view()), name='alpost'),
path('alistalltise/', login_required(views.ListAllTise.as_view()), name='alistalltise'),
path('adpost/<int:pk>', login_required(views.ADeletePost.as_view()), name='adpost'),
path('aluser/', login_required(views.ListUserView.as_view()), name='aluser'),
path('aduser/<int:pk>', login_required(views.ADeleteuser.as_view()), name='aduser'),
path('create_user_form/', login_required(views.create_user_form), name='create_user_form'),
path('create_user/', login_required(views.create_user), name='create_user'),
path('acreate_profile/', login_required(views.acreate_profile), name='acreate_profile'),
path('auser_profile/', login_required(views.auser_profile), name='auser_profile'),



# Instructor URLs
path('instructor/', login_required(views.home_instructor), name='instructor'),
path('quiz_add/', login_required(views.QuizCreateView.as_view()), name='quiz_add'),
path('question_add/<int:pk>', login_required(views.question_add), name='question_add'),
path('quiz/<int:quiz_pk>/<int:question_pk>/', login_required(views.question_change), name='question_change'),
path('llist_quiz/', login_required(views.QuizListView.as_view()), name='quiz_change_list'),
path('quiz/<int:quiz_pk>/question/<int:question_pk>/delete/', login_required(views.QuestionDeleteView.as_view()), name='question_delete'),
path('quiz/<int:pk>/results/', login_required(views.QuizResultsView.as_view()), name='quiz_results'),
path('quiz/<int:pk>/delete/', login_required(views.QuizDeleteView.as_view()), name='quiz_delete'),
path('quizupdate/<int:pk>/', login_required(views.QuizUpdateView.as_view()), name='quiz_change'),
path('ipost/', login_required(views.CreatePost.as_view()), name='ipost'),
path('llchat/', login_required(views.TiseList.as_view()), name='llchat'),
path('user_profile/', login_required(views.user_profile), name='user_profile'),
path('create_profile/', login_required(views.create_profile), name='create_profile'),
path('tutorial/', login_required(views.tutorial), name='tutorial'),
path('post/', login_required(views.publish_tutorial),name='publish_tutorial'),
path('itutorial/', login_required(views.itutorial),name='itutorial'),
path('itutorials/<int:pk>/', login_required(views.ITutorialDetail.as_view()), name = "itutorial-detail"),
path('listnotes/', login_required(views.LNotesList.as_view()), name='lnotes'),
path('iadd_notes/', login_required(views.iadd_notes), name='iadd_notes'),
path('publish_notes/', login_required(views.publish_notes), name='publish_notes'),
path('update_file/<int:pk>', login_required(views.update_file), name='update_file'),




# Learner URl's
path('learner/', login_required(views.home_learner),name='learner'),
path('ltutorial/', login_required(views.ltutorial),name='ltutorial'),
path('llistnotes/', login_required(views.LLNotesList.as_view()), name='llnotes'),
path('ilchat/', login_required(views.ITiseList.as_view()), name='ilchat'),
path('luser_profile/', login_required(views.luser_profile), name='luser_profile'),
path('lcreate_profile/', login_required(views.lcreate_profile), name='lcreate_profile'),
path('tutorials/<int:pk>/', login_required(views.LTutorialDetail.as_view()), name = "tutorial-detail"),
path('interests/', login_required(views.LearnerInterestsView.as_view()), name='interests'),
path('learner_quiz/', login_required(views.LQuizListView.as_view()), name='lquiz_list'),
path('taken/', login_required(views.TakenQuizListView.as_view()), name='taken_quiz_list'),
path('quiz/<int:pk>/', login_required(views.take_quiz), name='take_quiz'),







































 
]

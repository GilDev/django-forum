from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

import main.views


main_urlpatterns = [
    path('login/', main.views.LoginTemplateView.as_view(), name='login'),
    path('logout/', main.views.logout_view, name='logout'),
    path('register/', main.views.RegisterTemplateView.as_view(), name='register'),
    path('reset_pwd_form/', main.views.ResetPwdFormTemplateView.as_view(), name='reset_pwd_form'),
    path('reset_pwd_done/', main.views.ResetPwdDoneTemplateView.as_view(), name='reset_pwd_done'),
    path('reset_pwd_confirm/<str:email>', main.views.ResetPwdConfirmTemplateView.as_view(), name='reset_pwd_confirm'),
    path('reset_pwd_complete/', main.views.ResetPwdCompleteTemplateView.as_view(), name='reset_pwd_complete'),
    path('profil/', main.views.ProfilTemplateView.as_view(), name='profil'),
    path('topics/', main.views.TopicListTemplateView.as_view(), name='topic_list'),
    path('topics/<int:page>', main.views.TopicListTemplateView.as_view(), name='topic_list'),
    path('topics/topic_<int:pk>/', main.views.TopicDetailTemplateView.as_view(), name='topic_detail'),
    path('topics/new/', main.views.TopicCreateTemplateView.as_view(), name='topic_create'),
    path('react/', main.views.ReactTemplateView.as_view(), name='react'),
]

urlpatterns = [
    path('', main.views.HomeTemplateView.as_view(), name='home'),
    path('main/', include(main_urlpatterns)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
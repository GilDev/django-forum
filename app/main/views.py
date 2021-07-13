from django.contrib import messages
from django.core.validators import validate_email
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import TemplateView
from .models import Topic, Comment, User

class HomeTemplateView(TemplateView):
    template_name = 'main/home.html'

class LoginTemplateView(TemplateView):
    template_name = 'main/login.html'

class RegisterTemplateView(TemplateView):
    template_name = 'main/register.html'

    def post(self, request):
        email            = request.POST.get('username')
        password         = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check for empty fields
        if not email or not password or not confirm_password:
            print(1);
            return render(request, self.template_name, {
                'error_message': "Please fill in all the fields.",
            })

        # Check for valid email
        try:
            validate_email(email)
        except:
            return render(request, self.template_name, {
                'error_message': "The entered email is invalid.",
            })

        # Check for unused email
        if User.objects.filter(email=email).count() > 0:
            return render(request, self.template_name, {
                'error_message': "An account with this email already exists.",
            })

        # Check for password confirmation
        if password != confirm_password:
            return render(request, self.template_name, {
                'error_message': "Password and confirmation doesn’t match.",
            })

        try:
            user = User.objects.create_user(email=email, password=password)
            user.first_name = email.split('@')[0]
            user.last_name = ''
            user.level = User.Level.NEWBIE
            user.save()
        except Exception as e:
            return render(request, self.template_name, {
                # 'error_message': "An error occured.",
                'error_message': e,
            })

        messages.add_message(request, messages.SUCCESS, "Account successfully created, please log in.")

        return HttpResponseRedirect(reverse('login'))

class ResetPwdFormTemplateView(TemplateView):
    template_name = 'main/reset_pwd_form.html'

class ResetPwdDoneTemplateView(TemplateView):
    template_name = 'main/reset_pwd_done.html'

class ResetPwdConfirmTemplateView(TemplateView):
    template_name = 'main/reset_pwd_confirm.html'

class ResetPwdCompleteTemplateView(TemplateView):
    template_name = 'main/reset_pwd_complete.html'

class ProfilTemplateView(TemplateView):
    template_name = 'main/profil.html'

class TopicListTemplateView(TemplateView):
    template_name = 'main/topic_list.html'
    # TODO: ajouter paramètre get “page” et récupérer seulement 10 topics par page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topics'] = Topic.objects.order_by('-date')[:10]
        return context

class TopicDetailTemplateView(TemplateView):
    template_name = 'main/topic_detail.html'

    def post(self, request, pk):
        context = self.get_context_data()

        if request.POST.get('reply'):
            new_comment = Comment(
                topic   = context['topic'],
                message = request.POST.get('reply'),
                author  = User.objects.first(), # TODO: Use the currently logged in user
            )
            new_comment.save()

            return HttpResponseRedirect(reverse('topic_detail', args=(pk,)))
        else:
            context['error_message'] = "Please enter a reply message."
            return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        topic = get_object_or_404(Topic, pk=self.kwargs['pk'])
        topic.author.level = topic.author.Level(topic.author.level).label

        topic.comments = topic.comment_set.all()
        for comment in topic.comments:
            comment.author.level = comment.author.Level(comment.author.level).label

        context['topic'] = topic
        return context


class TopicCreateTemplateView(TemplateView):
    template_name = 'main/topic_create.html'

    def post(self, request):
        if request.POST.get('title') and request.POST.get('description'):
            new_topic = Topic(
                title   = request.POST.get('title'),
                message = request.POST.get('description'),
                author  = User.objects.first(), # TODO: Use the currently logged in user
            )
            new_topic.save()

            return HttpResponseRedirect(reverse('topic_detail', args=(new_topic.id,)))
        else:
            return render(request, self.template_name, {
                'error_message': "Please enter a title and a message.",
            })

class ReactTemplateView(TemplateView):
    template_name = 'main/react.html'
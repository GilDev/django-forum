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
                author  = User.objects.first(),
            )
            new_topic.save()

            return HttpResponseRedirect(reverse('topic_detail', args=(new_topic.id,)))
        else:
            return render(request, self.template_name, {
                'error_message': "Please enter a title and a message.",
            })

class ReactTempalteView(TemplateView):
    template_name = 'main/react.html'
import datetime
from os.path import splitext
import secrets

from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView, ListView
from django.views.generic.base import ContextMixin
from .models import Topic, Comment, User

class HomeTemplateView(TemplateView):
    template_name = 'main/home.html'

class LoginTemplateView(TemplateView):
    template_name = 'main/login.html'

    def post(self, request):
        email    = request.POST.get('username')
        password = request.POST.get('password')

        # Check for empty fields
        if not email or not password:
            messages.add_message(request, messages.ERROR, "Please fill in all the fields.")
            return render(request, self.template_name)

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.add_message(request, messages.SUCCESS, "Successfully logged in.")
            return HttpResponseRedirect(reverse('topic_list'))
        else:
            messages.add_message(request, messages.ERROR, "Incorrect credentials.")
            return render(request, self.template_name)

@login_required
def logout_view(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS, "Successfully logged out.")
    return HttpResponseRedirect(reverse('login'))

class RegisterTemplateView(TemplateView):
    template_name = 'main/register.html'

    def post(self, request):
        email            = request.POST.get('username')
        password         = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check for empty fields
        if not email or not password or not confirm_password:
            messages.add_message(request, messages.ERROR, "Please fill in all the fields.")
            return render(request, self.template_name)

        # Check for valid email
        try:
            validate_email(email)
        except:
            messages.add_message(request, messages.ERROR, "The entered email is invalid.")
            return render(request, self.template_name)

        # Check for unused email
        if User.objects.filter(email=email).count() > 0:
            messages.add_message(request, messages.ERROR, "An account with this email already exists.")
            return render(request, self.template_name)

        # Check for password confirmation
        if password != confirm_password:
            messages.add_message(request, messages.ERROR, "Password and confirmation don’t match.")
            return render(request, self.template_name)

        try:
            user            = User.objects.create_user(email=email, password=password)
            user.first_name = email.split('@')[0]
            user.last_name  = ''
            user.level      = User.Level.NEWBIE
            user.save()
        except Exception as e:
            messages.add_message(request, messages.ERROR, "An error occured: " + e)
            return render(request, self.template_name)

        messages.add_message(request, messages.SUCCESS, "Account successfully created, please log in.")

        return HttpResponseRedirect(reverse('login'))

class ResetPwdFormTemplateView(TemplateView):
    template_name = 'main/reset_pwd_form.html'

    def post(self, request):
        email = request.POST.get('username')

        # Check for valid email
        try:
            validate_email(email)
        except:
            messages.add_message(request, messages.ERROR, "The entered email is invalid.")
            return render(request, self.template_name)

        user = User.objects.filter(email=email).first()
        # Send mail if user exists
        if user:
            user.reset_pwd_time = timezone.now()
            user.reset_pwd_hash = secrets.token_hex(nbytes=32)
            user.save()

            send_mail(
                "Django Forum: new password request",
                ("Please use the following link to reset your password: " +
                 request.build_absolute_uri(reverse('reset_pwd_confirm', kwargs={'hash': user.reset_pwd_hash})) +
                 ". This link will be usable for 10 minutes, after which "
                 "you will have to fill in the “Forgot password” form "
                 "once more."),
                "noreply@djangoforum.com",
                [email],
                fail_silently=False,
            )

        return HttpResponseRedirect(reverse('reset_pwd_done'))


class ResetPwdDoneTemplateView(TemplateView):
    template_name = 'main/reset_pwd_done.html'

class ResetPwdConfirmTemplateView(TemplateView):
    template_name = 'main/reset_pwd_confirm.html'

    def get(self, request, hash):
        context = {
            'validlink': False,
            'hash': hash,
        }

        # Check if user exists
        try:
            user = User.objects.get(reset_pwd_hash=hash)
        except User.DoesNotExist:
            return render(request, self.template_name, context)

        # Check if reset time interval is still valid
        if timezone.now() > user.reset_pwd_time + datetime.timedelta(minutes=10):
            return render(request, self.template_name, context)

        context['validlink'] = True
        return render(request, self.template_name, context)

    def post(self, request, hash):
        context = {
            'validlink': False,
            'hash': hash,
        }

        password         = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check for empty fields
        if not password or not confirm_password:
            messages.add_message(request, messages.ERROR, "Please fill in all the fields.")
            return render(request, self.template_name, context)

        # Check if user exists
        try:
            user = User.objects.get(reset_pwd_hash=hash)
        except User.DoesNotExist:
            return render(request, self.template_name, context)

        # Check if reset time interval is still valid
        if timezone.now() > user.reset_pwd_time + datetime.timedelta(minutes=10):
            return render(request, self.template_name, context)

        context['validlink'] = True

        # Check for password confirmation
        if password != confirm_password:
            messages.add_message(request, messages.ERROR, "Password and confirmation don’t match.")
            return render(request, self.template_name, context)

        user.set_password(password)
        user.reset_pwd_hash = ""
        user.reset_pwd_time = None
        user.save()

        return HttpResponseRedirect(reverse('reset_pwd_complete'))

class ResetPwdCompleteTemplateView(TemplateView):
    template_name = 'main/reset_pwd_complete.html'

class ProfileTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'main/profile.html'

    def post(self, request):
        avatar     = request.FILES['profile_photo']
        email      = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name  = request.POST.get('last_name')

        # Check for empty fields
        if not email or not first_name or not last_name or not avatar:
            messages.add_message(request, messages.ERROR, "Please fill in all the fields.")
            return render(request, self.template_name)

        # Check for valid email
        try:
            validate_email(email)
        except:
            messages.add_message(request, messages.ERROR, "The entered email is invalid.")
            return render(request, self.template_name)

        # Check for unused email
        if request.user.email != email and User.objects.filter(email=email).count() > 0:
            messages.add_message(request, messages.ERROR, "An account with this email already exists.")
            return render(request, self.template_name)

        avatar.name = email + splitext(avatar.name)[-1]
        try:
            user            = request.user
            user.email      = email
            user.first_name = first_name
            user.last_name  = last_name
            user.avatar     = avatar
            user.save()
        except Exception as e:
            messages.add_message(request, messages.ERROR, "An error occured: " + e)
            return render(request, self.template_name)

        messages.add_message(request, messages.SUCCESS, "Profile successfully updated.")

        return HttpResponseRedirect(reverse('topic_list'))

class TopicListView(LoginRequiredMixin, ListView):
    template_name = 'main/topic_list.html'
    model = Topic
    paginate_by = 5

    def get_queryset(self):
        self.filter = self.request.GET.get('filter', 'all')
        self.search = self.request.GET.get('search', '')
        page        = int(self.request.GET.get('page', '1'))

        topics = Topic.objects.order_by('-date')
        if self.filter == "solved":
            topics = topics.filter(solved=True)
        elif self.filter == "unsolved":
            topics = topics.filter(solved=False)
        elif self.filter == "no_replies":
            topics = topics.annotate(nb_comments=Count('comment')).filter(nb_comments=0)

        # TODO: Use Q()
        if self.search:
            topics = topics.filter(title__icontains=self.search) \
                   | topics.filter(message__icontains=self.search)

        return topics

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter
        context['search'] = self.search
        return context

class TopicDetailTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'main/topic_detail.html'

    def post(self, request, pk):
        context = self.get_context_data()

        if request.POST.get('reply'):
            new_comment = Comment(
                topic   = context['topic'],
                message = request.POST.get('reply'),
                author  = request.user
            )
            new_comment.save()

            messages.add_message(request, messages.SUCCESS, "New comment created successfully.")

            return HttpResponseRedirect(reverse('topic_detail', args=(pk,)))
        else:
            messages.add_message(request, messages.ERROR, "Please enter a comment before sending.")
            return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        topic = get_object_or_404(Topic, pk=self.kwargs['pk'])

        context['topic'] = topic
        return context


class TopicCreateTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'main/topic_create.html'

    def post(self, request):
        if request.POST.get('title') and request.POST.get('description'):
            new_topic = Topic(
                title   = request.POST.get('title'),
                message = request.POST.get('description'),
                author  = request.user
            )
            new_topic.save()

            messages.add_message(request, messages.SUCCESS, "New topic created successfully.")

            return HttpResponseRedirect(reverse('topic_detail', args=(new_topic.id,)))
        else:
            messages.add_message(request, messages.ERROR, "Please enter a title and a message.")
            return render(request, self.template_name)

class ReactTemplateView(TemplateView):
    template_name = 'main/react.html'
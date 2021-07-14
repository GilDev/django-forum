from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db.models import Count
from django.http import HttpResponseRedirect
from os.path import splitext
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import TemplateView
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

        # Send mail if user exists
        if User.objects.filter(email=email).count() > 0:
            send_mail(
                "Django Forum: new password request",
                ("Please use the following link to reset your password: " +
                 request.build_absolute_uri(reverse('reset_pwd_confirm', kwargs={'email': email})) +
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

    def get(self, request, email):
        context = {
            'validlink': False,
            'email': email,
        }

        # Check if user exists
        if User.objects.filter(email=email).count() == 0:
            return render(request, self.template_name, context)

        context['validlink'] = True
        return render(request, self.template_name, context)

    def post(self, request, email):
        context = {
            'validlink': False,
            'email': email,
        }

        password         = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check for empty fields
        if not email or not password or not confirm_password:
            messages.add_message(request, messages.ERROR, "Please fill in all the fields.")
            return render(request, self.template_name, context)

        # Check if user exists
        if User.objects.filter(email=email).count() == 0:
            messages.add_message(request, messages.ERROR, "The user doesn’t exists.")
            return render(request, self.template_name, context)

        context['validlink'] = True

        # Check for password confirmation
        if password != confirm_password:
            messages.add_message(request, messages.ERROR, "Password and confirmation don’t match.")
            return render(request, self.template_name, context)

        user = User.objects.get(email=email)
        user.set_password(password)
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

        avatar.name = email + splitext(avatar.name)[1]
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

class TopicListTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'main/topic_list.html'

    def get(self, request, filter="all", page=1, search=""):
        if filter == "solved":
            topics = Topic.objects.filter(solved=True).order_by('-date')
        elif filter == "unsolved":
            topics = Topic.objects.filter(solved=False).order_by('-date')
        elif filter == "no_replies":
            topics = Topic.objects.annotate(nb_comments=Count('comment')).filter(nb_comments=0).order_by('-date')
        else:
            topics = Topic.objects.order_by('-date')

        search = request.GET.get('search')
        if search:
            topics = topics.filter(title__icontains=search) \
                   | topics.filter(message__icontains=search)

        nb_per_page = 5
        nb_pages    = int((len(topics) - 1) / nb_per_page) + 1
        if page > nb_pages:
            return HttpResponseRedirect(reverse('topic_list', kwargs={'filter': filter, 'page': nb_pages}))
        elif page < 1:
            return HttpResponseRedirect(reverse('topic_list', kwargs={'filter': filter, 'page': 1}))

        topics_start = (page - 1) * nb_per_page
        topics_end   = topics_start + nb_per_page
        context = {
            'topics': topics[topics_start:topics_end],
            'filter': filter,
            'current_page': page,
            'nb_pages': nb_pages,
        }
        return render(request, self.template_name, context)

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
        topic.author.level = topic.author.Level(topic.author.level).label

        topic.comments = topic.comment_set.all()
        for comment in topic.comments:
            comment.author.level = comment.author.Level(comment.author.level).label

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
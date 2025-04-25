from django.conf import settings
from django.contrib.auth.models import User
from shop.tokens import password_reset_token
from django.core.mail import BadHeaderError, send_mail
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from shop.forms import UserForgotPasswordForm
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from shop.forms import UserPasswordResetForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_str
from django.contrib.auth import update_session_auth_hash

def password_reset(request):
    """User forgot password form view."""
    msg = ''
    if request.method == "POST":
        form = UserForgotPasswordForm(request.POST)
        if form.is_valid():
            email = request.POST.get('email')
            qs = User.objects.filter(email=email)
            site = get_current_site(request)

            if len(qs) > 0:
                user = qs[0]
                user.is_active = False  # User needs to be inactive for the reset password duration
                user.save()
                subject = "You have requested Password Reset if not you ignore link or click the link to reset your password"
                message = render_to_string('accounts/password_reset_mail.html', {
                    'user': user.first_name,
                    'protocol': 'https',
                    'domain': site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': password_reset_token.make_token(user),
                })

                from_email = settings.EMAIL_HOST_USER
                to_list = [user.email]

                try:
                   send_mail(subject, message, from_email, to_list, fail_silently=True)
                except Exception as e:
                   print(e)
            messages.add_message(request, messages.SUCCESS, 'Email {0} submitted.'.format(email))
            msg = 'We’ve emailed you instructions for setting your password, if an account exists with the email you entered. You should receive them shortly. If you don’t receive an email, please make sure you’ve entered the address you registered with, and check your spam folder.'
        else:
            messages.add_message(request, messages.WARNING, 'Email not submitted.')
            return render(request, 'accounts/password_reset_req.html', {'form': form})

    return render(request, 'accounts/password_reset_req.html', {'form': UserForgotPasswordForm, 'msg': msg})

def reset(request, uidb64, token):

    if request.method == 'POST':
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            messages.add_message(request, messages.WARNING, str(e))
            user = None

        if user is not None and password_reset_token.check_token(user, token):
            form = UserPasswordResetForm(user=user, data=request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)

                user.is_active = True
                user.save()
                messages.add_message(request, messages.SUCCESS, 'Password reset successfully.')
                return redirect('LogIn')
            else:
                context = {
                    'form': form,
                    'uid': uidb64,
                    'token': token
                }
                messages.add_message(request, messages.WARNING, 'Password could not be reset.')
                return render(request, 'accounts/password_reset_conf.html', context)
        else:
            messages.add_message(request, messages.WARNING, 'Password reset link is invalid.')
            messages.add_message(request, messages.WARNING, 'Please request a new password reset.')

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        messages.add_message(request, messages.WARNING, str(e))
        user = None
    if user is not None and password_reset_token.check_token(user, token):
        context = {
            'form': UserPasswordResetForm(user),
            'uid': uidb64,
            'token': token
        }
        return render(request, 'accounts/password_reset_conf.html', context)
    else:
        messages.add_message(request, messages.WARNING, 'Password reset link is invalid.')
        messages.add_message(request, messages.WARNING, 'Please request a new password reset.')

    return redirect('LogIn')

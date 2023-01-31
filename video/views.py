from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import AccountAuthenticationForm, RegistrationForm, AccountUpdateFrom, CreateRoomForm, UpdateRoomForm
from .models import Account, Room
from django.urls import reverse
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from random import randint
from django.http import HttpResponse, Http404


def generate_random_id():
    range_start = 10 ** (6 - 1)
    range_end = (10 ** 6) - 1
    return randint(range_start, range_end)


def home_screen_view(request):
    context = {}
    questions = Account.objects.all()
    context['questions'] = questions

    return render(request, "personal/home.html", context)


def registration_view(request):
    context = {}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            email = form.cleaned_data.get('email')
            account.save()
            email_to_send = generate_activation_email(request, account, email, 'activate')
            email_to_send.send(fail_silently=False)
            context['success_message'] = "Please click on the link sent to your Email address for Account Activation"
            return render(request, 'accounts/register.html', context)
        else:

            context['registration_form'] = form
    else:  # GET request
        form = RegistrationForm()
        context['registration_form'] = form
    return render(request, 'accounts/register.html', context)


def logout_view(request):
    logout(request)
    return redirect('home')


def login_view(request):
    context = {}

    user = request.user
    if user.is_authenticated:
        return redirect("home")

    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user:
                context = {
                    "email": email
                }
                login(request, user)
                return redirect('experiments')

    else:
        form = AccountAuthenticationForm()
    context['login_form'] = form
    return render(request, 'accounts/login.html', context)


def account_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    context = {}
    if request.POST:
        form = AccountUpdateFrom(request.POST, instance=request.user)
        if form.is_valid():
            form.initial = {
                "email": request.POST['email'],
                "username": request.POST['username'],
            }
            form.save()
            context['success_message'] = "Account Updated"

    else:
        form = AccountUpdateFrom(
            initial={
                "email": request.user.email,
                "username": request.user.username,
            }

        )
    context['account_form'] = form
    return render(request, 'accounts/account.html', context)


def experiments_view(request, message=None):
    print(message)
    context = {}
    print(request)
    print(request.user.email)
    user = Account.objects.get(email=request.user.email)
    if user.is_admin:
        context['exps'] = Room.objects.all()
        context['admin'] = True
    else:
        context['exps'] = Room.objects.filter(email=request.user.email)
    if message == "failed":
        context['modaldisplay'] = True
    return render(request, 'experiments/experiments.html', context)


def verification_view(request, email, token):
    if request.method == "GET":
        try:
            decoded_email = force_text(urlsafe_base64_decode(email))
            user = Account.objects.get(email=decoded_email)
            if user.is_active:
                return redirect("login")

            if not token_generator.check_token(user, token):
                user.delete()
                return render(request, 'accounts/activationFailure.html')

            user.is_active = True
            user.save()
        except Exception as e:
            print(e)
            return render(request, 'accounts/error.html')

    return render(request, 'accounts/activationSuccess.html')


def request_password_reset_email(request):
    context = {}
    if request.method == "GET":
        return render(request, 'accounts/reset-password-email.html')

    if request.method == "POST":
        email = request.POST['email']
        account = Account.objects.filter(email=email).first()
        if account:
            email_to_send = generate_activation_email(request, account, email, 'request-reset-link')
            email_to_send.send(fail_silently=False)
            context['success_message'] = "A Password reset link has been Sent your Email."
            return render(request, 'accounts/reset-password-email.html', context)


def reset_user_password(request, email, token):
    if request.method == "GET":
        context = {
            "email": email,
            "token": token
        }
        user = Account.objects.get(email=force_text(urlsafe_base64_decode(email)))
        if not PasswordResetTokenGenerator().check_token(user, token):
            return render(request, 'accounts/passwordFailure.html')
        else:
            return render(request, 'accounts/reset-user-password.html', context)
    if request.method == "POST":
        user = Account.objects.get(email=force_text(urlsafe_base64_decode(email)))
        if not PasswordResetTokenGenerator().check_token(user, token):
            context = {
                "email": email,
                "token": token
            }

            password1 = request.POST['password1']
            password2 = request.POST['password2']

            if password1 != password2:
                context['error_message'] = "Password do not match"
                return render(request, 'accounts/reset-user-password.html', context)

            user.set_password(password1)
            user.save()
            context['success_message'] = "Password rest successfull.Please login with you new password"
            return render(request, 'accounts/reset-user-password.html', context)
        else:

            return render(request, 'accounts/passwordFailure.html')


def create_room_view(request):
    context = {}
    if request.method == "GET":
        return render(request, 'experiments/createroom.html')

    if request.method == "POST":
        form = CreateRoomForm(request.POST)
        print(form.errors)
        try:
            if form.is_valid():
                room = form.save(commit=False)
                room.email = request.user.email
                room.username = request.user.username

                if request.POST['room_id'] == '':
                    while True:
                        room_id = generate_random_id()
                        if not Room.objects.filter(room_id=room_id).exists():
                            room.room_id = room_id
                            break
                else:
                    room.room_id = request.POST['room_id']

                if request.POST['communication'] == "a":
                    room.is_video_enabled = False
                if request.POST['recording'] == "a":
                    room.is_recording_video_enabled = False
                if request.POST['recording'] == "nr":
                    room.is_recording_video_enabled = False
                    room.is_recording_audio_enabled = False

                if request.POST['transcription'] == "yes":
                    room.is_transcription_enabled = True

                room.save()
                context['success_message'] = "Room Created Successfully"
            else:
                context['room_form'] = form
        except Exception as e:
            raise
        return render(request, 'experiments/createroom.html', context)


def csrf_failure(request, reason=""):
    return redirect('logout')


def generate_activation_email(request, account, email, type):
    domain = get_current_site(request).domain
    encoded_email = urlsafe_base64_encode(force_bytes(email))
    if type == "activate":
        link = reverse(type, kwargs={'email': encoded_email, 'token': token_generator.make_token(account)})
        email_subject = "MaxLab Account Activation"
        message = f"Hello {account.username}\n Please click on the link to activate your account\n"
    else:
        link = reverse("reset-user-password",
                       kwargs={'email': encoded_email, 'token': PasswordResetTokenGenerator().make_token(account)})
        email_subject = "MaxLab Password Reset Link"
        message = f"Hello {account.username}\n Please click on the link to reset your password\n"

    activate_url = "http://" + domain + link

    email_body = message + activate_url
    email = EmailMessage(
        subject=email_subject,
        body=email_body,
        to=[email],
    )

    return email


def download_view(request, type, roomid):
    zip_file = open("D:\\maxlab_project\MaxLabProject\\transcription_app\\transcribe_utility.zip", 'rb')
    response = HttpResponse(zip_file, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="%s"' % 'foo.zip'
    return response


def editExp(request, room_id):
    expObj = Room.objects.get(room_id=room_id)
    print('The object before update is:', expObj)
    if request.method == "POST":

        form = UpdateRoomForm(request.POST,instance=expObj)
        print(form.errors)

        if form.is_valid():
            if request.POST['transcription'] == "yes":
                expObj.is_transcription_enabled = True
            else:
                expObj.is_transcription_enabled = False

            if request.POST['communication'] == "a":
                expObj.is_video_enabled = False
            else:
                expObj.is_video_enabled = True

            if request.POST['recording'] == "a":
                expObj.is_recording_video_enabled = False
            if request.POST['recording'] == "nr":
                expObj.is_recording_video_enabled = False
                expObj.is_recording_audio_enabled = False
            form.save()
            return redirect('experiments')
    return render(request, 'experiments/editRoom.html', {'expObj': expObj})


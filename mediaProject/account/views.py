from django.core.exceptions import ValidationError
from django.utils import timezone

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import BadHeaderError, send_mail
from .models import UserProfile, Friendship
from group.models import Group


def user_login_check(user):
    return user.is_anonymous()


@user_passes_test(user_login_check)
def create_account(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        name = request.POST['name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        date = request.POST['date']
        sex = request.POST['sex']
        user_exist = User.objects.filter(username=username).first()
        email_exist = User.objects.filter(email=email).first()
        if not user_exist:
            if email_exist:
                sms = "%s ya esta siendo usado por otro usuario" % email
                return render(request, 'create_account.html', locals())
            profile = UserProfile()
            profile.born_date = date
            profile.sex = sex
            user = User(username=username, email=email, first_name=name, last_name=last_name)
            user.set_password(password)
            try:
                user.save()
                profile.user = user
                profile.save()
            except ValidationError:
                user.delete()
                sms = "el formato de la fecha esta mal"
                return render(request, 'create_account.html', locals())
            return redirect(reverse('account:dashboard'))
        else:
            sms = "%s ya esta siendo usado por otro, por favor seleccione otro" % username
            return render(request, 'create_account.html', locals())
    else:
        return render(request, 'create_account.html', locals())


@login_required
def user_search(request):
    pass


@login_required
def user_update(request, pk):
    profile = UserProfile.objects.get(user_id=pk)
    return render(request, 'edit_profile.html', locals())


@login_required
def friendship(request, id_receiver):
    user_sender = User.objects.get(id=request.user.id)
    user_receiver = User.objects.get(id=id_receiver)
    friend = Friendship()
    exits = Friendship.objects.filter(receiver_id=id_receiver)
    if exits:
        sms = "ya envio una peticion a %s" % user_receiver.username
        return redirect(reverse("account:dashboard") + "?sms=%s" % sms)
    friend.sender = user_sender
    friend.receiver = user_receiver
    friend.status = 2
    friend.date = timezone.now()
    friend.save()
    sms_ok = "se le ha enviado una peticion a %s" % user_receiver.username
    return redirect(reverse('account:dashboard')+ "?sms_ok=%s" % sms_ok)


def accept_friendship(request, id):
    solicitude = Friendship.objects.get(id=id)
    solicitude.status = 0
    solicitude.save()
    return redirect(reverse('account:dashboard'))


def notification(request):
    friend_request = Friendship.objects.filter(Q(status=2) & Q(receiver=request.user))
    return render(request, 'notification.html', locals())


def users(request):
    users_list = UserProfile.objects.all()
    return render(request, 'users.html', locals())


def user_profile(request, pk):
    profile = UserProfile.objects.get(user_id=pk)
    own = UserProfile.objects.get(user_id=request.user.pk)
    is_my_profile = own == profile
    return render(request, 'user_profile.html', locals())


@login_required
def user_login(request):
    users = UserProfile.objects.filter(is_conected=True).exclude(user_id=request.user.pk)
    friend = Friendship.objects.filter(Q(status=0) & (Q(sender=request.user) | Q(receiver=request.user)))
    return render(request, 'user_login.html', locals())


@login_required
def user_staff_login(request):
    users_staff = UserProfile.objects.filter(is_conected=True, user__is_staff=True).exclude(user_id=request.user.pk)
    return render(request, 'user_staff.html', locals())


@login_required
def dashboard(request):
    if request.method == 'GET':
        if "create-group" in request.GET:
            name = request.GET.get("name-group", None)
            about = request.GET.get("about-group", None)
            if name is not None and about is not None:
                exist = Group.objects.filter(name=name)
                if exist:
                    message_error = "ese grupo ya existe, por favor, escoja otro nombre"
                    return render(request, 'index.html', locals())
                group = Group(name=name, about=about, owner=request.user)
                group.save()
                return redirect(reverse('account:dashboard'))
        else:
            friend_request = Friendship.objects.filter(Q(status=2) & Q(receiver=request.user))
            users = UserProfile.objects.filter(is_conected=True)
            user = request.user
            return render(request, 'index.html', locals())
    else:
        if "send" in request.POST:
            email = request.POST.get('email', "")
            subject = request.POST.get('subject', "")
            message = request.POST.get('message', "")
            if email and subject and message:
                try:
                    # email = EmailMultiAlternatives(subject, message, 'rhernandeza@facinf.uho.edu.cu',
                    # ['rhernandeza@facinf.uho.edu.cu'])
                    # message_html = '<h1>' + message + '</h1>'
                    # email.attach_alternative(message_html, 'text/html')
                    # email.send(False)
                    subject = '[The Wall] ' + subject
                    send_mail(subject, message, 'rhernandeza@facinf.uho.edu.cu', ['rhernandeza@facinf.uho.edu.cu'],
                              False, 'rhernandeza', 'seabiskuit32+')
                except BadHeaderError:
                    error = True
                    message_error = 'Se ha encontrado una cabecera invalida'
                    return render(request, 'index.html', locals())
                return render(request, 'index.html', locals())
            else:
                error = True
                message_error = 'Debe de llenar todos los campos'
                return render(request, 'index.html', locals())
        else:  # si "save" in request.POST
            full_name = request.POST.get('name', "")
            email = request.POST.get('email', "")
            user = request.user
            user.first_name = full_name.split(" ")[0]
            user.last_name = " ".join(full_name.split(" ")[1:])
            user.email = email
            user.save()
            return render(request, 'index.html', locals())


def information(request):
    mesagge = 'Informaciones recientes'
    return render(request, 'informations.html', locals())


def login_view(request):
    if request.user.is_authenticated():
        return redirect(reverse('account:dashboard') + "?sms_ok=usted ya esta logeado")
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is None:
                error = True
                message = 'Usuario o contrasena incorrectos'
                return render(request, 'login.html', locals())
            elif user.is_active:
                login(request, user)
                profile = UserProfile.objects.get(user=user)
                profile.is_conected = True
                profile.save()
                return redirect(reverse('account:dashboard'))
            else:
                error = True
                message = 'Este usuario ha sido baneado, por favor contacte al administrador'
                return render(request, 'login.html', locals())
        else:
            return render(request, 'login.html', locals())


@login_required
def logout_view(request):
    profile = UserProfile.objects.get(user=request.user)
    profile.is_conected = False
    profile.save()
    logout(request)
    return redirect(reverse('account:login') + "?sms_ok=hasta pronto")


def chat(request):
    my = UserProfile.objects.get(user=request.user)
    return render(request, 'chat.html', locals())


def contact_us(request):
    profile = UserProfile.objects.get(user_id=request.user.pk)
    return render(request, 'contact.html', locals())


def terms(request):
    return render(request, 'terms.html')


def about(request):
    return render(request, 'about.html')


def privacy(request):
    return render(request, 'privacy.html')

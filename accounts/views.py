from django.shortcuts import render, redirect
from django.http import HttpResponse
from . forms import UserForm
from vendor.forms import VendorForm
from . models import User, UserProfile
from django.contrib import messages,auth
from .utils import detectUser, send_verification_email
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator




# restrict customer from accessing vendor page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# restrict vendor from accessing customer page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied



def registeruser(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # create the user using form
            # password = form.cleaned_data['password']
            # user = form.save(commit=False)
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # user.save()

            # Create the user using create_user methode
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password
            )
            user.role = User.CUSTOMER
            user.save() 

            #send verification mail
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)
            messages.success(request, 'Congrats, your account created successfully !')
            return redirect('login')
        else:
            print(form.errors)
    else:
        form = UserForm()
    return render(request, 'accounts/user_register.html', {'form': form})


def register_restaurant(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
            )
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            #send verification mail
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Your request for account registration was sucessfully, Please wait for Approval')
            return redirect('login')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = UserForm
        v_form = VendorForm

    context = {
        'form': form,
        'v_form': v_form,
    }
    return render(request, 'accounts/register_restaurant.html', context)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations, Your account is activated.')
        return redirect('myaccount')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('myaccount')


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        print(request.POST)
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            print(request.POST)
            auth.login(request, user)
            messages.success(request, 'Your are logged in sucessfully')
            return redirect('home')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    else:
        return render(request, 'accounts/login.html')


def logout(request):
    auth.logout(request)
    messages.success(request, 'Your are logged out')
    return redirect('login')

@login_required(login_url='login')
def myaccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custdashboard(request):
    return render(request, 'accounts/custdashboard.html')


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendordashboard(request):
    return render(request, 'accounts/vendordashboard.html')
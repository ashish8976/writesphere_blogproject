from django.shortcuts import render,redirect
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.conf import settings
import random
from . models import User
import time

# Create your views here.
def index(request):
    return render (request,'index.html')

def explore(request):
    return render (request,'explore.html')

def blog_details(request):
    return render (request,'blog_details.html')

def profile(request):
    return render(request,'profile.html')


def register(request):
    if request.method =="POST":
        if User.objects.filter(email=request.POST['email']).exists():
            return render(request, 'register.html', {'msg': 'Email already exists'})
    
        if User.objects.filter(username=request.POST['username']).exists():
            return render(request, 'register.html', {'msg': 'Username already taken, please choose another'})
        
        if request.POST['password'] != request.POST['cpassword']:
            return render(request,'register.html',{'msg','password and confirm password not match'})
        
        User.objects.create(
            fname=request.POST['fname'],
            lname=request.POST['lname'],
            username=request.POST['username'],
            email=request.POST['email'],
            password=make_password(request.POST['password']),
            role=request.POST['role'],
        )
        return render(request, 'login.html', {'msg': 'Registration Successful!'})
    else:
        return render (request,'register.html')


def login(request):
    if request.method == "POST":
        login_input = request.POST['username']
        login_password = request.POST['password']

        try:
            user = User.objects.get(Q(username=login_input) | Q(email=login_input))

            if check_password(login_password,user.password):
                request.session['user_email']=user.email
                request.session['user_name'] = user.username
                request.session['user_role'] = user.role
                return redirect('index')
            else:
                return render(request, 'login.html', {'msg':"Password is not correct"})
        except User.DoesNotExist:
            return render(request, 'login.html', {'msg':"User not found"})
    else:
        return render(request,'login.html')
    
def logout(request):
    request.session.flush()
    return render(request,'login.html')

def author(request):
    return render(request,'author.html')

def forgetpassword(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            otp = random.randint(100001,999999)
            subject = "OTP for forget Password"
            message =f"Hi {user.fname}  {user.lname}  Your OTP  is { str(otp)}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email,]
            send_mail(
                subject,
                message,
                email_from,
                recipient_list,
                fail_silently=False
            )
            request.session['useremail'] = user.email
            request.session['otp'] = str(otp)
            request.session['otp_time'] = time.time()
            return redirect('otp')
        except User.DoesNotExist:
            msg = "Email  does not Exists "
            return render (request, 'forgetpassword.html',{'msg':msg})
    else:
        return render(request,'forgetpassword.html')
    

def otp(request):
    if request.method == "POST":
          #   user = User.objects.get(email = request.session['newemail'])
          
            entered_otp = request.POST.get('uotp')
            session_otp = request.session.get('otp')
            otp_time = request.session.get('otp_time')

            if not session_otp or not otp_time:
                msg = "Session expired. Try again."
                return render(request, 'otp.html', {'msg': msg})
            
            if entered_otp == session_otp:
                del request.session['otp']
                del request.session['otp_time']
                return redirect('resetpassword') 
            
            else:
                 msg = "OTP is invalid"
                 return render(request, 'otp.html', {'msg': msg})

    else:
        return render(request, 'otp.html')

def resetpassword(request):
    if request.method == "POST":
        update_email = request.session.get('useremail')

        if not update_email:
            return redirect ('forgetpassword')
        
        try:
             user = User.objects.get(email = update_email)
             new_password = request.POST.get('newpassword')
             cpassword = request.POST.get('cpassword')

             if new_password == cpassword :
                user.password = make_password(new_password)
                user.save()
                del request.session['useremail']
                return redirect('login')
             else:
                    msg = "Password and Confirm Password doesn't match"
                    return render(request,'resetpassword.html',{'msg':msg})
        except User.DoesNotExist:
            msg = "User not Found"
            return render(request,'forget_password.html')
    else:
        return render(request,'resetpassword.html')
    
def dashboard(request):
    return render (request, 'dashboard.html')


def profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    
    user = User.objects.get(id=user_id)
    return render(request, 'profile.html', {'user': user, 'blogs': []})

def edit_profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    
    user = User.objects.get(id=user_id)

    if request.method == "POST":
        user.fname = request.POST.get('fname')
        user.lname = request.POST.get('lname')
        user.bio = request.POST.get('bio')

        if request.FILES.get('profile_photo'):
            user.profile_photo = request.FILES['profile_photo']

        user.save()
        return redirect('profile')
    
    return render(request, 'edit_profile.html', {'user': user})
        
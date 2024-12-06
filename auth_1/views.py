from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.views.generic import View
# to activate user account
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.urls import NoReverseMatch,reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,force_str,DjangoUnicodeDecodeError

#reset password generator
from django.contrib.auth.tokens import PasswordResetTokenGenerator

# getting tokens from utils

from .utils import TokenGenerator,generate_token

# emails
from django.core.mail import send_mail,EmailMultiAlternatives
from django.core.mail import BadHeaderError,send_mail
from django.core import mail
from django.conf import settings
from django.core.mail import EmailMessage


from django.contrib.auth.decorators import login_required
from .models import UserProfile
from my_app.forms import UserProfileForm
from django.contrib.auth.models import User



#threading

import threading

class EmailThread(threading.Thread):
    def __init__(self,email_message):
        self.email_message=email_message
        threading.Thread.__init__(self)
        
    def run(self):
        self.email_message.send()


# Create your views here.


def signup(request):
    if request.method == 'POST':

        email=request.POST.get('email')
        pass1=request.POST.get('pass1')
        pass2=request.POST.get('pass2')
        if pass1 != pass2:

            messages.error(request,"Password do not Match,Please Try Again!")
            return redirect('signup')
        try:
            if User.objects.get(username=email):
                messages.warning(request,"Email Already Exists")
                return redirect('/auth/signup')
        except Exception as identifier:            
            pass 
        try:
            if User.objects.get(email=email):
                messages.warning(request,"Email Already Exists")
                return redirect('/auth/signup')
        except Exception as identifier:
            pass        
       
        user=User.objects.create_user(email, email, pass1)
        profile = UserProfile.objects.create(user=user, bio="" )
        profile.save()
        
        user.is_active=False
        user.save()
        current_site=get_current_site(request)
        email_subject="Activate Your Account"
        message=render_to_string('auth/activate.html',{
            'user':user,
            'domain':'127.0.0.1:8000',
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':generate_token.make_token(user)
        })
        print(f"Sending activation email to {email}")
        email_message=EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email])
        EmailThread(email_message).start()
        messages.info(request,'Activate Your Acount by Cliking link on your email')
        # messages.info(request,"Signup Successful Please Login")
        return redirect('/auth/login')    
    return render(request,"auth/signup.html")        


class activateAccountView(View):
    def get(self,request,uidb64,token):
        try:
            uid=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=uid)
        except Exception as identifier:
            user =None
            
        if user is not None and generate_token.check_token(user,token):
            user.is_active=True
            user.save()
            messages.info(request,"Account activated Successfully")
            return redirect('/auth/login')
        return render(request,'auth/activate.html')
        
        

def handlelogin(request):

    if request.method == "POST":
        username=request.POST.get('email')
        userpassword=request.POST.get('pass1')
        myuser=authenticate(username=username,password=userpassword)

        if myuser is not None:
            login(request,myuser)
            messages.info(request,"Login Success")
            return redirect('/')
        else:
            messages.error(request,"Invalid Credentials")
            return redirect('/auth/login')

    
    return render(request,'auth/login.html')


def handlelogout(request):
    logout(request)
    messages.success(request,"Logout Successful")
    return redirect('/auth/login')

class ResetRequestEmailView(View):
    def get (self,request):
        return render(request,'auth/request-reset-email.html')
    
    def post(self,request):
        email=request.POST['email']
        user=User.objects.filter(email=email)
        
        
        if user.exists():
            current_site=get_current_site(request)
            email_subject='[Reset Your Password]'
            message=render_to_string('auth/reset-user-password.html',{
            'domain':'127.0.0.1:8000',
            'uid':urlsafe_base64_encode(force_bytes(user[0].pk)),
            'token':PasswordResetTokenGenerator().make_token(user[0])
            })
            email_message=EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email])
            EmailThread(email_message).start()
            messages.info(request,'WE HAVE SENT YOU AN EMAIL WITH INSTRUCTIONS ON HOW TO RESET YOUR PASSWORD')
            return render (request,'auth/request-reset-email.html')
        
class SetNewPasswordView(View):
    def get(self,request,uidb64,token):
        context={
            'uidb64':uidb64,
             'token':token
        }
        
        try:
            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=user_id)
            
            if not PasswordResetTokenGenerator().check_token(user,token):
                messages.warning(request,"Password Reset Link is Invalid")
                return render (request,'auth/request-reset-email.html')
            
        except DjangoUnicodeDecodeError as identifier:
            pass
        
        return render (request,'auth/set-new-password.html',context)
    def post(self,request,uidb64,token):
        context={
            'uidb64':uidb64,
             'token':token
        }
        pass1=request.POST.get('pass1')
        pass2=request.POST.get('pass2')
        if pass1 != pass2:
            messages.error(request,"Password do not Match,Please Try Again!")
            return redirect(request,'auth/set-new-password.html',context)
        
        try:
            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=user_id)
            user.set_password(pass1)
            user.save()
            messages.success(request,"Password Reset Link is Successful Please Login with New Password")
            return redirect('/auth/login/')
              
        except DjangoUnicodeDecodeError as identifier:
             messages.error(request,"Something Went Wrong") 
             return render(request,'auth/set-new-password.html',context) 
         
        return render(request,'auth/set-new-password.html',context) 
    
    
    
    
    
    
    
@login_required
def profile_view(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = None
    return render(request, 'auth/profile_view.html', {'profile': profile})




@login_required
def edit_profile(request):
    try:
        # profile = request.user.profile
        profile , created = UserProfile.objects.get_or_create(user=request.user)
    except UserProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user  
            user_profile.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('/auth/profile/')  
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'auth/profile_edit.html', {'form': form})





@login_required
def delete_profile(request):
    user = request.user
    # Delete the associated UserProfile if it exists
    try:
        profile = UserProfile.objects.get(user=user)
        profile.delete()
    except UserProfile.DoesNotExist:
        pass
    # Delete the user
    user.delete()
    messages.success(request, "Your account has been deleted successfully.")
    return redirect('/auth/signup/')  # Redirect to signup page after deletion
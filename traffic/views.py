import io
from django.shortcuts import render, redirect
from .forms import AccidentForm, UserRegister, UserLogin, CarImageForm,ReportForm, ProfileAccidentForm,CommentForm
from django import forms
from .models import Profile, RegistrationImage,CarImage,Accident,Report,Involved
from django.forms.models import modelform_factory
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.forms import modelformset_factory
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages
from easy_pdf.rendering import render_to_pdf
from django.core.mail import EmailMessage

def home(request):
    return render(request, 'home.html')
  
def involved(request):
    if request.user.is_anonymous:
        return redirect('login')
    error=""
    if request.method=='POST':
        if request.POST['involved']:
            num=request.POST['involved']
            return redirect('create-accident',num)
        else:
            error="Please add number of involved people"
    context = {
        "error":error,
    }

    return render(request, "involved.html",context)

def accidentCreate(request,involved):
    if request.user.is_anonymous:
        return redirect('login')
    involvedFormSet = modelformset_factory(
            Profile,
            form = ProfileAccidentForm,
            fields=('civil_id','email'),
            labels={'civil_id':'Civil id',
            'email':'Email'},
            extra = involved-1
        )
    registrationImageFormSet = modelformset_factory(
            RegistrationImage,
            form = forms.ModelForm,
            fields=('regist_image',),
            labels={'regist_image':'Involved Car registration'},
            extra = involved
        )
    involvedFormset = involvedFormSet(queryset=Profile.objects.none())
    registrationFormset = registrationImageFormSet(queryset=RegistrationImage.objects.none())
    accidentForm=AccidentForm()
    commentForm=CommentForm()
    car_images_form=CarImageForm()
    if request.method == "POST":
        accidentForm = AccidentForm(request.POST, request.FILES)
        involvedFormset = involvedFormSet(request.POST, queryset=Profile.objects.none())
        car_images_form=CarImageForm(request.POST, request.FILES)
        commentForm=CommentForm(request.POST)
        registrationFormset=registrationImageFormSet(
                request.POST,
                request.FILES,
                queryset=RegistrationImage.objects.none(),
            )
        car_images_form=CarImageForm(request.POST,request.FILES)
        print (involvedFormset)


        if accidentForm.is_valid()  and registrationFormset.is_valid() and car_images_form.is_valid() and commentForm.is_valid():
            accident=accidentForm.save()
            myProfile=Profile.objects.get(user_id=request.user.id)
            accident.involved_people.add(myProfile)
            comment=commentForm.save(commit=False)
            comment.accident=accident
            comment.involved=request.user.profile
            comment.status="Accepted"
            comment.save()
            for x in involvedFormset:
                if x.cleaned_data:
                    pop=x.save(commit=False)
                    profile,created=Profile.objects.get_or_create(civil_id=pop.civil_id)
                    profile.email=pop.email
                    profile.save()
                    if profile.civil_id:
                        accident.involved_people.add(profile)
                        involvedx,created=Involved.objects.get_or_create(accident=accident,involved=profile,status="No Response")
                        if(created):
                            involvedx.save()


            for x in registrationFormset:
                if x.cleaned_data:
                    regist_images=x.save(commit=False)
                    regist_images.accident=accident
                    regist_images.save()
            files = request.FILES.getlist('file_field')
            for file in files:
                car_images=CarImage.objects.create(accident_image=file,accident=accident)
                car_images.save()
            regist_images=accident.save()

            messages.success(request, "Successfully Submitted!")
            email(request,accident)
            return redirect('profile')
    context={
    "involved":involved,
    "commentForm":commentForm,
        "involvedFormset":involvedFormset,
        "accidentForm":accidentForm,
        "registrationFormset":registrationFormset,
        "car_images_form":car_images_form,
    }
    return render(request, "accident.html", context )

def user_register(request):
    form = UserRegister()
    error=""
    popForm=modelform_factory(Profile, form=forms.ModelForm,fields=('civil_id','phone_no'),labels={'civil_id':'Civil id', 'phone_no':'Mobile Number'})
    if request.method == 'POST':
        form = UserRegister(request.POST)
        popForm=popForm(request.POST)
        if form.is_valid() and popForm.is_valid():
            user = form.save(commit=False)
            user.set_password(user.password)
            user.save()
            pop=popForm.save(commit=False)
            pop.user=user
            pop.save()
            login(request, user)
            return redirect('accident-report')
        elif User.objects.get(username=request.POST['username']):
            error="This username already exists"

    context = {
        "form":form,
        "popForm":popForm,
        "error":error,
    }
    return render(request, 'register.html', context)

def user_login(request):
    form = UserLogin()
    error=""
    if request.method == 'POST':
        form = UserLogin(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            auth_user = authenticate(username=username, password=password)
            if auth_user is not None:
                login(request, auth_user)
                # Where you want to go after a successful login
                if request.user.is_staff:
                    return redirect('staff-accident-list')
                else:
                    return redirect('accident-report')
            else:
                error="Invalid username or password"
                    

    context = {
    "error":error,
        "form":form,
    }
    return render(request, 'login.html', context)

def user_profile(request):
    if request.user.is_anonymous:
        return redirect('login')

    accidents=Accident.objects.filter(involved_people=request.user.profile)
    profile=request.user.profile
    prof_form = modelform_factory(Profile, form=forms.ModelForm,fields=('phone_no',),labels={'phone_no':'Mobile Number'})
    user_form = modelform_factory(User, form=UserRegister,fields=('password','email',))
    user_form = user_form(instance=profile.user)
    prof_form = prof_form(instance=profile)
    if request.method == "POST":
        prof_form = modelform_factory(Profile, form=forms.ModelForm,fields=('phone_no',),labels={'phone_no':'Mobile Number'})
        user_form = modelform_factory(User, form=forms.ModelForm,fields=('password','email',))
        prof_form = prof_form(request.POST,instance=profile)
        user_form = user_form(request.POST,instance=request.user)
        if prof_form.is_valid() and user_form.is_valid():
            user=user_form.save(commit=False)
            user.set_password(user.password)
            user.save()
            prof_form.save()
            return redirect('login')
    context={
        "accidents":accidents,
        "prof_form":prof_form,
        "user_form":user_form, 
    }
    return render(request, 'profile.html',context)

def updateProfile(request):
    if request.user.is_anonymous:
        return redirect('login')
    profile=request.user.profile
    prof_form = modelform_factory(Profile, form=forms.ModelForm,fields=('phone_no',),labels={'phone_no':'Mobile Number'})
    user_form = modelform_factory(User, form=UserRegister,fields=('username','password','email',))
    user_form = user_form(instance=profile.user)
    prof_form = prof_form(instance=profile)
    if request.method == "POST":
        prof_form = modelform_factory(Profile, form=forms.ModelForm,fields=('phone_no',),labels={'phone_no':'Mobile Number'})
        user_form = modelform_factory(User, form=forms.ModelForm,fields=('password','email',))
        prof_form = prof_form(request.POST,instance=profile)
        user_form = user_form(request.POST,instance=request.user)
        if prof_form.is_valid() and user_form.is_valid():
            user=user_form.save(commit=False)
            user.set_password(user.password)
            user.save()
            prof_form.save()
            return redirect('login')    
    
    context = {
        "prof_form":prof_form,
        "user_form":user_form,
        }
    return render(request, 'updateProfile.html', context)

def user_logout(request):
    logout(request)
    return redirect("home")

def report(request):
    return render(request, 'report.html')


def email(request,context):
    subject = 'Accident'     
    for involved in context.involved_set.all():
        html_message = render_to_string('trial.html',{'context':context,'profile':involved.id})
        print(involved.id)
        plain_message = strip_tags(html_message)  
        send_mail(subject, plain_message, '', [involved.involved.email], html_message=html_message)  
    
def accidentList(request):
    if request.user.is_anonymous:
        return redirect('login')
    myProfile=Profile.objects.get(user=request.user)
    accidents=Accident.objects.filter(involved=myProfile)
    context={
        'accidents':accidents,  
    }

    return render(request, "accidentList.html",context)

def accidentDetail(request, accident_id):
    if request.user.is_anonymous:
        return redirect('login')
    accident = Accident.objects.get(id=accident_id)
    involved = accident.involved_people.all()
    involved_comment = Involved.objects.filter(accident=accident)
    car_images=CarImage.objects.filter(accident=accident)
    regis_images=RegistrationImage.objects.filter(accident=accident)

    context = {
    "involved_comment":involved_comment,
        "accident": accident,
        "involved":involved,
        "car_images":car_images,
        "regis_images":regis_images
        }
    return render(request, 'accidentDetail.html', context)


def accidentListStaff(request):
    if request.user.is_anonymous:
        return redirect('login')
    if request.user.is_staff:
        accidents=Accident.objects.exclude(report= None)
        new_accidents=Accident.objects.filter(report= None)
        context={
            'accidents':accidents, 
            'new_accidents': new_accidents, 
        }
        return render(request, 'accidentListStaff.html', context)
    else:
        return render(request, 'permission.html')

def accidentDetailStaff(request, accident_id):
    if request.user.is_anonymous:
        return redirect('login')
    if request.user.is_staff:
        accident = Accident.objects.get(id=accident_id)
        involved = Involved.objects.filter(accident=accident)
        car_images=CarImage.objects.filter(accident=accident)
        regis_images=RegistrationImage.objects.filter(accident=accident)
        form=ReportForm()
        if(request.method=='POST'):
            form=ReportForm(request.POST)
            if form.is_valid():
                report=form.save(commit=False)
                report.accident=accident
                report.detective=request.user
                report.save()
                messages.success(request, "Accident"+str(accident_id)+" is reported successfully")
                send_pdf(request,accident)
                accident.status='Accepted'
                accident.save()
                return redirect('staff-accident-list')
    
        context = {
            "accident": accident,
            "form":form,
            "involved": involved,
            "car_images":car_images,
            "regis_images":regis_images
            }
        return render(request, 'accidentDetailStaff.html', context)
    else:
        return render(request, 'permission.html')




def compliance(request,accident_id,involved_id):
    accident=Accident.objects.get(id=accident_id)
    Error_messages=""
    involved=Involved.objects.get(id=involved_id)
    form=CommentForm(instance=involved)
    if(request.method=='POST'):
            form=CommentForm(request.POST,instance=involved)
            if form.is_valid():
                comment=form.save(commit=False)
                comment.status='Accepted'
                comment.save()
                messages.success(request, "Your remark on "+str(accident_id)+" is reported successfully")
                return redirect('home')
            else:
                Error_messages="Please type something." 
    context={
        "commentForm":form,
        "accident_id":accident_id,
        "involved_id":involved_id,
        "error":Error_messages
    }
    return render(request, 'compliance.html', context )            

def declined(request,accident_id,involved_id):
    accident=Accident.objects.get(id=accident_id)
    Error_messages=""
    involved=Involved.objects.get(id=involved_id)
    form=CommentForm(instance=involved)
    
    if(request.method=='POST'):
            form=CommentForm(request.POST, instance=involved)
            if form.is_valid():
                comment=form.save(commit=False)
                comment.status='Declined'
                comment.save()
                messages.success(request, "Your remark on "+str(accident_id)+" is reported successfully")
                return redirect('home')
            else:
                Error_messages="Please type something."     
    context={
        "commentForm":form,
        "accident_id":accident_id,
        "involved_id":involved_id,
        "error":Error_messages
    }
    return render(request, 'decline.html', context ) 


def send_pdf(request,accident):
    involved = accident.involved_people.all()
    car_images=CarImage.objects.filter(accident=accident)
    regis_images=RegistrationImage.objects.filter(accident=accident)
    email=[]     
    for involvedx in involved:
        email.append(involvedx.email)           
    post_pdf = render_to_pdf(
        'report_email.html',
        { "accident": accident,
            "involved": involved,
            "user":request.user,
            "registrationimages":regis_images},
)
    msg = EmailMessage(
        'Approved report', #subject
        'Your application was approved and below is the printable report.', #content
        '', #from
        email #to
        )
    msg.attach('file.pdf', post_pdf, 'application/pdf')
    msg.send()


def report(request):
   return render(request, 'report.html')




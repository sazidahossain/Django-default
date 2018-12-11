from django.shortcuts import render, redirect
from .forms import AccidentForm
from django import forms
from .models import Population
from django.forms.models import modelform_factory
from django.core.mail import send_mail
from django.conf import settings
# Create your views here.
def accidentCreate(request):
        # return redirect('login')
    # followers=[follow.follower.email for follow in Follow.objects.filter(followed=request.user)]
    form=AccidentForm()
    involvedForm=modelform_factory(Population,form=forms.ModelForm, fields=('civil_id',))
    if request.method == "POST":
        form = AccidentForm(request.POST, request.FILES)
        if form.is_valid():
            accident=form.save()
            myPopulation=Population.objects.get(id=request.user.id)
            p, created = Population.objects.get_or_create(civil_id=request.POST['civil_id'])
            accident.involved.add(myPopulation,p)
            accident.save()
            # sendemail(request.user,followers)
            # messages.success(request, "Successfully Created!")
            return redirect('create-accident')
        print (form.errors)

    context={
        "involvedForm":involvedForm,
        "form":form,

    }
    return render(request, "test.html", context )


def email(request):
    subject = 'Thank you for registering to our site'
    message = ' it  means a world to us '
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['sazidahossain@gmail.com',]
    send_mail( subject, message, email_from, recipient_list )    
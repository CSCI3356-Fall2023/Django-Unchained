from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from django.contrib import messages
# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Welcom {username}!')
            return redirect('homepage')
    else:
        form = RegisterForm()
    return render (request, 'templates:login.html', {'form':form})
        
def login(request):
    template = loader.get_template('login.html')
    context = {
        'Title': 'Sign into your Account', 
        'FieldOne': 'Email',
        'FieldTwo': 'Password'
    }
    return HttpResponse(template.render(context, request))

@login_required
def profile(request):
    return render(request, 'users/profile.html')
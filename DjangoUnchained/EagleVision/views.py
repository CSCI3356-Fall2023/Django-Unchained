from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# Create your views here.

def login(request):
    template = loader.get_template('login.html')
    context = {
        'Title': 'Sign into your Account', 
        'FieldOne': 'Email',
        'FieldTwo': 'Password',
        'Button': 'Login'
    }
    return HttpResponse(template.render(context, request))

def forgot(request):
    template = loader.get_template('login.html')
    context = {
        'Title': 'Reset Password', 
        'FieldOne': 'Email',
        'FieldTwo': 'New Password',
        'Button': 'Confirm'
    }
    return HttpResponse(template.render(context, request))

def signup(request):
    template = loader.get_template('login.html')
    context = {
        'Title': 'Sign Up', 
        'FieldOne': 'Email',
        'FieldTwo': 'Password',
        'Button': 'Sign Up'
    }
    return HttpResponse(template.render(context, request))

def signin(request):
    template = loader.get_template('landing.html')
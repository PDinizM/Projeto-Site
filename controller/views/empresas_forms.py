from django.shortcuts import render, redirect

def create(request):

    return render(
        request, 
        'controller/create.html'
    )
    
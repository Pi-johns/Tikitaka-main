from django.shortcuts import render

def terms(request):
    return render(request, 'term.html')
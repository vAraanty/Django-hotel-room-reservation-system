from django.shortcuts import render


def index(request):
    context = {
        'title': 'Caravel Hotel',
    }
    return render(request, 'index.html', context)

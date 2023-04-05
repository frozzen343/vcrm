from django.shortcuts import render


def main(request):
    template_name = 'main/main.html'

    return render(request, template_name)
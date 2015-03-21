from guestbook.response import TemplateResponse


def home(request):
    return TemplateResponse('home.html')

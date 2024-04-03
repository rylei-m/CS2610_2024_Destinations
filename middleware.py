from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Session

def session_middleware(get_response):
    def middleware(request):
        if not hasattr(request, 'user'):
            request.user = None

        session_token = request.COOKIES.get('session_token')
        if session_token:
            try:
                session = Session.objects.get(token=session_token)
                request.user = session.user
            except Session.DoesNotExist:
                request.user = None
        else:
            request.user = None

        paths_not_required_auth = [
            reverse('AssnDestinationsMyApp:new_user'),
            reverse('AssnDestinationsMyApp:register_user'),
            reverse('AssnDestinationsMyApp:new_session'),
            reverse('AssnDestinationsMyApp:create_session'),
            '/',
        ]

        if not request.user and request.path not in paths_not_required_auth:
            return HttpResponseRedirect(reverse('AssnDestinationsMyApp:new_session'))

        response = get_response(request)
        return response

    return middleware

"""
def session_middleware(get_response):
    def middleware(request):
        session_token = request.COOKIES.get('session_token')
        if session_token:
            try:
                session = Session.objects.get(token=session_token)
                request.user = session.user
            except Session.DoesNotExist:
                request.user = None

        paths_not_required_auth = [
            reverse('AssnDestinationsMyApp:new_user'),
            reverse('AssnDestinationsMyApp:register_user'),
            reverse('AssnDestinationsMyApp:new_session'),
            reverse('AssnDestinationsMyApp:create_session'),
            '/',
        ]

        if not request.user and request.path not in paths_not_required_auth:
            return HttpResponseRedirect(reverse('AssnDestinationsMyApp:new_session'))

        response = get_response(request)
        return response

    return middleware
"""
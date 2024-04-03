from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, HttpResponseRedirect
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponseRedirect, HttpResponse
from .models import User, Session, Destination
from .forms import DestinationForm

def home(request):
    destinations = Destination.objects.filter(share_publicly=True).order_by('-created_at')[:5]
    return render(request, 'home.html', {'destinations': destinations})

def new_user(request):
    return render(request, 'new_user.html')

def new_session(request):
    return render(request, 'new_session.html')

def register_user(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        hashed_password = make_password(password)
        user = User(email=email, name="", password=hashed_password)
        user.save()
        return redirect('/destinations')
    '''
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        password = make_password(password)
        user = User(email=email, password_hash=password)
        user.save()
        return redirect('/destinations')
'''

def login_user(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.filter(email=email).first()

        if user and check_password(password, user.password):
            token = get_random_string(40)
            Session.objects.create(user=user, token=token)
            response = HttpResponseRedirect('/')
            response.set_cookie('session_token', token, httponly=True, path='/')
            return response
        else:
            return render(request, 'login.html', {'error': 'Invalid email or password'})
    return render(request, 'login.html')

def create_user(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            return render(request, 'new_user.html', {'error': 'A user with this email already exists.'})

        user = User.objects.create_user(email=email, password=password)
        
        return redirect('new_session')

    else:
        return render(request, 'new_user.html')

    return HttpResponse("Unexpected error", status=400)

def create_session(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(f"Attempting login for {email}")  # Debug print

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            print("User does not exist")  # Debug print
            return render(request, 'new_session.html', {'error': 'Invalid email or password.'})

        if user and check_password(password, user.password):
            token = get_random_string(40)
            Session.objects.update_or_create(user=user, defaults={'token': token})
            response = HttpResponseRedirect('/')
            response.set_cookie('session_token', token, httponly=True, path='/')
            print(f"Login successful, token set: {token}")  # Debug print
            return response
        else:
            print("Password check failed")  # Debug print
            return render(request, 'new_session.html', {'error': 'Invalid email or password.'})

    return render(request, 'new_session.html')

def destroy_session(request):
    response = HttpResponseRedirect('/')
    response.delete_cookie('session_token')
    return response

def list_destinations(request):
    current_user = get_current_user(request)
    if current_user is None:
        return HttpResponseRedirect('/sessions/new')

    destinations = Destination.objects.filter(user=current_user)
    return render(request, 'list_destinations.html', {'destinations': destinations})

def new_destination(request):
    if request.method == 'POST':
        form = DestinationForm(request.POST)
        if form.is_valid():
            destination = form.save(commit=False)
            current_user = get_current_user(request)
            if not current_user:
                return HttpResponseRedirect('/sessions/new')
            destination.user = current_user
            destination.save()
            return redirect('home')
    else:
        form = DestinationForm()
    return render(request, 'new_destination.html', {'form': form})

def create_destination(request):
    if request.method == "POST":
        user = get_current_user(request)
        if user is None:
            return HttpResponseRedirect('/sessions/new')

        name = request.POST.get('name')
        review = request.POST.get('review')
        rating = request.POST.get('rating')
        share_publicly = 'share_publicly' in request.POST
        print("log for destinations")

        Destination.objects.create(
            user=user,
            name=name,
            review=review,
            rating=rating,
            share_publicly=share_publicly
        )
        return HttpResponseRedirect('/destinations')
    else:
        pass

def edit_destination(request, id):
    destination = get_object_or_404(Destination, id=id, user=get_current_user(request))
    if request.method == "GET":
        return render(request, 'edit_destination.html', {'destination': destination})
    elif request.method == "POST":
        destination.name = request.POST['name']
        destination.review = request.POST['review']
        destination.rating = request.POST['rating']
        destination.share_publicly = request.POST.get('share_publicly', False) == 'on'
        destination.save()
        return HttpResponseRedirect('/destinations')

def destroy_destination(request, id):
    if request.method == "POST":
        destination = get_object_or_404(Destination, id=id, user=get_current_user(request))
        destination.delete()
        return HttpResponseRedirect('/destinations')

def get_current_user(request):
    session_token = request.COOKIES.get('session_token')
    if session_token:
        try:
            session = Session.objects.get(token=session_token)
            return session.user
        except Session.DoesNotExist:
            return None
    return None

def index(request):
    context = {
        'welcome_message': 'Welcome to the Travel Log',
    }
    return render(request, 'index.html', context)

def some_protected_view(request):
    if not get_current_user(request):
        return HttpResponseRedirect('/sessions/new')

def logout_user(request):
    response = HttpResponseRedirect('/')
    response.delete_cookie('session_token')
    return response
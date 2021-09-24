from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def index(request):
    # if no user is signed in return to login page:
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("users:login"))
    return render(request, "users/user.html")


def login_view(request):
    if request.method == "POST":
        # Accessing the username and password from form data
        username = request.POST["username"]
        password = request.POST["password"]
        
        # Check if username and password are correct, returning User object if so
        user = authenticate(request, username=username, password=password)

        # if user object is returned, log in and route to index page
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse("users:index"))
        # otherwise, return login page again with new content
        else: 
            return render(request, "users/login.html", {
                "message": "Invalid Credentials"
            })
            
    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    return render(request, "users/login.html", {
        "message": "Logged Out"
    })
from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from .models import User

# Create your views here.
def index(request):
    return render(request, 'MentalMathWebsite/index.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST["email"]
        #check if user exists
        if len(User.objects.filter(username=username)) > 0:
            return render(request, "MentalMathWebsite/register.html", {
                "message": "Username is not unique"
            })
        
        newUser = User.objects.create_user(username, email, password)
        newUser.save()
        login(request, newUser)
        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, "MentalMathWebsite/register.html", {
            "message": ""
        })

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user is not None:
            print("user is being logged in")
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "MentalMathWebsite/login.html",{
                "message": "Invalid credentials."
            })

    return render(request, "MentalMathWebsite/login.html", {
        "message": ""
    })

def logout_view(request):
    logout(request)
    return render(request, "MentalMathWebsite/index.html")

def profile(request):
    if request.user.is_authenticated:
        return render(request, "MentalMathWebsite/profile.html")
    else:
        return HttpResponse("Please log in")
from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from .models import User, Submission, UserProfilePicture

# Create your views here.
def index(request):
    return render(request, 'MentalMathWebsite/index.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST["email"]
        profilePicture = request.POST["profilePicture"]
        
        #check if user exists
        if len(User.objects.filter(username=username)) > 0:
            return render(request, "MentalMathWebsite/register.html", {
                "message": "Username is not unique"
            })
        

        newUser = User.objects.create_user(username, email, password)
        newUser.save()
        if profilePicture != "":
            newProfilePic = UserProfilePicture(user=newUser, image=profilePicture)
            newProfilePic.save()

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
        user = User.objects.get(username=request.user.username)

        submissions = Submission.objects.filter(user=user)

        addition_avg_succ_resp_time = 0
        count = 0
        for sub in submissions:
            if sub.typeOfProblem == "+" and sub.isCorrect == True:
                addition_avg_succ_resp_time = (addition_avg_succ_resp_time*count / (count + 1.0)) + (sub.timeToFinish / (count + 1.0))
                count = count + 1
        subtraction_avg_succ_resp_time = 0
        count = 0
        for sub in submissions:
            if sub.typeOfProblem == "-" and sub.isCorrect == True:
                subtraction_avg_succ_resp_time = (subtraction_avg_succ_resp_time*count / (count + 1.0)) + (sub.timeToFinish / (count + 1.0))
                count = count + 1
        multiplication_avg_succ_resp_time = 0
        count = 0
        for sub in submissions:
            if sub.typeOfProblem == "*" and sub.isCorrect == True:
                multiplication_avg_succ_resp_time = (multiplication_avg_succ_resp_time*count / (count + 1.0)) + (sub.timeToFinish / (count + 1.0))
                count = count + 1
        division_avg_succ_resp_time = 0
        count = 0
        for sub in submissions:
            if sub.typeOfProblem == "/" and sub.isCorrect == True:
                division_avg_succ_resp_time = (division_avg_succ_resp_time*count / (count + 1.0)) + (sub.timeToFinish / (count + 1.0))
                count = count + 1
        profilePic = ""
        if len(UserProfilePicture.objects.filter(user=user)) > 0:
            profilePic = UserProfilePicture.objects.filter(user=user)[0].image

        return render(request, "MentalMathWebsite/profile.html", {
            "addition_avg_succ_resp_time": addition_avg_succ_resp_time,
            "subtraction_avg_succ_resp_time": subtraction_avg_succ_resp_time,
            "multiplication_avg_succ_resp_time": multiplication_avg_succ_resp_time,
            "division_avg_succ_resp_time": division_avg_succ_resp_time,
            "profilePic": profilePic
        })
    else:
        return HttpResponse("Please log in")


def leaderboard(request):
    userList = sorted(User.objects.all(), key= lambda u: u.points, reverse=True)

    return render(request, "MentalMathWebsite/leaderboard.html",{
        "userList": userList
    })
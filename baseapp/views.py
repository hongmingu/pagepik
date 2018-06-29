from django.shortcuts import render

# Create your views here.

def user_main(request, user_username):
    if request.method == "GET":
        return render(request, 'baseapp/user_main.html')
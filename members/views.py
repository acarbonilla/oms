from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def omsLogin(request):
    if request.user.is_authenticated:
        return redirect('group_based_redirect')

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('')
            else:
                return redirect('group_based_redirect')

        else:
            # Return an 'invalid login' error message.
            messages.error(request, "Username and Password didn't match. Try Again")
            return redirect('omsLogin')

    else:
        return render(request, 'members/login.html', {'title': 'OMS Login'})


def omsLogout(request):
    logout(request)
    # messages.success(request, "Successfully Logout.")
    return redirect('omsLogin')

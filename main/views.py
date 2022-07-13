from django.shortcuts import render


def index(response):
    # user verified
    if response.COOKIES.get('attendance_verified'):
        return render(response, "main/home.html", {})

    # not verified, but sent code
    if response.method == "POST":
        if response.POST.get('code'):
            pass

    return render(response, "main/verify.html", {})

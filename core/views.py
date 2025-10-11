from django.http import HttpResponse


def home(request):
    """Simple health/home endpoint"""
    return HttpResponse("Avourist v1 is running.")

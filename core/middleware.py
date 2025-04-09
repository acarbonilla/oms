from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import resolve, reverse

APP_GROUP_ACCESS = {
    'c2': {'EV', 'AM', 'EMP'},
    'danao': {'EV_D', 'AM_D', 'EMP_D'},
    # 'rr': {'EV', 'AM', 'EMP'},
}

EXCLUDED_PATHS = ['/admin/', '/login/', '/logout/', '/static/']


class GroupAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow excluded paths
        if any(request.path.startswith(path) for path in EXCLUDED_PATHS):
            return self.get_response(request)

        # If not logged in, redirect to login
        if not request.user.is_authenticated:
            return redirect(reverse('omsLogin'))

        # Superusers can access everything
        if request.user.is_superuser:
            return self.get_response(request)

        # Get the app name from the URL resolver
        try:
            resolver_match = resolve(request.path)
            app_name = resolver_match.app_name  # Needs `app_name` set in urls.py!
        except Exception:
            return HttpResponseForbidden("403 Forbidden: Invalid URL or app.")

        # If the app is not restricted, allow
        if app_name not in APP_GROUP_ACCESS:
            return self.get_response(request)

        # Get allowed groups for the app
        allowed_groups = APP_GROUP_ACCESS[app_name]
        user_groups = set(request.user.groups.values_list('name', flat=True))

        # Allow only if there's an intersection
        if user_groups.intersection(allowed_groups):
            return self.get_response(request)

        return HttpResponseForbidden(f"403 Forbidden: You are not allowed to access the '{app_name}' section.")

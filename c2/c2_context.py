from django.contrib.auth.models import Group, User


def am_group(request):
    if request.user.is_authenticated:
        am = Group.objects.get(name="AM")

        # Get all users in this group
        all_am = am.user_set.all()
    else:
        am = None
        all_am = None
    return {"all_am": all_am, "am": am}


def emp_group(request):
    if request.user.is_authenticated:
        emp = Group.objects.get(name="EMP")

        # Get all users in this group
        all_emp = emp.user_set.all()
    else:
        emp = None
        all_emp = None
    return {"all_emp": all_emp, "emp": emp}
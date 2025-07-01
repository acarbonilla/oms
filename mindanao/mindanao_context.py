from django.contrib.auth.models import Group, User


def am_group_mindanao(request):
    if request.user.is_authenticated:
        am_m = Group.objects.get(name="AM_M")

        # Get all users in this group
        all_am_m = am_m.user_set.all()
    else:
        am_m = None
        all_am_m = None
    return {"all_am_m": all_am_m, "am_m": am_m}


def emp_group_mindanao(request):
    if request.user.is_authenticated:
        emp_m = Group.objects.get(name="EMP_M")

        # Get all users in this group
        all_emp_m = emp_m.user_set.all()
    else:
        emp_m = None
        all_emp_m = None
    return {"all_emp_m": all_emp_m, "emp_d": emp_m}


def ev_group_mindanao(request):
    if request.user.is_authenticated:
        ev_m = Group.objects.get(name="EV_M")

        # Get all users in this group
        all_ev_m = ev_m.user_set.all()
    else:
        ev_m = None
        all_ev_m = None
    return {"all_ev_m": all_ev_m, "ev_d": ev_m}

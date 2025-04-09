from django.contrib.auth.models import Group, User


def am_group_danao(request):
    if request.user.is_authenticated:
        am_d = Group.objects.get(name="AM_D")

        # Get all users in this group
        all_am_d = am_d.user_set.all()
    else:
        am_d = None
        all_am_d = None
    return {"all_am_d": all_am_d, "am_d": am_d}


def emp_group_danao(request):
    if request.user.is_authenticated:
        emp_d = Group.objects.get(name="EMP_D")

        # Get all users in this group
        all_emp_d = emp_d.user_set.all()
    else:
        emp_d = None
        all_emp_d = None
    return {"all_emp_d": all_emp_d, "emp_d": emp_d}


def ev_group_danao(request):
    if request.user.is_authenticated:
        ev_d = Group.objects.get(name="EV_D")

        # Get all users in this group
        all_ev_d = ev_d.user_set.all()
    else:
        ev_d = None
        all_ev_d = None
    return {"all_ev_d": all_ev_d, "ev_d": ev_d}

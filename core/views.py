from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from c2.models import C2Facility


@login_required(login_url='omsLogin')
def defaultPage(request):
    context = {}
    return render(request, 'core/default_page.html', context)


@login_required(login_url='omsLogin')
def group_based_redirect(request):
    user = request.user

    # 🔍 Check if the session stored a last visited facility before login
    last_facility_id = request.session.get('last_facility_id')

    if last_facility_id:
        return redirect('facility_qr_upload', facility_id=last_facility_id)

    # If no stored facility, check a user group
    if user.groups.filter(name='AM').exists():
        return redirect('amMember')

    if user.groups.filter(name='EMP').exists():
        return redirect('empMember')

    elif user.groups.filter(name='EV').exists():
        if last_facility_id:
            return redirect('facility_qr_upload', facility_id=last_facility_id)  # ✅ Redirect to QR scanned page

        return redirect('evMember')

    else:
        return redirect('defaultPage')


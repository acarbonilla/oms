from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required(login_url='omsLogin')
def defaultPage(request):
    context = {}
    return render(request, 'core/default_page.html', context)


@login_required(login_url='omsLogin')
def group_based_redirect(request):
    user = request.user

    # 🧹 Removed session-based last_facility_id check
    if user.groups.filter(name='EV').exists():
        return redirect('evMember')

    if user.groups.filter(name='AM').exists():
        return redirect('amMember')

    if user.groups.filter(name='EMP').exists():
        return redirect('empMember')

    if user.groups.filter(name='EMP_D').exists():
        return redirect('empMemberDanao')

    if user.groups.filter(name='EV_D').exists():
        return redirect('evMemberDanao')

    if user.groups.filter(name='AM_D').exists():
        return redirect('amMemberDanao')

    return redirect('defaultPage')

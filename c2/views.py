import datetime
import textwrap
# This for time
from datetime import timedelta
# Decorators
from functools import wraps
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Decorator for only allowing eV group
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.core.paginator import Paginator  # ✅ Import Paginator
from django.db.models import Count
from django.db.models import OuterRef, Subquery
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.http import Http404
# This is for QR
from django.urls import reverse
from django.utils.html import strip_tags
# local time
from django.utils.timezone import localtime
# This is for dashboard time
from django.utils.timezone import make_aware, is_naive
from django.utils.timezone import now
from reportlab.lib import colors
# pdf
from reportlab.lib.pagesizes import letter, A4, LEGAL, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from c2.forms import C2RecentImageForm, C2RecentImageFormUpdate, TechnicalActivitiesForm
# from c2.filters import FacilityFilter
from c2.models import C2Standard, C2User, C2Facility, C2TechActivities, C2TechActivityImage
from .models import C2RecentImage  # Ensure correct model import
from django.http import JsonResponse  # Adding this for main form concern

# This is for Technical Activities
import base64
from django.core.files.base import ContentFile
import json


# Decorators to prohibits the other app access
def restrict_for_c2group_only(allowed_groups=None, redirect_url="access_denied/"):
    """
    This decorator restricts access to views to only users in the specified list of allowed groups.
    If the user is not in one of the allowed groups, they will be redirected to the access_denied page.

    :param allowed_groups: List of group names (strings) that are allowed to access the view.
    :param redirect_url: URL to redirect to if the user is not in the allowed groups (default is 'access_denied/').
    """
    if allowed_groups is None:
        allowed_groups = []

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Check if the user is in one of the allowed groups
            if not any(request.user.groups.filter(name=group).exists() for group in allowed_groups):
                # If user is not in allowed groups, show a message and redirect
                messages.warning(request, "🚫 You are not authorized to access this page.")
                return redirect(access_denied)
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


# This decorator prohibits the EMP group to access the page

def restrict_emp_group(redirect_url="access_denied/"):  # Redirect to "access_denied"
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.groups.filter(name="EMP").exists():
                messages.warning(request, "🚫 You are not authorized to access this page.")
                return redirect(redirect_url)
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def access_denied(request):
    return render(request, "forbidden/access_denied.html")


# This is for only user belong to EV group can access the upload_recent_image_qr
def ev_group_required(user):
    return user.groups.filter(name="EV").exists()


@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@restrict_emp_group(redirect_url="access_denied")  # Redirect EMP users to home page
@login_required(login_url='omsLogin')
def evMember(request):
    # Get current time in Philippine Time
    ph_time_now = localtime(now())

    # Get the start of this week (Monday)
    start_of_week = ph_time_now - timedelta(days=ph_time_now.weekday())

    # Get the start of this month
    start_of_month = ph_time_now.replace(day=1)

    # Get the start of this year
    start_of_year = ph_time_now.replace(month=1, day=1)

    # ✅ Count form entries for this week, month, and year
    weekly_count = C2RecentImage.objects.filter(created__gte=start_of_week).count()
    monthly_count = C2RecentImage.objects.filter(created__gte=start_of_month).count()
    yearly_count = C2RecentImage.objects.filter(created__gte=start_of_year).count()

    # ✅ Get Passed Facilities within this month
    search_query = request.GET.get("search", "")

    passed_facilities = C2RecentImage.objects.filter(
        status="Pass",
        created__gte=start_of_month
    ).values("id", "s_image__facility__name", "created").distinct()

    # ✅ Apply search filter
    if search_query:
        passed_facilities = passed_facilities.filter(s_image__facility__name__icontains=search_query)

    # ✅ Pagination (10 per page)
    paginator = Paginator(passed_facilities, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "failed_sites_count": C2RecentImage.objects.filter(
            status="Failed",
            created__gte=ph_time_now - timedelta(days=30)
        ).count(),
        "total_facilities": C2Facility.objects.count(),
        "passed_facilities_count": passed_facilities.count(),
        "page_obj": page_obj,
        "search_query": search_query,

        # ✅ New Data for Weekly, Monthly, Yearly Form Counts
        "weekly_count": weekly_count,
        "monthly_count": monthly_count,
        "yearly_count": yearly_count,
        "title": "Evaluator Dashboard",
    }
    return render(request, 'c2/ev/ev_dashboard.html', context)


@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@login_required(login_url='omsLogin')
def empMember(request):
    facilities = C2Facility.objects.all()  # ✅ Fetch all facilities
    name = User.objects.all()
    context = {'name': name, 'facilities': facilities, 'title': 'Employee',
               'user_name': request.user.first_name or request.user.username}
    return render(request, 'c2/emp/emp_list.html', context)


@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@login_required(login_url='omsLogin')
def amMember(request):
    # Get all users
    name = User.objects.all()

    # Get the current time with timezone awareness
    today = datetime.datetime.now().astimezone()

    # Start of the week (Monday)
    week_start = today.replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=today.weekday())

    # Start of the month
    month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Start of the year
    year_start = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    # Ensure they are timezone-aware
    if is_naive(week_start):
        week_start = make_aware(week_start)

    if is_naive(month_start):
        month_start = make_aware(month_start)

    if is_naive(year_start):
        year_start = make_aware(year_start)

    # Now you can use them in queries
    weekly_general_activities = C2RecentImage.objects.filter(created__gte=week_start).count()
    monthly_general_activities = C2RecentImage.objects.filter(created__gte=month_start).count()
    yearly_general_activities = C2RecentImage.objects.filter(created__gte=year_start).count()

    # Facility Statistics
    facility_reg_count = C2Facility.objects.count()
    # ✅ Get all facilities that WERE visited within the last month
    facility_visited_week = C2RecentImage.objects.filter(
        created__gte=week_start).values_list("s_image__facility__id", flat=True).distinct().count()
    facility_not_visited_week = facility_reg_count - facility_visited_week

    # Status Breakdown
    passed_count = C2RecentImage.objects.filter(status="Pass").count()
    failed_count = C2RecentImage.objects.filter(status="Failed").count()
    pending_count = C2RecentImage.objects.filter(status="Pending").count()

    # Technical Activities (C2TechActivities) Counts
    weekly_tech_activities = C2TechActivities.objects.filter(created__gte=week_start).count()
    print(f"Weekly: {weekly_tech_activities}")
    monthly_tech_activities = C2TechActivities.objects.filter(created__gte=month_start).count()
    yearly_tech_activities = C2TechActivities.objects.filter(created__gte=year_start).count()

    context = {
        'name': name,
        'weekly_general_activities': weekly_general_activities,
        'monthly_general_activities': monthly_general_activities,
        'yearly_general_activities': yearly_general_activities,
        'facility_reg_count': facility_reg_count,
        'facility_visited_week': facility_visited_week,
        'facility_not_visited_week': facility_not_visited_week,
        'passed_count': passed_count,
        'failed_count': failed_count,
        'pending_count': pending_count,
        'weekly_tech_activities': weekly_tech_activities,
        'monthly_tech_activities': monthly_tech_activities,
        'yearly_tech_activities': yearly_tech_activities,
        'title': "Managers' Dashboard",

    }
    return render(request, 'c2/am/am_list.html', context)


@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@restrict_emp_group(redirect_url="access_denied")  # Redirect EMP users to home page
@login_required(login_url='omsLogin')
def amAssessment(request):
    """Show the latest failed recent images per facility with search and pagination."""

    search_query = request.GET.get("search", "")

    latest_recent = C2RecentImage.objects.filter(
        s_image__facility=OuterRef("s_image__facility")
    ).order_by("-updated", "-id").values("id")[:1]

    latest_recent_images = C2RecentImage.objects.filter(
        id=Subquery(latest_recent)
    ).exclude(status="Pass")

    # ✅ Filter by search query (Facility Name)
    if search_query:
        latest_recent_images = latest_recent_images.filter(
            Q(s_image__facility__name__icontains=search_query)
        )

    # ✅ Ensure we correctly count failures per facility
    failed_counts = C2RecentImage.objects.filter(status="Failed").values("s_image__facility").annotate(
        failed_count=Count("id")
    )
    failed_dict = {item["s_image__facility"]: item["failed_count"] for item in failed_counts}

    # ✅ Combine results and add `failed_count`
    combined_data = []
    for recent in latest_recent_images:
        facility_id = recent.s_image.facility.id
        failed_count = failed_dict.get(facility_id, 0)  # ✅ Ensure failed_count is not None

        combined_data.append({
            "id": recent.id,
            "title": recent.title if recent.title else "Untitled",
            "s_image": recent.s_image.facility.name,
            "recent_image": recent.recent_image.url if recent.recent_image else None,
            "standard_image": recent.s_image.standard_image.url if recent.s_image.standard_image else None,
            "failed_count": failed_count,  # ✅ Now guaranteed to be passed correctly

        })

    # ✅ PAGINATION - Show 5 items per page
    paginator = Paginator(combined_data, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "title": "Assessment List",
    }
    return render(request, "c2/assessment.html", context)


@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@user_passes_test(ev_group_required, login_url='omsLogin')  # ✅ Redirect if not in "EV" group
def upload_recent_image_qr(request, facility_id):
    """Handles QR code scanning and redirects users to the upload form."""

    request.session['last_facility_id'] = facility_id
    request.session.modified = True

    facility = get_object_or_404(C2Facility, id=facility_id)

    if request.method == "POST":
        print(f"User in request: {request.user}")  # Check user in production
        form = C2RecentImageForm(request.user, request.POST, request.FILES)
        print(f"User in form: {form.user}")  # Check user passed to form
        if form.is_valid():
            recent_image = form.save(commit=False)

            # ✅ Debugging: Print facility ID and check standard image
            print(f"Facility ID: {facility.id}, Facility Name: {facility.name}")

            standard_image = C2Standard.objects.filter(facility=facility).first()  # ✅ Prevents multiple query failures

            if not standard_image:
                print("Debug: No standard image found for this facility!")  # ✅ Debugging print
                messages.error(request, "No standard image found for this facility.")
                return redirect('facility_qr_upload', facility_id=facility.id)

            print(f"Debug: Standard Image Found - {standard_image.standard_image.url}")  # ✅ Print the found image

            recent_image.s_image = standard_image  # ✅ Assign standard image safely
            recent_image.save()
            messages.success(request, "Recent image uploaded successfully!")

            return redirect(reverse('update_recent_image', kwargs={'pk': recent_image.id}))

        else:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field.capitalize()}: {error}")
            messages.error(request, " | ".join(error_messages))

    else:
        form = C2RecentImageForm(request.user)

    return render(request, 'c2/ev/upload_recent_image_qr.html',
                  {'form': form, 'facility': facility, 'title': "Upload Form"})


# This section is for uploading or updating the recent image.
@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@user_passes_test(ev_group_required, login_url='omsLogin')  # ✅ Redirect if not in "EV" group
def update_recent_image(request, pk):
    """Update an existing C2RecentImage and automatically assign remark_by."""

    recent_image = get_object_or_404(C2RecentImage, pk=pk)

    if request.method == "POST":
        form = C2RecentImageFormUpdate(request.POST, request.FILES, instance=recent_image,
                                       user=request.user)  # ✅ Pass request.user
        if form.is_valid():
            form.save()
            messages.success(request, "Recent image updated successfully!")

            return redirect('assessment')

        else:
            messages.error(request, ", ".join([str(error) for error in form.errors.values()]))

    else:
        form = C2RecentImageFormUpdate(instance=recent_image, user=request.user)  # ✅ Pass request.user

    return render(request, 'c2/ev_update_recent_image.html', {'form': form, 'recent_image': recent_image,
                                                              'title': "Update Form"})


# Details Section
@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@restrict_emp_group(redirect_url="access_denied")  # Redirect EMP users to home page
@login_required(login_url='omsLogin')
def recent_image_detail(request, pk):
    """Displays details of a recent image and shows assigned users of the facility."""

    image = get_object_or_404(C2RecentImage, pk=pk)

    # ✅ Query the assigned user(s) for the facility via `C2Standard`
    assigned_users = C2User.objects.filter(facility=image.s_image.facility)

    return render(request, 'c2/recent_image_detail.html', {
        'image': image,
        'assigned_users': assigned_users,  # ✅ Pass assigned users to template
        "title": "Present Image Details"
    })


# This is for EV Standard Image
# @restrict_emp_group(redirect_url="access_denied")  # Redirect EMP users to home page
@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@login_required(login_url='omsLogin')
def standard_image_ev(request):
    """Displays standard images with search, sorting, and pagination."""

    search_query = request.GET.get('search', '')  # Get search input
    sort_order = request.GET.get('sort', 'asc')  # Get sorting order (default: ascending)

    s_image_standard = C2Standard.objects.all()

    # ✅ Search filter
    if search_query:
        s_image_standard = s_image_standard.filter(
            Q(facility__name__icontains=search_query)
        )

    # ✅ Sorting by Facility Name
    if sort_order == 'desc':
        s_image_standard = s_image_standard.order_by('-facility__name')  # Descending
    else:
        s_image_standard = s_image_standard.order_by('facility__name')  # Ascending (default)

    # ✅ Pagination setup (10 images per page)
    paginator = Paginator(s_image_standard, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        's_standard': page_obj,  # Paginated results
        'search_query': search_query,  # Pass search input for template reuse
        'sort_order': sort_order,  # Pass sorting order
        'title': "Standard Image"
    }

    return render(request, 'c2/ev/s_image_standard.html', context)


# @restrict_emp_group(redirect_url="access_denied")  # Redirect EMP users to home page
@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@login_required(login_url='omsLogin')
def standard_image_ev_details(request, pk):
    """View details of a specific standard image and show the assigned user."""

    s_image = get_object_or_404(C2Standard, pk=pk)  # Get the standard image
    assigned_users = C2User.objects.filter(facility=s_image.facility)  # ✅ Query assigned users

    context = {
        "s_image": s_image,
        "assigned_users": assigned_users,  # ✅ Pass users to template
        "title": f"Standard Image - {s_image.facility.name}"
    }
    return render(request, "c2/ev/standard_image_details.html", context)


# This is for everyone
# @restrict_emp_group(redirect_url="access_denied")  # Redirect EMP users to home page
@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@login_required(login_url='omsLogin')
def failed_list(request):
    """Show up to 3 'Failed' images within 30 days & keep a yearly history, with search and pagination."""

    thirty_days_ago = now() - timedelta(days=30)  # ✅ 30 days filter
    one_year_ago = now() - timedelta(days=365)  # ✅ 1 year filter

    search_query = request.GET.get('search', '')  # ✅ Get search input
    facilities = C2Facility.objects.all()

    if search_query:
        facilities = facilities.filter(name__icontains=search_query)  # ✅ Filter by facility name

    failed_facilities = []  # ✅ Stores facilities with failed images

    for facility in facilities:
        recent_failed_images = C2RecentImage.objects.filter(
            s_image__facility=facility,
            status="Failed",
            created__gte=thirty_days_ago
        ).order_by('-created')[:3]

        yearly_failed_images = C2RecentImage.objects.filter(
            s_image__facility=facility,
            status="Failed",
            created__gte=one_year_ago,
            created__lt=thirty_days_ago
        ).order_by('-created')

        if recent_failed_images.exists() or yearly_failed_images.exists():
            failed_facilities.append({
                "facility": facility,
                "recent_failed_images": recent_failed_images,
                "yearly_failed_images": yearly_failed_images,
                "failed_count": recent_failed_images.count() + yearly_failed_images.count(),
            })

    # ✅ PAGINATION - Show 5 facilities per page
    paginator = Paginator(failed_facilities, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj, 'search_query': search_query,
               'title': f"Failed List "}
    return render(request, 'c2/failed_list.html', context)


@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@restrict_emp_group(redirect_url="access_denied")  # Redirect EMP users to home page
@login_required(login_url='omsLogin')
def generate_pdf(request):
    """Generate and download a PDF report of C2RecentImage entries within the current year."""

    # ✅ Get search query (if provided)
    search_query = request.GET.get("search", "")
    current_year = now().year

    # ✅ Filter images within the current year
    images = C2RecentImage.objects.filter(created__year=current_year)

    # ✅ Apply search filter (by facility name or title)
    if search_query:
        images = images.filter(Q(title__icontains=search_query) | Q(s_image__facility__name__icontains=search_query))

    # ✅ Paginate results (10 per page)
    paginator = Paginator(images, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # ✅ Generate PDF
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y_position = height - 50  # Start position

    def add_watermark(pdf, width, height):
        try:
            watermark_path = finders.find("report_logo/fm_logo.png")
            if watermark_path:
                pdf.saveState()
                pdf.setFillAlpha(0.15)  # Slightly more visible transparency
                # Center-center positioning: calculate center coordinates
                logo_width, logo_height = 500, 300  # Bigger watermark size
                center_x = (width - logo_width) / 2
                center_y = (height - logo_height) / 2
                pdf.drawImage(ImageReader(watermark_path), center_x, center_y, width=logo_width, height=logo_height, mask='auto')
                pdf.restoreState()
        except Exception as e:
            print(f"Error adding watermark: {e}")

    # Add watermark to first page
    add_watermark(pdf, width, height)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, y_position, "C2 Recent Image Report - " + str(current_year))
    y_position -= 40

    pdf.setFont("Helvetica", 12)

    for img in page_obj:
        pdf.drawString(50, y_position, f"Title: {img.title}")
        pdf.drawString(50, y_position - 20, f"Facility: {img.s_image.facility.name}")
        pdf.drawString(50, y_position - 40, f"Status: {img.status}")
        pdf.drawString(50, y_position - 60, f"Uploaded By: {img.uploaded_by}")
        y_position -= 100  # Move down

        if y_position < 100:  # Prevent overflow
            pdf.showPage()
            add_watermark(pdf, width, height)  # Add watermark to new page
            y_position = height - 50
            pdf.setFont("Helvetica", 12)

    pdf.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="C2RecentImage_Report.pdf"'
    return response


@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@restrict_emp_group(redirect_url="access_denied")  # Redirect EMP users to home page
@login_required(login_url='omsLogin')
def generate_selected_pdf(request):
    """Generate a landscape PDF report with watermark, images, and details."""
    selected_ids = request.GET.getlist("selected_ids", [])
    search_query = request.GET.get("search", "")
    current_year = now().year
    images = C2RecentImage.objects.filter(created__year=current_year).exclude(status="Pending")

    if search_query:
        images = images.filter(Q(title__icontains=search_query) | Q(s_image__facility__name__icontains=search_query)
                               | Q(status__icontains=search_query)
                               | Q(uploaded_by__name__first_name__icontains=search_query)
                               | Q(id__icontains=search_query)
                               )

    if not images.exists():
        return render(request, "c2/report_selection.html", {
            "error_message": "❌ No available records to download (Pending records are excluded).",
            "search_query": search_query
        })

    if not selected_ids:
        return render(request, "c2/report_selection.html", {
            "error_message": "❌ Please select at least one item before downloading.",
            "search_query": search_query,
            "page_obj": images
        })

    images = images.filter(id__in=selected_ids)
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    def add_watermark(pdf, width, height):
        try:
            watermark_path = finders.find("report_logo/fm_logo.png")
            if watermark_path:
                pdf.saveState()
                pdf.setFillAlpha(0.15)  # Slightly more visible transparency
                # Center-center positioning: calculate center coordinates
                logo_width, logo_height = 500, 300  # Bigger watermark size
                center_x = (width - logo_width) / 2
                center_y = (height - logo_height) / 2
                pdf.drawImage(ImageReader(watermark_path), center_x, center_y, width=logo_width, height=logo_height, mask='auto')
                pdf.restoreState()
        except Exception as e:
            print(f"Error adding watermark: {e}")

    for index, img in enumerate(images):  # Added index to track the first page
        if index > 0:  # Only add a new page after the first iteration
            pdf.showPage()  # ✅ Now it correctly starts a new page for each report

        # add_watermark(pdf, width, height)  # Add watermark
        add_watermark(pdf, width, height)  # Add watermark
        # Border
        pdf.setStrokeColor(colors.black)
        pdf.setLineWidth(2)
        pdf.rect(20, 20, width - 40, height - 40)

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(250, height - 50, "Facility Management Inspection Report")
        pdf.setFont("Helvetica", 12)

        col1_x, col2_x, col3_x = 50, 300, 550
        img_width, img_height = 200, 150
        y_position = height - 100

        # Column 1: Information
        pdf.drawString(col1_x, y_position, f"ID: {img.id}")
        pdf.drawString(col1_x, y_position - 20, f"Title: {img.title}")
        pdf.drawString(col1_x, y_position - 40, f"Facility: {img.s_image.facility.name}")
        pdf.drawString(col1_x, y_position - 60, f"Status: {img.status}")

        y_position -= 80
        pdf.drawString(col1_x, y_position - 10, f"Re-Schedule: {img.re_schedule if img.re_schedule else 'N/A'}")
        pdf.drawString(
            col1_x, y_position - 30,
            f"Evaluated By: {img.remark_by.first_name} {img.remark_by.last_name}" if img.remark_by else "Evaluated "
                                                                                                        "By: N/A"
        )

        pdf.drawString(col1_x, y_position - 50,
                       f"Updated: {localtime(img.updated).strftime('%Y-%m-%d %H:%M:%S') if img.updated else 'N/A'}")
        pdf.drawString(col1_x, y_position - 70,
                       f"Created: {localtime(img.created).strftime('%Y-%m-%d %H:%M:%S') if img.created else 'N/A'}")
        y_position -= 90

        # Column 2: Standard Image
        if img.s_image and img.s_image.standard_image:
            try:
                pdf.drawString(col2_x, y_position, "Standard Image")
                pdf.drawImage(ImageReader(img.s_image.standard_image.path), col2_x, height - 230, width=img_width,
                              height=img_height)
            except Exception as e:
                print(f"Error loading standard image: {e}")

        # Column 3: Latest Image
        if img.recent_image:
            try:
                pdf.drawString(col3_x, y_position, "Latest Image")
                pdf.drawImage(ImageReader(img.recent_image.path), col3_x, height - 230, width=img_width,
                              height=img_height)
            except Exception as e:
                print(f"Error loading latest image: {e}")

        # Remove HTML tags and prepare remarks text
        remarks_text = strip_tags(img.remarks) if img.remarks else 'N/A'

        # Wrap text for proper formatting in PDF
        wrapped_remarks = textwrap.wrap(" ".join(remarks_text.split()[:150]), width=120)

        pdf.drawString(col1_x, y_position, "Remarks:")

        # Indented text
        y_position -= 50
        indentation = 20  # Adjust this value for indentation

        for line in wrapped_remarks:
            pdf.drawString(col1_x + indentation, y_position, line)  # Apply indentation
            y_position -= 25  # Line spacing

        # End of Report
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(280, y_position - 20, "-----End of Report-----")

        try:
            logo2_path = finders.find("report_logo/zfc-logo.png")

            if logo2_path:
                pdf.drawImage(ImageReader(logo2_path), 30, height - 75, width=100, height=50)
        except Exception as e:
            print(f"Error loading logos: {e}")

    pdf.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Facility Mgt Inspection Report.pdf"'
    return response


# This is for Pass List
@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@login_required(login_url='omsLogin')
def pass_list(request):
    """View to list all 'Pass' statuses within 30 days and 1 year, sorted by date, with search & pagination."""

    # ✅ Get current time
    ph_time_now = localtime(now())

    # ✅ Get 30 days ago and 1 year ago
    thirty_days_ago = ph_time_now - timedelta(days=30)
    one_year_ago = ph_time_now - timedelta(days=365)

    # ✅ Get search query from request
    search_query = request.GET.get("search", "")

    # ✅ Query for records marked as "Pass"
    recent_passes = C2RecentImage.objects.filter(
        status="Pass",
        created__gte=thirty_days_ago  # ✅ Passed within the last 30 days
    ).order_by("-created")

    old_passes = C2RecentImage.objects.filter(
        status="Pass",
        created__gte=one_year_ago,
        created__lt=thirty_days_ago  # ✅ Passed after 30 days but within a year
    ).order_by("-created")

    # ✅ Apply search filter
    if search_query:
        recent_passes = recent_passes.filter(
            Q(title__icontains=search_query) |
            Q(s_image__facility__name__icontains=search_query)
        )
        old_passes = old_passes.filter(
            Q(title__icontains=search_query) |
            Q(s_image__facility__name__icontains=search_query)
        )

    # ✅ Pagination (10 per page)
    paginator_recent = Paginator(recent_passes, 10)
    paginator_old = Paginator(old_passes, 10)
    page_number_recent = request.GET.get("recent_page")
    page_number_old = request.GET.get("old_page")
    recent_page_obj = paginator_recent.get_page(page_number_recent)
    old_page_obj = paginator_old.get_page(page_number_old)

    context = {
        "recent_page_obj": recent_page_obj,  # ✅ Recent passes within 30 days
        "old_page_obj": old_page_obj,  # ✅ Older passes within 1 year
        "search_query": search_query,  # ✅ Preserve search input
        "title": "Passed List",
    }
    return render(request, 'c2/pass_list.html', context)


@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@restrict_emp_group(redirect_url="access_denied")  # Redirect EMP users to home page
@login_required(login_url='omsLogin')
def not_visited_facilities_list(request):
    """View to list facilities that have NOT been visited within the last month."""

    # ✅ Get current time in Philippine Time
    ph_time_now = localtime(now())

    # ✅ Get the start of the current month
    one_month_ago = ph_time_now - timedelta(days=30)

    # ✅ Get search query from request
    search_query = request.GET.get("search", "")

    # ✅ Get all facilities that WERE visited within the last month
    visited_facilities = C2RecentImage.objects.filter(
        created__gte=one_month_ago
    ).values_list("s_image__facility__id", flat=True).distinct()

    # ✅ Get facilities that were NOT visited within the last month
    not_visited_facilities = C2Facility.objects.exclude(id__in=visited_facilities).order_by("name")

    # ✅ Apply search filter
    if search_query:
        not_visited_facilities = not_visited_facilities.filter(
            Q(name__icontains=search_query)
        )

    # ✅ Pagination (10 per page)
    paginator = Paginator(not_visited_facilities, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,  # ✅ List of facilities not visited
        "search_query": search_query,  # ✅ Preserve search input
        "title": "Not Visited List",
    }
    return render(request, 'c2/ev/not_visited_facilities_list.html', context)


# This is for Technical Activities
@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@login_required(login_url='omsLogin')
def tech_act_upload(request, pk=None):
    tech = get_object_or_404(C2TechActivities, id=pk) if pk else None
    MAX_IMAGE_SIZE = 15 * 1024 * 1024  # 15MB
    MAX_IMAGES = 20
    ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
    MIN_IMAGE_SIZE = 10 * 1024  # 10KB

    if request.method == "POST":
        form = TechnicalActivitiesForm(request.POST, instance=tech)

        try:
            if form.is_valid():
                tech_activity = form.save(commit=False)
                
                # Decode HTML entities in remarks before saving
                if tech_activity.remarks:
                    import html
                    
                    # Decode all HTML entities
                    decoded_remarks = html.unescape(tech_activity.remarks)
                    
                    # Update the remarks with decoded text
                    tech_activity.remarks = decoded_remarks
                
                tech_activity.uploaded_by = C2User.objects.get(name__id=request.user.id)
                tech_activity.save()

                uploaded_images = 0
                errors = []
                warnings = []

                # Handle uploaded image files
                files = request.FILES.getlist('image')
                if len(files) > MAX_IMAGES:
                    messages.error(request, f'Maximum {MAX_IMAGES} images allowed')
                    
                    # Check if this is an AJAX request
                    if request.headers.get('Accept') == 'application/json':
                        return JsonResponse({
                            'success': False,
                            'error': f'Maximum {MAX_IMAGES} images allowed'
                        }, status=400)
                    
                    return redirect('tech_act_upload')

                for file in files:
                    try:
                        # Validate file size
                        if file.size > MAX_IMAGE_SIZE:
                            errors.append(f'File {file.name} exceeds 5MB limit')
                            continue

                        if file.size < MIN_IMAGE_SIZE:
                            errors.append(f'File {file.name} is too small (minimum 10KB)')
                            continue

                        # Validate file type
                        if not file.content_type.startswith('image/'):
                            errors.append(f'File {file.name} is not an image')
                            continue

                        # Additional MIME type validation
                        if file.content_type not in ALLOWED_MIME_TYPES:
                            errors.append(
                                f'File {file.name} format not supported. Allowed formats: JPEG, PNG, GIF, WebP')
                            continue

                        # Validate image integrity
                        try:
                            from PIL import Image
                            img = Image.open(file)
                            img.verify()  # Verify image integrity

                            # Check minimum dimensions
                            if img.width < 100 or img.height < 100:
                                errors.append(f'File {file.name} dimensions too small (minimum 100x100)')
                                continue

                            # Check maximum dimensions
                            if img.width > 4096 or img.height > 4096:
                                errors.append(f'File {file.name} dimensions too large (maximum 4096x4096)')
                                continue

                            # Check aspect ratio (4:3) - More flexible validation
                            aspect_ratio = img.width / img.height
                            target_ratio = 4/3
                            tolerance = 0.5  # Allow 50% deviation from perfect 4:3 ratio (more flexible)
                            
                            # Only warn for extremely wide or tall images
                            if aspect_ratio < 0.5 or aspect_ratio > 3.0:
                                warnings.append(f'File {file.name} has extreme aspect ratio (current ratio: {aspect_ratio:.2f}). Please use a more standard image format.')
                                continue

                        except Exception as e:
                            errors.append(f'File {file.name} appears to be corrupted')
                            continue

                        C2TechActivityImage.objects.create(activity=tech_activity, image=file)
                        uploaded_images += 1
                    except Exception as e:
                        errors.append(f'Error uploading {file.name}: {str(e)}')

                # Handle captured images (Base64 format)
                captured_images = request.POST.get('captured_images')
                if captured_images:
                    try:
                        images = json.loads(captured_images)
                        if len(images) + uploaded_images > MAX_IMAGES:
                            messages.error(request, f'Total images exceed maximum limit of {MAX_IMAGES}')
                            tech_activity.delete()
                            return redirect('tech_act_upload')

                        for idx, img_data in enumerate(images):
                            try:
                                # Validate base64 image
                                if not img_data.startswith('data:image/'):
                                    errors.append(f'Invalid image format for captured image {idx + 1}')
                                    continue

                                format, imgstr = img_data.split(';base64,')
                                ext = format.split('/')[-1]

                                # Validate image format
                                if not f'image/{ext}' in ALLOWED_MIME_TYPES:
                                    errors.append(f'Captured image {idx + 1} format not supported')
                                    continue

                                # Decode and validate size
                                decoded_image = base64.b64decode(imgstr)
                                if len(decoded_image) > MAX_IMAGE_SIZE:
                                    errors.append(f'Captured image {idx + 1} exceeds 5MB limit')
                                    continue

                                if len(decoded_image) < MIN_IMAGE_SIZE:
                                    errors.append(f'Captured image {idx + 1} is too small (minimum 10KB)')
                                    continue

                                # Validate image integrity
                                try:
                                    from PIL import Image
                                    import io
                                    img = Image.open(io.BytesIO(decoded_image))
                                    img.verify()  # Verify image integrity

                                    # Check minimum dimensions
                                    if img.width < 100 or img.height < 100:
                                        errors.append(
                                            f'Captured image {idx + 1} dimensions too small (minimum 100x100)')
                                        continue

                                    # Check maximum dimensions
                                    if img.width > 4096 or img.height > 4096:
                                        errors.append(
                                            f'Captured image {idx + 1} dimensions too large (maximum 4096x4096)')
                                        continue

                                    # Check aspect ratio (4:3) - More flexible validation
                                    aspect_ratio = img.width / img.height
                                    target_ratio = 4/3
                                    tolerance = 0.5  # Allow 50% deviation from perfect 4:3 ratio (more flexible)
                                    
                                    # Only warn for extremely wide or tall images
                                    if aspect_ratio < 0.5 or aspect_ratio > 3.0:
                                        warnings.append(f'Captured image {idx + 1} has extreme aspect ratio (current ratio: {aspect_ratio:.2f}). Please use a more standard image format.')
                                        continue

                                except Exception as e:
                                    errors.append(f'Captured image {idx + 1} appears to be corrupted')
                                    continue

                                file_data = ContentFile(decoded_image, name=f"captured_{tech_activity.id}_{idx}.{ext}")
                                C2TechActivityImage.objects.create(activity=tech_activity, image=file_data)
                                uploaded_images += 1
                            except Exception as e:
                                errors.append(f'Error processing captured image {idx + 1}: {str(e)}')

                    except json.JSONDecodeError:
                        errors.append('Invalid captured images data')

                if uploaded_images == 0:
                    tech_activity.delete()
                    messages.error(request, 'No valid images were uploaded')
                    if errors:
                        for error in errors:
                            messages.warning(request, error)
                    
                    # Check if this is an AJAX request
                    if request.headers.get('Accept') == 'application/json':
                        return JsonResponse({
                            'success': False,
                            'error': 'No valid images were uploaded',
                            'errors': errors
                        }, status=400)
                    
                    return redirect('tech_act_upload')

                messages.success(request, f'Successfully uploaded {uploaded_images} images')
                if errors:
                    for error in errors:
                        messages.warning(request, error)

                # Check if this is an AJAX request
                if request.headers.get('Accept') == 'application/json':
                    response_data = {
                        'success': True,
                        'message': f'Successfully uploaded {uploaded_images} images',
                        'redirect_url': '/c2/activities/',
                        'uploaded_count': uploaded_images
                    }
                    
                    # Include warnings in the response if any
                    if warnings:
                        response_data['warnings'] = warnings
                    
                    return JsonResponse(response_data)
                
                return redirect('activity_list')
            else:
                for field, error_list in form.errors.items():
                    for error in error_list:
                        messages.error(request, f'{field}: {error}')
                return redirect('tech_act_upload')

        except C2User.DoesNotExist:
            messages.error(request, 'User not found')
            return redirect('tech_act_upload')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('tech_act_upload')
    else:
        form = TechnicalActivitiesForm(instance=tech)

    return render(request, "c2/tech_act_upload.html", {
        "activity_form": form,
        "title": "Tech-Activity Form",
        "max_images": MAX_IMAGES,
        "max_image_size": MAX_IMAGE_SIZE
    })


# This is for tech view list
@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@login_required(login_url='omsLogin')
def activity_list(request):
    """View for listing activities with search, filter, and pagination."""

    search_query = request.GET.get("search", "")
    filter_option = request.GET.get("filter", "all")
    page_number = request.GET.get("page", 1)

    today = now()

    # Determine filter date range
    if filter_option == "week":
        start_date = today - timedelta(days=7)
    elif filter_option == "month":
        start_date = today - timedelta(days=30)
    elif filter_option == "year":
        start_date = today - timedelta(days=365)
    else:
        start_date = None  # Show all records

    # Apply filters
    activities = C2TechActivities.objects.all().prefetch_related("images")
    if start_date:
        activities = activities.filter(created__gte=start_date)
    if search_query:
        activities = activities.filter(name__icontains=search_query)  # Search by activity name

    # Add pagination
    paginator = Paginator(activities, 10)  # Show 5 activities per page
    activities_page = paginator.get_page(page_number)

    return render(
        request,
        "c2/activity_list.html",
        {
            "activities": activities_page,
            "filter_option": filter_option,
            "search_query": search_query,
            "title": "Tech-Activity List"
        }
    )


@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@login_required(login_url='omsLogin')
def activity_detail(request, activity_id):
    """View to show details of a specific activity with images."""
    activity = get_object_or_404(C2TechActivities, id=activity_id)
    return render(request, "c2/activity_detail.html",
                  {"activity": activity, "title": f" Activity-Details: {activity.name}"})


# This is for downloading the QR code from facility
@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
def generate_qr_code(request, facility_id):
    # Get the facility by ID
    facility = get_object_or_404(C2Facility, id=facility_id)

    # Return the QR code image as a downloadable response
    with open(facility.qr_code.path, 'rb') as qr_file:
        response = HttpResponse(qr_file.read(), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename={facility.qr_code.name.split("/")[-1]}'
        return response


@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
def facility_list(request):
    # Get the search query from the request
    query = request.GET.get('search', '')

    # Filter facilities by name if a search query is provided
    facilities = C2Facility.objects.filter(name__icontains=query)

    # Pagination
    paginator = Paginator(facilities, 5)  # Show 5 facilities per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'c2/facility_list.html', {
        'page_obj': page_obj,
        'query': query
    })


@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@login_required(login_url='omsLogin')
def tech_activity_download(request):
    """View for selecting technical activities to download as PDF."""
    search_query = request.GET.get("search", "")
    filter_option = request.GET.get("filter", "all")
    page_number = request.GET.get("page", 1)
    page_size = int(request.GET.get("page_size", 10))  # Default to 10 items per page

    today = now()

    # Determine filter date range
    if filter_option == "week":
        start_date = today - timedelta(days=7)
    elif filter_option == "month":
        start_date = today - timedelta(days=30)
    elif filter_option == "year":
        start_date = today - timedelta(days=365)
    else:
        start_date = None

    # Apply filters
    activities = C2TechActivities.objects.all().prefetch_related("images").order_by('-created')
    if start_date:
        activities = activities.filter(created__gte=start_date)
    if search_query:
        activities = activities.filter(name__icontains=search_query)

    # Add pagination with dynamic page size
    paginator = Paginator(activities, page_size)
    activities_page = paginator.get_page(page_number)

    # Calculate visible page range (show 5 pages around current page)
    page_range = []
    current_page = activities_page.number
    total_pages = paginator.num_pages

    # Always show first page
    if current_page > 3:
        page_range.append(1)
        if current_page > 4:
            page_range.append(None)  # Represents ellipsis

    # Show pages around current page
    for i in range(max(1, current_page - 2), min(total_pages + 1, current_page + 3)):
        page_range.append(i)

    # Always show last page
    if current_page < total_pages - 2:
        if current_page < total_pages - 3:
            page_range.append(None)  # Represents ellipsis
        page_range.append(total_pages)

    context = {
        "activities": activities_page,
        "filter_option": filter_option,
        "search_query": search_query,
        "page_size": page_size,
        "page_range": page_range,
        "title": "Download Technical Activities"
    }

    return render(request, "c2/tech_activity_download.html", context)


@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@login_required(login_url='omsLogin')
def tech_activity_pdf(request):
    """Generate PDF for selected technical activities."""
    selected_ids = request.GET.getlist("selected_ids", [])
    download_all = request.GET.get("download_all") == "true"
    include_images = request.GET.get("include_images") == "on"
    include_details = request.GET.get("include_details") == "on"
    page_size = request.GET.get("page_size", "letter")
    orientation = request.GET.get("orientation", "landscape")
    search_query = request.GET.get("search", "")
    filter_option = request.GET.get("filter", "all")

    # Get activities based on filters
    activities = C2TechActivities.objects.all().prefetch_related("images")

    if not download_all:
        if not selected_ids:
            messages.error(request, "Please select at least one activity to download.")
            return redirect('tech_activity_download')
        activities = activities.filter(id__in=selected_ids)

    # Apply search and time filters
    if search_query:
        activities = activities.filter(name__icontains=search_query)

    today = now()
    if filter_option == "week":
        activities = activities.filter(created__gte=today - timedelta(days=7))
    elif filter_option == "month":
        activities = activities.filter(created__gte=today - timedelta(days=30))
    elif filter_option == "year":
        activities = activities.filter(created__gte=today - timedelta(days=365))

    if not activities.exists():
        messages.error(request, "No activities found matching your criteria.")
        return redirect('tech_activity_download')

    # Create PDF
    buffer = BytesIO()

    # Set up the PDF with proper page size
    if page_size == "a4":
        page_size_tuple = A4
    elif page_size == "legal":
        page_size_tuple = LEGAL
    else:  # default to letter
        page_size_tuple = letter

    if orientation == "landscape":
        page_size_tuple = landscape(page_size_tuple)

    pdf = canvas.Canvas(buffer, pagesize=page_size_tuple)
    width, height = page_size_tuple

    # Define watermark function
    def add_watermark(pdf, width, height):
        try:
            watermark_path = finders.find("report_logo/fm_logo.png")
            if watermark_path:
                pdf.saveState()
                pdf.setFillAlpha(0.15)  # Slightly more visible transparency
                # Center-center positioning: calculate center coordinates
                logo_width, logo_height = 500, 300  # Bigger watermark size
                center_x = (width - logo_width) / 2
                center_y = (height - logo_height) / 2
                pdf.drawImage(ImageReader(watermark_path), center_x, center_y, width=logo_width, height=logo_height, mask='auto')
                pdf.restoreState()
        except Exception as e:
            print(f"Error adding watermark: {e}")

    # Define colors and styles
    colors_dict = {
        'primary': colors.HexColor('#4f46e5'),  # Indigo
        'secondary': colors.HexColor('#6b7280'),  # Gray
        'success': colors.HexColor('#10b981'),  # Green
        'light': colors.HexColor('#f3f4f6'),  # Light Gray
        'dark': colors.HexColor('#1f2937'),  # Dark Gray
        'border': colors.HexColor('#e5e7eb'),  # Border Gray
    }

    def add_page_header(page_num, activity=None):
        """Add styled header to each page matching the Danao design"""
        # Add watermark to every page
        add_watermark(pdf, width, height)
        
        # Header background
        header_height = 100
        pdf.setFillColor(colors.white)
        pdf.rect(0, height - header_height, width, header_height, fill=True)
        
        # Left section - Main Title
        title_x = 70
        title_y = height - 40
        pdf.setFillColor(colors.black)
        pdf.setFont("Helvetica-Bold", 30)
        
        # Title with line breaks to match Danao design
        pdf.drawString(title_x, title_y, "Facilities Inspection &")
        pdf.drawString(title_x, title_y - 26, "Maintenance Report")
        
        # Activity name under the title
        if activity and hasattr(activity, 'name') and activity.name:
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(title_x, title_y - 45, activity.name)
        
        # Right section - Document Metadata Table (4 rows with borders)
        table_width = 400
        table_x = width - 450  # Right-aligned, positioned to align with title
        table_y = height - 8
        table_height = 80  # Height for 4 rows
        
        # Table border
        pdf.setStrokeColor(colors.HexColor('#d1d5db'))
        pdf.setLineWidth(1)
        pdf.rect(table_x, table_y - table_height, table_width, table_height, fill=False)
        
        # Table rows and columns (4 rows as shown in image)
        row_height = table_height / 4
        col_width = table_width / 2
        
        # Draw horizontal lines (3 lines to separate 4 rows)
        for i in range(1, 4):
            y_pos = table_y - (i * row_height)
            pdf.line(table_x, y_pos, table_x + table_width, y_pos)
        
        # Draw vertical line
        pdf.line(table_x + col_width, table_y - table_height, table_x + col_width, table_y)
        
        # Table content
        pdf.setFont("Helvetica", 9)
        pdf.setFillColor(colors.black)
        
        # Document Code (with space as shown in image)
        pdf.drawString(table_x + 5, table_y - 12, "Document Code:")
        pdf.drawString(table_x + col_width + 5, table_y - 12, "FM-MP-VM- 01.01")
        
        # Revision No.
        pdf.drawString(table_x + 5, table_y - 12 - row_height, "Revision No.:")
        pdf.drawString(table_x + col_width + 5, table_y - 12 - row_height, "0")
        
        # Effectivity Date
        pdf.drawString(table_x + 5, table_y - 12 - (2 * row_height), "Effectivity Date:")
        pdf.drawString(table_x + col_width + 5, table_y - 12 - (2 * row_height), "September 01, 2025")
        
        # Retention Period
        pdf.drawString(table_x + 5, table_y - 12 - (3 * row_height), "Retention Period:")
        pdf.drawString(table_x + col_width + 5, table_y - 12 - (3 * row_height), "5 Years")
        
        # Page number at bottom right
        pdf.setFont("Helvetica", 10)
        pdf.drawRightString(width - 50, height - header_height + 5, f"Page {page_num}")

    def add_footer():
        """Add footer with generated date to each page"""
        from datetime import datetime
        generated_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Footer line
        pdf.setStrokeColor(colors_dict['border'])
        pdf.setLineWidth(0.5)
        pdf.line(50, 50, width - 50, 50)
        
        # Generated date at bottom left
        pdf.setFont("Helvetica", 8)
        pdf.setFillColor(colors_dict['secondary'])
        pdf.drawString(60, 30, f"Generated: {generated_date}")

    def add_activity_header(y_position, activity):
        """Add styled activity header"""
        # Background rectangle for activity header - Moved down by adjusting y_position
        pdf.setFillColor(colors_dict['light'])
        pdf.rect(50, y_position - 10, width - 100, 30, fill=True)
        
        # Activity name - Adjusted position
        pdf.setFillColor(colors_dict['dark'])
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(60, y_position + 2, f"Activity: {activity.name}")
        
        return y_position - 40  # Increased spacing after header

    def add_metadata_section(y_position, activity):
        """Add metadata section with icons and styled layout"""
        pdf.setFont("Helvetica", 10)
        pdf.setFillColor(colors_dict['secondary'])
        
        # Activity name
        pdf.drawString(60, y_position, "📋 Activity:")
        pdf.setFillColor(colors_dict['dark'])
        pdf.drawString(140, y_position, activity.name)
        
        # Location
        y_position -= 20
        pdf.setFillColor(colors_dict['secondary'])
        pdf.drawString(60, y_position, "📍 Location:")
        pdf.setFillColor(colors_dict['dark'])
        pdf.drawString(140, y_position, activity.location)
        
        # Created date
        y_position -= 20
        pdf.setFillColor(colors_dict['secondary'])
        pdf.drawString(60, y_position, "📅 Created:")
        pdf.setFillColor(colors_dict['dark'])
        pdf.drawString(140, y_position, localtime(activity.created).strftime('%Y-%m-%d %H:%M'))
        
        # Updated date
        y_position -= 20
        pdf.setFillColor(colors_dict['secondary'])
        pdf.drawString(60, y_position, "🔄 Updated:")
        pdf.setFillColor(colors_dict['dark'])
        pdf.drawString(140, y_position, localtime(activity.updated).strftime('%Y-%m-%d %H:%M'))
        
        # Uploaded by - with full name
        y_position -= 20
        pdf.setFillColor(colors_dict['secondary'])
        pdf.drawString(60, y_position, "👤 Uploaded by:")
        pdf.setFillColor(colors_dict['dark'])
        if activity.uploaded_by and activity.uploaded_by.name:
            first_name = activity.uploaded_by.name.first_name or ''
            last_name = activity.uploaded_by.name.last_name or ''
            full_name = f"{first_name} {last_name}".strip()
            pdf.drawString(140, y_position, full_name or "N/A")
        else:
            pdf.drawString(140, y_position, "N/A")
        
        # Remarked by - with full name
        if activity.remark_by:
            y_position -= 20
            pdf.setFillColor(colors_dict['secondary'])
            pdf.drawString(60, y_position, "👤 Remarked by:")
            pdf.setFillColor(colors_dict['dark'])
            first_name = activity.remark_by.name.first_name or ''
            last_name = activity.remark_by.name.last_name or ''
            full_name = f"{first_name} {last_name}".strip()
            pdf.drawString(140, y_position, full_name or "N/A")
        
        return y_position - 30

    def add_remarks_section(y_position, activity):
        """Add styled remarks section with preserved formatting"""
        if activity.remarks:
            # Check if we have enough space for remarks header
            if y_position < 150:  # Very low threshold to ensure remarks stays on same page
                pdf.showPage()
                y_position = height - 120
                add_page_header(pdf._pageNumber)
            
            # Remarks header
            pdf.setFillColor(colors_dict['primary'])
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(60, y_position, "Remarks")
            
            # Remarks content
            y_position -= 20
            pdf.setFillColor(colors_dict['dark'])
            pdf.setFont("Helvetica", 10)
            
            # Handle HTML content with preserved formatting
            remarks_text = activity.remarks
            
            # Replace common HTML bullets with PDF-friendly bullets
            remarks_text = remarks_text.replace('<ul>', '').replace('</ul>', '')
            remarks_text = remarks_text.replace('<ol>', '').replace('</ol>', '')
            remarks_text = remarks_text.replace('<li>', '• ').replace('</li>', '')
            
            # Handle arrows and other special characters
            remarks_text = remarks_text.replace('→', '→')
            remarks_text = remarks_text.replace('←', '←')
            remarks_text = remarks_text.replace('↑', '↑')
            remarks_text = remarks_text.replace('↓', '↓')
            remarks_text = remarks_text.replace('⇒', '⇒')
            remarks_text = remarks_text.replace('⇐', '⇐')
            
            # Remove other HTML tags but preserve line breaks
            remarks_text = strip_tags(remarks_text)
            
            # Split into lines and handle indentation
            lines = remarks_text.split('\n')
            current_number = 1  # Counter for numbered lists
            
            for line in lines:
                # Check if we need a new page before adding content
                if y_position < 120:  # Reduced threshold to allow more content on same page
                    pdf.showPage()
                    y_position = height - 120
                    add_page_header(pdf._pageNumber)
                
                # Skip empty lines
                if not line.strip():
                    y_position -= 15
                    continue
                
                # Handle bullet points
                if line.strip().startswith('•'):
                    # Draw bullet point
                    pdf.drawString(70, y_position, '•')
                    # Draw text after bullet with proper indentation
                    text = line.strip()[1:].strip()
                    wrapped_text = textwrap.wrap(text, width=85)
                    for i, wrapped_line in enumerate(wrapped_text):
                        if i == 0:
                            pdf.drawString(85, y_position, wrapped_line)
                        else:
                            pdf.drawString(85, y_position - (i * 15), wrapped_line)
                    y_position -= (len(wrapped_text) * 15) + 5
                # Handle numbered lists
                elif line.strip().startswith(str(current_number) + '.'):
                    # Draw number
                    number_text = f"{current_number}."
                    pdf.drawString(70, y_position, number_text)
                    # Draw text after number with proper indentation
                    text = line.strip()[len(number_text):].strip()
                    wrapped_text = textwrap.wrap(text, width=85)
                    for i, wrapped_line in enumerate(wrapped_text):
                        if i == 0:
                            pdf.drawString(85, y_position, wrapped_line)
                        else:
                            pdf.drawString(85, y_position - (i * 15), wrapped_line)
                    y_position -= (len(wrapped_text) * 15) + 5
                    current_number += 1
                else:
                    # Regular text without bullet or number
                    wrapped_text = textwrap.wrap(line, width=90)
                    for wrapped_line in wrapped_text:
                        pdf.drawString(70, y_position, wrapped_line)
                        y_position -= 15
                    # Reset number counter for new lists
                    current_number = 1
                
                y_position -= 5  # Add some spacing between lines
            
            y_position -= 10
        
        return y_position

    def add_images_section(y_position, activity):
        """Add images in a grid layout"""
        if include_images and activity.images.exists():
            # Images header
            pdf.setFillColor(colors_dict['primary'])
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(40, y_position, f"Images ({activity.images.count()})")
            y_position -= 30

            images = activity.images.all()
            images_per_row = 3 if orientation == "landscape" else 2
            # Adjust margins and spacing
            left_margin = 40
            right_margin = 40
            spacing = 20  # Space between images
            available_width = width - left_margin - right_margin
            image_width = (available_width - (spacing * (images_per_row - 1))) / images_per_row
            image_height = 160  # Adjusted height for better proportions

            for i, image in enumerate(images):
                if y_position < 200:  # Increased threshold to prevent footer overlap
                    pdf.showPage()
                    y_position = height - 120  # Start higher to leave room for footer
                    add_page_header(pdf._pageNumber)

                row = i // images_per_row
                col = i % images_per_row
                x_position = left_margin + (col * (image_width + spacing))
                
                try:
                    pdf.drawImage(
                        ImageReader(image.image.path),
                        x_position,
                        y_position - image_height,
                        width=image_width,
                        height=image_height,
                        preserveAspectRatio=True
                    )
                except Exception as e:
                    print(f"Error adding image: {e}")

                if (i + 1) % images_per_row == 0:
                    y_position -= (image_height + 40)  # Increased spacing between rows

            if len(images) % images_per_row != 0:
                y_position -= (image_height + 40)

        return y_position

    # Generate PDF content
    page_num = 2  # Start from page 2 (cover page is page 1)
    for activity in activities:
        if page_num > 2:
            pdf.showPage()
        
        add_page_header(pdf._pageNumber, activity)
        add_footer()
        y_position = height - 130
        
        # Add activity content
        y_position = add_activity_header(y_position, activity)
        y_position = add_metadata_section(y_position, activity)
        
        # Add separator line
        pdf.setStrokeColor(colors_dict['border'])
        pdf.line(60, y_position, width - 60, y_position)
        y_position -= 20
        
        # Check if we have enough space for remarks section before calling it
        if y_position < 100:  # Very low threshold to ensure remarks stays on same page
            pdf.showPage()
            y_position = height - 120
            add_page_header(pdf._pageNumber)
        
        y_position = add_remarks_section(y_position, activity)
        
        # Another separator before images
        pdf.setStrokeColor(colors_dict['border'])
        pdf.line(60, y_position, width - 60, y_position)
        y_position -= 20
        
        y_position = add_images_section(y_position, activity)
        
        # Add end of report text
        # Add end of report text
        # Check if we have enough space for end text
        if y_position < 150:  # Need space for end text + footer
            pdf.showPage()
            y_position = height - 120
            add_page_header(pdf._pageNumber)
        
        y_position -= 30
        pdf.setFont("Helvetica-Bold", 14)
        pdf.setFillColor(colors_dict['primary'])
        pdf.drawString(60, y_position, "End of the Report")
        
        y_position -= 20
        pdf.setFont("Helvetica", 12)
        pdf.setFillColor(colors_dict['dark'])
        pdf.drawString(60, y_position, "Thank you!")
        
        page_num += 1

    # Save PDF
    pdf.save()
    buffer.seek(0)

    # Create response
    response = HttpResponse(buffer, content_type="application/pdf")
    filename = f"technical_activities_report_{today.strftime('%Y%m%d')}.pdf"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response


# This is for Errors
def custom_403(request, exception=None):
    return render(request, "forbidden/403.html", status=403)


def custom_404(request, exception):
    return render(request, "forbidden/404.html", status=404)


def custom_500(request):
    return render(request, "forbidden/500.html", status=500)


def trigger_500(request):
    raise ValueError("Intentional Server Error")


@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@login_required(login_url='omsLogin')
def tech_activity_update(request, pk):
    """View for updating technical activities."""
    activity = get_object_or_404(C2TechActivities, id=pk)
    
    if request.method == "POST":
        form = TechnicalActivitiesForm(request.POST, instance=activity)
        if form.is_valid():
            tech_activity = form.save(commit=False)
            
            # Decode HTML entities in remarks before saving
            if tech_activity.remarks:
                import html
                
                # Decode all HTML entities
                decoded_remarks = html.unescape(tech_activity.remarks)
                
                # Update the remarks with decoded text
                tech_activity.remarks = decoded_remarks
            
            tech_activity.remark_by = C2User.objects.get(name__id=request.user.id)
            tech_activity.save()
            messages.success(request, 'Activity updated successfully!')
            return redirect('activity_list')
    else:
        form = TechnicalActivitiesForm(instance=activity)

    return render(request, "c2/tech_activity_update.html", {
        "form": form,
        "activity": activity,
        "title": f"Update Activity: {activity.name}"
    })


@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@login_required(login_url='omsLogin')
def update_image_label(request):
    """AJAX view to update image label"""
    print(f"update_image_label called with method: {request.method}")
    print(f"Request body: {request.body}")
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    try:
        data = json.loads(request.body)
        image_id = data.get('image_id')
        label = data.get('label', '').strip()
        
        print(f"Parsed data: image_id={image_id}, label='{label}'")
        
        if not image_id:
            return JsonResponse({'success': False, 'error': 'Image ID is required'})
        
        # Get the image object
        image = get_object_or_404(C2TechActivityImage, id=image_id)
        print(f"Found image: {image}")
        
        # Check if user has permission to edit this image
        # (You can add more specific permission checks here if needed)
        
        # Update the label
        image.label = label if label else None
        image.save()
        print(f"Updated image label to: '{image.label}'")
        
        return JsonResponse({
            'success': True, 
            'message': 'Label updated successfully',
            'label': image.label or ''
        })
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        print(f"General error: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@restrict_for_c2group_only(allowed_groups=['EV', 'AM', 'EMP'])
@login_required(login_url='omsLogin')
def delete_activity_c2(request, activity_id):
    """
    Delete a technical activity with confirmation
    """
    try:
        # Get the activity object
        activity = get_object_or_404(C2TechActivities, id=activity_id)
        
        # Check if user has permission to delete this activity
        # Only allow deletion if user is the uploader or is in EV group
        if not (activity.uploaded_by == request.user.users or 
                request.user.groups.filter(name="EV").exists()):
            messages.error(request, "🚫 You don't have permission to delete this activity.")
            return redirect('activity_list')
        
        # Delete the activity (this will cascade delete all related images)
        activity_name = activity.name
        activity.delete()
        
        messages.success(request, f"✅ Activity '{activity_name}' has been successfully deleted.")
        
    except Http404:
        messages.error(request, "❌ Activity not found.")
    except Exception as e:
        messages.error(request, f"❌ An error occurred while deleting the activity: {str(e)}")
    
    return redirect('activity_list')
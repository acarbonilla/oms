from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# Decorator for only allowing eV group
from django.contrib.auth.decorators import user_passes_test

from django.shortcuts import render, redirect, get_object_or_404

# This is for QR
from django.urls import reverse
from django.utils.html import strip_tags
from reportlab.lib import colors

from c2.forms import C2RecentImageForm, C2RecentImageFormUpdate, TechnicalActivitiesForm
# from c2.filters import FacilityFilter
from c2.models import C2Standard, C2RecentImage, C2User, C2Facility, C2TechActivities, C2TechActivityImage

from django.db.models import OuterRef, Subquery

from django.contrib import messages
# This for time
from django.utils.timezone import now
from datetime import timedelta
from django.core.paginator import Paginator  # ✅ Import Paginator
from django.db.models import Q, Count

# pdf
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from django.utils.timezone import now
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from .models import C2RecentImage  # Ensure correct model import
from django.contrib.staticfiles import finders
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.lib.styles import getSampleStyleSheet
import textwrap

# local time
from django.utils.timezone import localtime

# Decorators
from django.http import HttpResponseForbidden
from functools import wraps


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
    }
    return render(request, 'c2/ev/ev_dashboard.html', context)


@login_required(login_url='omsLogin')
def empMember(request):
    facilities = C2Facility.objects.all()  # ✅ Fetch all facilities
    name = User.objects.all()
    context = {'name': name, 'facilities': facilities}
    return render(request, 'c2/emp/emp_list.html', context)


@login_required(login_url='omsLogin')
def amMember(request):
    name = User.objects.all()
    context = {'name': name}
    return render(request, 'c2/am/am_list.html', context)


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
    paginator = Paginator(combined_data, 2)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search_query": search_query
    }
    return render(request, "c2/assessment.html", context)


@user_passes_test(ev_group_required, login_url='omsLogin')  # ✅ Redirect if not in "EV" group
def upload_recent_image_qr(request, facility_id):
    """Handles QR code scanning and redirects users to the upload form."""

    request.session['last_facility_id'] = facility_id
    request.session.modified = True

    facility = get_object_or_404(C2Facility, id=facility_id)

    if request.method == "POST":
        form = C2RecentImageForm(request.user, request.POST, request.FILES)
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
            messages.error(request, ", ".join([str(error) for error in form.errors.values()]))

    else:
        form = C2RecentImageForm(request.user)

    return render(request, 'c2/ev/upload_recent_image_qr.html', {'form': form, 'facility': facility})


# This section is for uploading or updating the recent image.

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

    return render(request, 'c2/ev_update_recent_image.html', {'form': form, 'recent_image': recent_image})


# Details Section
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
    })


# This is for EV Standard Image
@restrict_emp_group(redirect_url="access_denied")  # Redirect EMP users to home page
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


@restrict_emp_group(redirect_url="access_denied")  # Redirect EMP users to home page
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
@restrict_emp_group(redirect_url="access_denied")  # Redirect EMP users to home page
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

    return render(request, 'c2/failed_list.html', {'page_obj': page_obj, 'search_query': search_query})


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
            y_position = height - 50
            pdf.setFont("Helvetica", 12)

    pdf.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="C2RecentImage_Report.pdf"'
    return response


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
            watermark_path = finders.find("report_logo/fm_2.png")
            if watermark_path:
                pdf.saveState()
                pdf.setFillAlpha(0.1)  # Transparency
                pdf.drawImage(ImageReader(watermark_path), width / 3, height / 3, width=300, height=150, mask='auto')
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
    }
    return render(request, 'c2/pass_list.html', context)


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
    }
    return render(request, 'c2/ev/not_visited_facilities_list.html', context)


# This is for Technical Activities
@login_required(login_url='omsLogin')
def tech_act_upload(request, pk=None):
    tech = get_object_or_404(C2TechActivities, id=pk) if pk else None

    if request.method == "POST":
        form = TechnicalActivitiesForm(request.POST, instance=tech)

        if form.is_valid():
            tech_activity = form.save(commit=False)

            # ✅ Correctly get the C2User instance
            tech_activity.uploaded_by = C2User.objects.get(name__id=request.user.id)

            tech_activity.save()

            # ✅ Handle multiple image uploads
            files = request.FILES.getlist('image')
            for file in files:
                C2TechActivityImage.objects.create(activity=tech_activity, image=file)

            return redirect('empMember')
    else:
        form = TechnicalActivitiesForm(instance=tech)

    return render(request, "c2/tech_act_upload.html", {"activity_form": form})


# This is for tech view list
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
    paginator = Paginator(activities, 5)  # Show 5 activities per page
    activities_page = paginator.get_page(page_number)

    return render(
        request,
        "c2/activity_list.html",
        {
            "activities": activities_page,
            "filter_option": filter_option,
            "search_query": search_query
        }
    )


@login_required(login_url='omsLogin')
def activity_detail(request, activity_id):
    """View to show details of a specific activity with images."""
    activity = get_object_or_404(C2TechActivities, id=activity_id)
    return render(request, "c2/activity_detail.html", {"activity": activity})


# This is for Errors
def custom_403(request, exception=None):
    return render(request, "forbidden/403.html", status=403)


def custom_404(request, exception):
    return render(request, "forbidden/404.html", status=404)


def custom_500(request):
    return render(request, "forbidden/500.html", status=500)


def trigger_500(request):
    raise ValueError("Intentional Server Error")

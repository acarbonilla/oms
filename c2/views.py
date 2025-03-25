from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# Decorator for only allowing eV group
from django.contrib.auth.decorators import user_passes_test

from django.shortcuts import render, redirect, get_object_or_404

# This is for QR
from django.urls import reverse

from c2.forms import C2RecentImageForm, C2RecentImageFormUpdate
# from c2.filters import FacilityFilter
from c2.models import C2Standard, C2RecentImage, C2User, C2Facility

from django.db.models import OuterRef, Subquery

from django.contrib import messages
# This for time
from django.utils.timezone import now
from datetime import timedelta
from django.core.paginator import Paginator  # ✅ Import Paginator
from django.db.models import Q, Count

# pdf

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from django.utils.timezone import now
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from .models import C2RecentImage  # Ensure correct model import
from django.contrib.staticfiles import finders


@login_required(login_url='omsLogin')
def evMember(request):
    facilities = C2Facility.objects.all()  # ✅ Fetch all facilities
    name = User.objects.all()
    context = {'name': name, 'facilities': facilities}
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


# This is for only user belong to EV group can access the upload_recent_image_qr
def ev_group_required(user):
    return user.groups.filter(name="EV").exists()


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


# This is for QR code creation and link

# This section is for uploading or updating the recent image.

@login_required(login_url='omsLogin')
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
@user_passes_test(ev_group_required, login_url='omsLogin')  # ✅ Redirect if not in "EV" group
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


@user_passes_test(ev_group_required, login_url='omsLogin')  # ✅ Redirect if not in "EV" group
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

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="C2RecentImage_Report.pdf"'
    return response


@login_required(login_url='omsLogin')
def generate_selected_pdf(request):
    """Generate a PDF report with images, ensuring each selected record is on a single page."""

    selected_ids = request.GET.getlist("selected_ids", [])
    search_query = request.GET.get("search", "")
    current_year = now().year

    images = C2RecentImage.objects.filter(created__year=current_year).exclude(status="Pending")

    if search_query:
        images = images.filter(Q(title__icontains=search_query) | Q(s_image__facility__name__icontains=search_query))

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
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    for img in images:
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(150, height - 50, f"Selected C2 Recent Image Report - {current_year}")

        y_position = height - 100
        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, y_position, f"Title: {img.title}")
        pdf.drawString(50, y_position - 20, f"Facility: {img.s_image.facility.name}")
        pdf.drawString(50, y_position - 40, f"Status: {img.status}")
        pdf.drawString(50, y_position - 60, f"Remarks: {img.remarks if img.remarks else 'N/A'}")
        pdf.drawString(50, y_position - 80, f"Re-Schedule: {img.re_schedule if img.re_schedule else 'N/A'}")
        pdf.drawString(50, y_position - 100, f"Evaluated By: {img.remark_by if img.remark_by else 'N/A'}")
        pdf.drawString(50, y_position - 120,
                       f"Updated: {img.updated.strftime('%Y-%m-%d %H:%M:%S') if img.updated else 'N/A'}")
        pdf.drawString(50, y_position - 140,
                       f"Created: {img.created.strftime('%Y-%m-%d %H:%M:%S') if img.created else 'N/A'}")

        # ✅ Fetch Assigned Users for the Facility
        assigned_users = C2User.objects.filter(facility=img.s_image.facility)
        user_names = ", ".join(
            [user.name.username for user in assigned_users]) if assigned_users else "No Assigned Users"
        pdf.drawString(50, y_position - 160, f"In-charge: {user_names}")

        # ✅ Include Image
        if img.recent_image:
            try:
                img_path = img.recent_image.path
                pdf.drawImage(ImageReader(img_path), 50, y_position - 310, width=200, height=150)
            except Exception as e:
                print(f"Error loading image: {e}")

        # ✅ Add logos at the bottom
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(200, 100, "End of Report")

        try:
            logo1_path = finders.find("report_logo/JWS-FM Logo.JPG")
            logo2_path = finders.find("report_logo/zfc-logo.png")

            if logo1_path:
                pdf.drawImage(ImageReader(logo1_path), 50, 50, width=100, height=50)
            else:
                print("Error: JWS-FM Logo not found")

            if logo2_path:
                pdf.drawImage(ImageReader(logo2_path), 200, 50, width=100, height=50)
            else:
                print("Error: ZFC Logo not found")
        except Exception as e:
            print(f"Error loading logos: {e}")

        pdf.showPage()  # ✅ Ensure each entry starts on a new page

    pdf.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Selected_C2RecentImage_Report.pdf"'
    return response

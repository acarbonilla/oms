from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404

from c2.forms import C2RecentImageForm, C2RecentImageFormUpdate
# from c2.filters import FacilityFilter
from c2.models import C2Standard, C2RecentImage, C2User, C2Facility

from django.db.models import OuterRef, Subquery

from django.contrib import messages

from django.http import JsonResponse


@login_required(login_url='omsLogin')
def empMember(request):
    name = User.objects.all()
    context = {'name': name}
    return render(request, 'c2/emp/emp_list.html', context)


@login_required(login_url='omsLogin')
def amMember(request):
    name = User.objects.all()
    context = {'name': name}
    return render(request, 'c2/am/am_list.html', context)


@login_required(login_url='omsLogin')
def amAssessment(request):
    # This code is to output only 1 recent image and 1 recent standard of each facility or location. (Start the line
    # of Code) Subquery to get the latest Recent Image per facility
    latest_recent = C2RecentImage.objects.filter(
        facility=OuterRef('facility')
    ).order_by('-updated', '-id').values('id')[:1]

    # Query to get latest Recent Images and exclude the status: Pass
    latest_recent_images = C2RecentImage.objects.filter(
        id=Subquery(latest_recent)
    ).exclude(status="Pass")

    # Create a dictionary for quick lookup of standard images
    standard_image_dict = {rec.s_image.facility.id: rec.s_image for rec in latest_recent_images if rec.s_image}

    # Combine the results in a list with facility-wise data
    combined_data = []
    for recent in latest_recent_images:
        id = recent.id
        title = recent.title
        facility = recent.facility # alter this later
        standard_image = standard_image_dict.get(facility.id, None)  # Get related standard image
        combined_data.append({
            'id': id,
            'title': title,
            'facility': facility, # Marking
            'recent_image': recent.recent_image.url if recent.recent_image else None,
            'standard_image': standard_image.standard_image.url if standard_image and standard_image.standard_image else None
        })
    # This code is to output only 1 recent image and 1 recent standard of each facility or location. (End line of Code)

    context = {'combined_data': combined_data}
    return render(request, 'c2/am/assessment.html', context)


@login_required(login_url='omsLogin')
def upload_recent_image(request):
    if request.method == "POST":
        form = C2RecentImageForm(request.user, request.POST, request.FILES)  # Fix argument order
        if form.is_valid():
            lead = form.save(commit=False)  # Don't save yet
            try:
                lead.uploaded_by = C2User.objects.get(name=request.user)  # Set uploaded_by
                lead.save()
                messages.success(request, "Image uploaded successfully!")
                return redirect('upload_recent_image')
            except C2User.DoesNotExist:
                messages.error(request, "User not found in C2User.")

        else:
            for error in list(form.errors.values()):
                messages.error(request, ", ".join(error))  # Fix error message formatting

    else:
        form = C2RecentImageForm(request.user)  # Ensure user is always passed

    return render(request, 'c2/emp/form/upload_recent_image.html', {'form': form})


@login_required(login_url='omsLogin')
def update_recent_image(request, pk):
    proved = get_object_or_404(C2RecentImage, id=pk)  # Use get_object_or_404 for better error handling
    form = C2RecentImageFormUpdate(request.POST or None, request.FILES or None, instance=proved)

    if request.method == "POST":  # Ensure form is only processed on POST requests
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully updated the form.")  # Message on success
            return redirect('assessment')  # Redirect after submission to avoid refresh issues
        else:
            messages.error(request, "There was an error updating the form.")  # Handle form errors
            print("❌ Form Errors:", form.errors)
    return render(request, 'c2/am/form/update_recent_image.html', {'form': form})


# Details Section
@login_required(login_url='omsLogin')
def recent_image_detail(request, pk):
    image = get_object_or_404(C2RecentImage, pk=pk)
    return render(request, 'c2/am/recent_image_detail.html', {'image': image})
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .forms import CSVFileForm
from .models import CSVFile
from django.contrib import messages
import pandas as pd
import csv
import os
from django.http import JsonResponse

# Create your views here.
def upload_file(request):
    if request.method == "POST" and request.FILES.get('file'):
        csv_file = request.FILES['file']

        # check if its a csv file
        if not csv_file.name.endswith('.csv'):
            return JsonResponse({'error': 'File is not CSV type'})
        
        # save file to database and filesystem
        uploaded_file = CSVFile.objects.create(file=csv_file)

        # read the CSV content
        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.file.name)
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            csv_data = list(reader)
        # decoded_file = csv_file.read().decode('utf-8').splitlines()
        # reader = csv.reader(decoded_file)
        # csv_data = list(reader)

        # send the CSV content back to the template
        return render(request, 'upload.html', {'csv_data': csv_data, 'file': uploaded_file})
    return render(request, 'upload.html')
    # if request.method == 'POST':
    #     form = CSVFileForm(request.POST, request.FILES)
    #     if form.is_valid():
    #         form.save()
    #         messages.success(request, 'File uploaded successfully.')
    #         return redirect('file_list')
    #     else:
    #         # Form is invalid, errors will be displayed in the template
    #         messages.error(request, 'There was an error uploading your file. Please ensure it is a CSV.')
    # else:
    #     form = CSVFileForm()
    # return render(request, 'upload.html', {'form': form})

def file_list(request):
    files = CSVFile.objects.all().order_by('-uploaded_at')
    return render(request, 'file_list.html', {'files': files})

def file_detail(request, file_id):
    csv_file = CSVFile.objects.get(id=file_id)
    return render(request, 'file_detail.html', {'csv_file': csv_file})

def select_file(request, file_id):
    csv_file = get_object_or_404(CSVFile, id= file_id)
    messages.success(request, f'File "{csv_file.name}" has been selected for further use')
    return redirect('file_list')
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .forms import CSVFileForm
from .models import CSVFile
from django.contrib import messages
import pandas as pd
import csv
import os
from django.http import JsonResponse
import plotly.express as px
import plotly.io as pio

# Create your views here.
def upload_file(request):
    if request.method == "POST" and request.FILES.get('file'):
        csv_file = request.FILES['file']
        
        # save file to database and filesystem
        uploaded_file = CSVFile.objects.create(file=csv_file)

        # read the CSV content
        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.file.name)

        # load CSV into a Pandas Dataframe
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            messages.error(request, f'Error reading the CSV file: {e}')
            return redirect('upload_file')

        # cleaning and preprocessing the data
        cleaned_df = df.copy()

        # preprocessing steps
        cleaned_df.dropna(inplace=True) # drop rows with missing values
        cleaned_df.drop_duplicates(inplace=True) # drop duplicate rows
        cleaned_df = cleaned_df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)    # strip whitespace
        cleaned_df = cleaned_df.fillna(0)   # replace any NaN with 0
        # cleaned_df = cleaned_df.apply(lambda x: x.str.lower() if x.dtype == "object" else x)    # convert to lowercase
        # cleaned_df.reset_index(drop=True, inplace=True) # reset the index

        # convert original and cleaned dataframe to HTML tables
        original_data = df.to_html(classes='table table-striped table-bordered table-dark table-hover', index=False)
        cleaned_data = cleaned_df.to_html(classes='table table-striped table-bordered table-dark table-hover', index=False)

        # generate Plotly Graphs

        # 1. Histogram for each numerical columns
        histograms = []
        numerical_cols = cleaned_df.select_dtypes(include=['number']).columns
        for column in numerical_cols:
            fig = px.histogram(cleaned_df, x = column, title=f'Histogram of {column}', nbins=20)
            hist_div = pio.to_html(fig, full_html=False, include_plotlyjs=False)
            histograms.append({'title': f'Histogram of {column}', 'div':hist_div})

        # 2. Scatter Plot between first two numerical columns(if at least two exist)
        scatter_div = None
        if len(numerical_cols)>=2:
            fig = px.scatter(cleaned_df, x=numerical_cols[0], y=numerical_cols[1], title=f'Scatter Plot of {numerical_cols[0]} vs {numerical_cols[1]}', trendline="ols")
            scatter_div = pio.to_html(fig, full_html=False, include_plotlyjs=False)


        # send original and cleaned data back to the template
        context = {
            'original_data': original_data,
            'original_data_info': {
                'rows': df.shape[0],
                'coumns': df.shape[1],
                'column_names': df.columns.tolist()
            },
            'cleaned_data': cleaned_data,
            'cleaned_data_info': {
                'rows': cleaned_df.shape[0],
                'coumns': cleaned_df.shape[1],
                'column_names': cleaned_df.columns.tolist()
            },
            'file': uploaded_file,
            'histograms': histograms,
            'scatter_div': scatter_div,
        }


        # with open(file_path, newline='', encoding='utf-8') as f:
        #     reader = csv.reader(f)
        #     csv_data = list(reader)
        # decoded_file = csv_file.read().decode('utf-8').splitlines()
        # reader = csv.reader(decoded_file)
        # csv_data = list(reader)

        # send the CSV content back to the template
        return render(request, 'upload.html', context)
    # uploaded_file = CSVFile.objects.all()
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
    csv_file = get_object_or_404(CSVFile, id=file_id)
    file_path = csv_file.file.path

    # read and parse the CSV file
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        csv_data = list(reader)
    context = {
        'csv_file': csv_file,
        'csv_data': csv_data,
    }
    return render(request, 'file_detail.html', context)

def select_file(request, file_id):
    csv_file = get_object_or_404(CSVFile, id= file_id)
    messages.success(request, f'File "{csv_file.file.name}" has been selected for further use')
    return redirect('file_list')
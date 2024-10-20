from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import CSVFile
from django.contrib import messages
import pandas as pd
import os
import plotly.express as px
import plotly.io as pio

# Create your views here.
def cleaning_data(dataframe):

    # preprocessing steps
    dataframe.dropna(inplace=True) # drop rows with missing values
    dataframe.drop_duplicates(inplace=True) # drop duplicate rows
    dataframe = dataframe.apply(lambda x: x.str.strip() if x.dtype == "object" else x)    # strip whitespace
    dataframe = dataframe.fillna(0)   # replace any NaN with 0
    dataframe = dataframe.apply(lambda x: x.str.lower() if x.dtype == "object" else x)    # convert to lowercase
    dataframe.reset_index(drop=True, inplace=True) # reset the index
    return dataframe

def upload_file(request):
    if request.method == "POST":
        # send the CSV content back to the template
        return render(request, 'data_info.html')
    request.session.flush()
    return render(request, 'upload.html')

def data_view(request):
    if request.FILES.get('file'):
        csv_file = request.FILES['file']
        uploaded_file = CSVFile.objects.create(file=csv_file)
        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.file.name)
        request.session['recent_file_path'] = file_path
        
    # load CSV into a Pandas Dataframe
    try:
        df = pd.read_csv(request.session.get('recent_file_path'))
    except Exception as e:
        messages.error(request, f'Error reading the CSV file: {e}')
        return redirect('upload_file')

    # cleaning and preprocessing the data
    cleaned_df = df.copy()
    # cleaned dataframe returned
    cleaned_df = cleaning_data(cleaned_df)

    # convert original and cleaned dataframe to HTML tables
    original_data = df.to_html(classes='table table-striped table-bordered table-dark table-hover', table_id="original-data", index=False)
    cleaned_data = cleaned_df.to_html(classes='table table-striped table-bordered table-dark table-hover', table_id='cleaned-data', index=False)

    # get cloumn names for selection
    numerical_columns = cleaned_df.select_dtypes(include=['number']).columns.tolist()
    categorical_columns = cleaned_df.select_dtypes(include=['object', 'category']).columns.tolist()

    # generate Plotly Graphs
    # 1. Histogram for each numerical columns
    histograms = []
    numerical_cols = cleaned_df.select_dtypes(include=['number']).columns
    for column in numerical_cols:
        fig = px.histogram(cleaned_df, x = column, title=f'Histogram of {column}', nbins=20, template='plotly_dark')
        hist_div = pio.to_html(fig, full_html=False, include_plotlyjs=False)
        histograms.append({'title': f'Histogram of {column}', 'div':hist_div})

    # 2. Scatter Plot between first two numerical columns(if at least two exist)
    scatter_plot = []
    if len(numerical_cols)>=2:
        for i in range(len(numerical_cols)-1):
            fig = px.scatter(cleaned_df, x=numerical_cols[i], y=numerical_cols[i+1], title=f'Scatter Plot of {numerical_cols[i]} vs {numerical_cols[i+1]}', trendline="ols", template='plotly_dark')
            scatter_div = pio.to_html(fig, full_html=False, include_plotlyjs=False)
            scatter_plot.append({'title': f'Scatter Plot of {numerical_cols[i]} vs {numerical_cols[i+1]}', 'div': scatter_div})
        
    
    # send original and cleaned data back to the template
    context = {
        'original_data_info': {
            'rows': df.shape[0],
            'columns': df.shape[1],
            'column_names': df.columns.tolist()
        },
        'cleaned_data_info': {
            'rows': cleaned_df.shape[0],
            'columns': cleaned_df.shape[1],
            'column_names': cleaned_df.columns.tolist()
        },
        'histograms': histograms,
        'scatter_plot': scatter_plot,
        'cleaned_data': cleaned_data,
        'original_data': original_data,
        'numerical_columns': numerical_columns,
        'categorical_columns': categorical_columns,
    }
    # send the CSV content back to the template
    return render(request, 'data_info.html', context)

def generate_graphs(request):
    if request.method == 'POST':
        # load the CSV file from the session
        file_path = request.session.get('recent_file_path')
        if not file_path:
            messages.error(request, 'File path is not availabe in the session')
            return redirect('upload_file')
        
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            messages.error(request, f'Error reading the CSV file: {e}')
            return redirect('upload_file')
        
        cleaned_df = df.copy()
        # cleaning and preprocessing
        cleaned_df = cleaning_data(cleaned_df)

        # retrieve existing graphs from the session if available
        graphs = request.session.get('graphs', [])
        
        # generate graphs based on user input
        plot_type = request.POST.get('plot_type')
        x_column = request.POST.get('x_column')
        y_column = request.POST.get('y_column')

        if plot_type == 'bar' and x_column:
            fig = px.bar(cleaned_df, x=x_column, title=f'Bar Chart of {x_column}', template='plotly_dark')
            graph_div = pio.to_html(fig, full_html=False, include_plotlyjs=False)
            graphs.append({'title': f'Bar Chart of {x_column}', 'div': graph_div})

        elif plot_type == 'hist' and x_column:
            fig = px.histogram(cleaned_df, x=x_column, title=f'Histogram of {x_column}', nbins=20, template='plotly_dark')
            graph_div = pio.to_html(fig, full_html=False, include_plotlyjs=False)
            graphs.append({'title': f'Histogram of {x_column}', 'div': graph_div})

        elif plot_type == 'scatter' and x_column and y_column:
            fig = px.scatter(cleaned_df, x=x_column, y=y_column, title=f'Scatter Plot of {x_column} vs {y_column}', trendline="ols", template='plotly_dark')
            graph_div = pio.to_html(fig, full_html=False, include_plotlyjs=False)
            graphs.append({'title': f'Scatter Plot of {x_column} vs {y_column}', 'div': graph_div})
        
        elif plot_type == 'pie' and x_column:
            fig = px.pie(cleaned_df, names=x_column, title=f'Pie Chart of {x_column}', template='plotly_dark')
            fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
            graph_div = pio.to_html(fig, full_html=False, include_plotlyjs=False)
            graphs.append({'title': f'Pie Chart of {x_column}', 'div': graph_div})

        elif plot_type == 'line' and x_column and y_column:
            fig = px.line(cleaned_df, x=x_column, y=y_column, title=f'Line Chart of {x_column} vs {y_column}', template='plotly_dark')
            graph_div = pio.to_html(fig, full_html=False, include_plotlyjs=False)
            graphs.append({'title': f'Line Chart of {x_column} vs {y_column}', 'div': graph_div})

        # Save the graphs in the session
        request.session['graphs'] = graphs

        # If the user clicked "Add Graph", redirect back to the data_view
        if 'graph' in request.GET:
            return render(request, 'data_view', {'graphs': graphs})

        context = {
            'graphs': graphs
            }
        return render(request, 'graphs.html', context)
    return redirect('upload_file')

# views.py
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django_xhtml2pdf.utils import generate_pdf

def download_graphs_pdf(request):
    graphs = request.session.get('graphs', [])  # Fetch your graphs data
    html = render_to_string('graphs.html', {'graphs': graphs})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="graphs.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def file_list(request):
    files = CSVFile.objects.all()
    request.session.flush()
    return render(request, 'file_list.html', {'files': files})

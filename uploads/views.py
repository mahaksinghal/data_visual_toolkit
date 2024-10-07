from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import CSVFile
from django.contrib import messages
import pandas as pd
import csv
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
        original_data = df.to_html(classes='table table-striped table-bordered table-dark table-hover',table_id="original-data", index=False)
        cleaned_data = cleaned_df.to_html(classes='table table-striped table-bordered table-dark table-hover',table_id='cleaned-data', index=False)

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
            
        # Initialize Empty Graphs
        graphs = []
        # if the user has selected columns for graphing, generate the graphs
        if 'plot_type' in request.POST:
            plot_type = request.POST.get('plot_type')
            x_column = request.POST.get('x_column')
            y_column = request.POST.get('y_column')

            if plot_type == 'bar' and x_column:
                fig = px.bar(cleaned_df, x=x_column, title=f'Bar Chart of {x_column}', template='plotly_dark')
                graph_div = pio.to_html(fig, full_html=False, include_plotlyjs=False)
                graphs.append({'title': f'Bar Chart of {x_column}', 'div': graph_div})
            
            elif plot_type == 'scatter' and x_column and y_column:
                fig = px.scatter(cleaned_df, x=x_column, y=y_column, title=f'Scatter Plot of {x_column} vs {y_column}', trendline="ols", template='plotly_dark')
                graph_div = pio.to_html(fig, full_html=False, include_plotlyjs=False)
                graphs.append({'title': f'Scatter Plot of {x_column} vs {y_column}', 'div': graph_div})
            
            elif plot_type == 'histogram' and x_column:
                fig = px.histogram(cleaned_df, x=x_column, title=f'Histogram of {x_column}', nbins=20, template='plotly_dark')
                graph_div = pio.to_html(fig, full_html=False, include_plotlyjs=False)
                graphs.append({'title': f'Histogram of {x_column}', 'div': graph_div})

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
            'graphs': graphs,
            'histograms': histograms,
            'scatter_plot': scatter_plot,
            'cleaned_data': cleaned_data,
            'original_data': original_data,
            'numerical_columns': numerical_columns,
            'categorical_columns': categorical_columns,
        }
        # send the CSV content back to the template
        return render(request, 'data_view.html', context)
    # uploaded_file = CSVFile.objects.all()
    return render(request, 'upload.html')

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






# def load_bar_chart(request, file_id):
#     uploaded_file = get_object_or_404(CSVFile, id = file_id)
#     file_path = os.path.join(settings.MEDIA_ROOT, upload_file.file.name)

#     try:
#         df = pd.read_csv(file_path)
#     except Exception as e:
#         messages.error(request, f'Error reading the CSV file: {e}')
#         return redirect('upload_file')
    
#     # cleaning and preprocessing the data
#     cleaned_df = df.copy()
#     cleaned_df.dropna(inplace=True)
#     cleaned_df.drop_duplicates(inplace=True)
#     cleaned_df = cleaned_df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
#     cleaned_df = cleaned_df.fillna(0)

#     # generate bar chart
#     categorical_col = None
#     for col in cleaned_df.columns:
#         if cleaned_df[col].dtype == 'object':
#             categorical_col = col
#             break

#     if categorical_col:
#         fig_bar = px.bar(cleaned_df, x=categorical_col, title=f'Count of {categorical_col}')
#         graph_html = fig_bar.to_html(full_html=False, include_plotlyjs=False)
#         context = {
#             'graph_title': f'Bar Chart of {categorical_col}',
#             'graph_html': graph_html,
#         }
#         return render(request, 'bar_chart.html', context)
#     else:
#         return JsonResponse({'error': 'No categorical column found.'})
    

# def load_scatter_plot(request, file_id):
    # uploaded_file = get_object_or_404(CSVFile, id=file_id)
    # file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.file.name)

    # try:
    #     df = pd.read_csv(file_path)
    #     cleaned_df = df.copy()
    #     cleaned_df.dropna(inplace=True)
    #     cleaned_df.drop_duplicates(inplace=True)
    #     cleaned_df = cleaned_df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    #     cleaned_df = cleaned_df.fillna(0)

    #     numerical_cols = cleaned_df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    #     if len(numerical_cols) >= 2:
    #         fig_scatter = px.scatter(cleaned_df, x=numerical_cols[0], y=numerical_cols[1], title=f'{numerical_cols[0]} vs {numerical_cols[1]}')
    #         graph_html = fig_scatter.to_html(full_html=False, include_plotlyjs=False)
    #         context = {
    #             'graph_title': f'Scatter Plot of {numerical_cols[0]} vs {numerical_cols[1]}',
    #             'graph_html': graph_html,
    #         }
    #         return render(request, 'scatter_plot.html', context)
    #     else:
    #         return JsonResponse({'error': 'Not enough numerical columns for scatter plot.'})

    # except Exception as e:
    #     return JsonResponse({'error': str(e)})
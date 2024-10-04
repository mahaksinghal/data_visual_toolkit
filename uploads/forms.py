from django import forms
from .models import CSVFile
from django.core.exceptions import ValidationError
import os

class CSVFileForm(forms.ModelForm):
    class Meta:
        model = CSVFile
        fields = ['file']

    # def clean_file(self):
    #     file = self.cleaned_data.get('file', False)
    #     if file:
    #         ext = os.path.splitext(file.name)[1].lower()
    #         if ext != '.csv':
    #             raise ValidationError('File type is not supported.')
    #         if file.size > 5 * 1024 * 1024:
    #             raise ValidationError('File size must be under 5MB.')
    #     else:
    #         raise ValidationError('Could not read the uploaded file.')
    #     return file
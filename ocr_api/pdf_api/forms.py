from django import forms
from multiupload.fields import MultiFileField

class PdfUploadForm(forms.Form):
    pdf_files = MultiFileField(label='Select PDF files')

    def clean_pdf_files(self):
        pdf_files = self.cleaned_data['pdf_files']
        for pdf_file in pdf_files:
            if not pdf_file.name.endswith('.pdf'):
                raise forms.ValidationError("Only PDF files are allowed.")
        return pdf_files
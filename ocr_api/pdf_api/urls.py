from django.urls import path
from .views import Pdf_Details_PCL,Pdf_Details_LOA,JsonDataView,display_pdf,save_pdf,PdfUploadView,upload_pdf_view,Pdf_Details_RAC,Pdf_Details_LO,Pdf_Details_APP,Pdf_Details_PCL_filepath

urlpatterns = [
    path('upload_pdf/', upload_pdf_view, name='upload_pdf'),

    #path('upload_pdf/<str:pdf_name>/', PdfUploadView.as_view(), name='upload_pdf'),

    #PCL file path
    #path('pdf_details_pcl_path/<path:pdf_path>/', Pdf_Details_PCL_filepath.as_view(), name='pdf_details_path'),


    #PCL
    path('pdf_details_pcl/<str:pdfname>/', Pdf_Details_PCL.as_view(), name='pdf_details'),

    #LOA
    path('pdf_details_loa/<str:pdfname>/', Pdf_Details_LOA.as_view(), name='pdf_details'),

    #RAC
    path('pdf_details_rac/<str:pdfname>/', Pdf_Details_RAC.as_view(), name='pdf_details'),

    #LO
    path('pdf_details_lo/<str:pdfname>/', Pdf_Details_LO.as_view(), name='pdf_details'),

    #LO
    path('pdf_details_app/<str:pdfname>/', Pdf_Details_APP.as_view(), name='pdf_details'),

    #path('json_data/',JsonDataView.as_view(),name="json-data"),
    path('display_pdf/', display_pdf, name='display_pdf'),
    path('save_pdf/<str:filename>/', save_pdf, name='save_pdf'),


    # Add other URL patterns here if needed
]
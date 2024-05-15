from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import View
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from .openai_main import *
import json
from .models import PdfFile
from django.conf import settings
from django.http import HttpResponse
#from django.core.files.base import File
from django.core.files import File
from django.http import FileResponse
from .forms import PdfUploadForm
import logging
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
load_dotenv()

def upload_to_s3(file_obj, folder):
    s3 = boto3.client('s3', aws_access_key_id=os.getenv("aws_access_key_id"), aws_secret_access_key=os.getenv("aws_secret_access_key"))
    bucket_name = 'lcmbluparrot'
    key = f'{folder}/{file_obj.name}'  # Use folder name to construct S3 key

    s3.upload_fileobj(file_obj, bucket_name, key)


def upload_pdf_view(request):
    if request.method == 'POST':
        if 'pcl_submit' in request.POST:
            pcl_file = request.FILES.get('pcl_pdf_file')
            if pcl_file:
                upload_to_s3(pcl_file, 'pcl')
            return JsonResponse({'message': 'PCL PDF uploaded successfully'})
        elif 'loa_submit' in request.POST:
            loa_file = request.FILES.get('loa_pdf_file')
            if loa_file:
                upload_to_s3(loa_file, 'loa')
            return JsonResponse({'message': 'LOA PDF uploaded successfully'})
        elif 'rac_submit' in request.POST:
            rac_file = request.FILES.get('rac_pdf_file')
            if rac_file:
                upload_to_s3(rac_file, 'rac')
            return JsonResponse({'message': 'RAC PDF uploaded successfully'})
        elif 'app_submit' in request.POST:
            app_file = request.FILES.get('app_pdf_file')
            if app_file:
                upload_to_s3(app_file, 'app')
            return JsonResponse({'message': 'APP PDF uploaded successfully'})
        elif 'lo_submit' in request.POST:
            lo_file = request.FILES.get('lo_pdf_file')
            if lo_file:
                upload_to_s3(lo_file, 'lo')
            return JsonResponse({'message': 'LO  PDF uploaded successfully'})
        
        # Add more conditions for other submit buttons and file upload sections if needed
        
    return render(request,"upload_pdf.html",{'error': 'Invalid request'}, status=400)    
 








    # if request.method == 'POST' and request.FILES.getlist('pdf_files'):
    #     pdf_files = request.FILES.getlist('pdf_files')
    #     file_folder = 'MY PDF'  # Folder to save PDF files
    #     if not os.path.exists(file_folder):
    #         os.makedirs(file_folder)
    #     for pdf_file in pdf_files:
    #         file_path = os.path.join(file_folder, pdf_file.name)
    #         with open(file_path, 'wb') as destination:
    #             for chunk in pdf_file.chunks():
    #                 destination.write(chunk)
    #     return JsonResponse({'message': 'PDF files uploaded successfully'})
    # return render(request, 'upload_pdf.html')


class PdfUploadView(APIView):
    # def get(self, request, pdf_name):
    #     # Handle GET requests here, if needed
    #     # For example, you might render a template with a form for file upload
    #     return  render(request,"upload_pdf.html")
        # pass

    def post(self, request, pdf_name):
        form = PdfUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_files = form.cleaned_data['pdf_files']
            file_folder = 'PDF'  # Folder to save PDF files
            pdf_folder_path = os.path.join(os.getcwd(), file_folder)
            if not os.path.exists(pdf_folder_path):
                os.makedirs(pdf_folder_path)
            for pdf_file in pdf_files:
                file_path = os.path.join(pdf_folder_path, pdf_name + '_' + pdf_file.name)
                with open(file_path, 'wb') as destination:
                    for chunk in pdf_file.chunks():
                        destination.write(chunk)
            return JsonResponse({'message': 'PDF files uploaded successfully'})
        else:
            return JsonResponse({'error': form.errors}, status=400)

class JsonDataView(APIView):
    def get(self, request):
        json_data = {}
        json_folder = r'E:\Blueparrot\ocr main\json_pcl_openai(new format)'  # Update the directory path
        try:
            for filename in os.listdir(json_folder):
                print (filename)
                if filename.endswith('.json'):
                    with open(os.path.join(json_folder, filename)) as file:
                        json_data[filename] = json.load(file)
            return Response(json_data)
        except FileNotFoundError:
            return Response({'error': 'Directory not found'}, status=404)
logger = logging.getLogger(__name__) 

###################
class Pdf_Details_PCL_filepath(APIView):
    
    def get(self, request,pdf_path):

         # Sanitize the path to prevent directory traversal attacks
        safe_pdf_path = os.path.normpath(pdf_path)

        # Split the path into directory and file name
        directory, filename = os.path.split(safe_pdf_path)

        # Construct the full file path
        filepath = os.path.join(directory, filename)

        if not os.path.exists(filepath):
            return Response({"error": "PDF file not found"}, status=404)        
      # Determine target folder based on file name pattern
        if 'LOA' in filename:  # Example pattern: LOA
            folder_name = 'LOA'
            target_folder = r'E:\Blueparrot\ocr main\ocr_api\LOA'
        elif 'PCL' in filename:
            folder_name = 'PCL'  # Default folder name if pattern not matched
            target_folder =  r'E:\Blueparrot\ocr main\ocr_api\PCL' # Save in the same folder as MY PDF

        # Creating folder if it doesn't exist
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        # Saving the file to the target folder
        target_filepath = os.path.join(target_folder, filename)
        with open(target_filepath, 'wb') as target_file:
            with open(filepath, 'rb') as source_file:
                target_file.write(source_file.read())
        
        print("saved in the folder")
        logger.info(f"PDF file '{filename}' saved successfully")

        raw_text = get_pdf_text1(filepath)
        if not raw_text:
            return Response({'error': 'Failed to extract text from PDF'}, status=400)
        
        output_text_pcl = generate_answer_PCL(raw_text)
       # output_text_loa = generate_answer_LOA(raw_text)
        if not output_text_pcl :
            return Response({'error': 'Failed to generate answer'}, status=400)    
        print("json text in viewpcl: ",output_text_pcl)
        

        # Parsing JSON content
        try:
            start = output_text_pcl.find('{')
            end = output_text_pcl.rfind('}') + 1
            json_content = output_text_pcl[start:end]
            json_content = json_content.replace("None", "")
            json_content = json_content.replace("null", "")
            d_pcl = eval(json_content)
            logger.info(f"JSON content parsed successfully for PDF '{filename}'")
            return Response(d_pcl)
        except Exception as e:
            logger.exception(f"Error occurred while parsing JSON content for PDF '{filename}': {str(e)}")
            return Response({'error': 'Failed to parse JSON content'}, status=400)




#################

class Pdf_Details_PCL(APIView):
    
    def get(self, request, pdfname):
        # Sanitize pdfname to prevent directory traversal attacks
        safe_pdfname = os.path.basename(pdfname)
        print(safe_pdfname)
        # Specify the S3 bucket name
        bucket_name = 'lcmbluparrot'
        
        # Construct the S3 key for the PDF file in the "PCL" folder
        pcl_key = f'pcl/{safe_pdfname}'

        # Construct the S3 key for the PDF file
        # key = safe_pdfname
        print("i m here")
        try:
            # Initialize the S3 client
            s3 = boto3.client('s3', aws_access_key_id=os.getenv("aws_access_key_id"), aws_secret_access_key=os.getenv("aws_secret_access_key"))
           
            # Check if the file exists in the S3 bucket
            s3.head_object(Bucket=bucket_name, Key=pcl_key)
            print(s3)
            print("not here")
            # If the file exists, proceed with processing
            # Use the appropriate S3 URI if needed (e.g., s3://bucket-name/file.pdf)
            # Assuming get_pdf_text1 function accepts S3 URI for file access
            print("goin")
            file_uri=f's3://{bucket_name}/{pcl_key}'
            raw_text_1 = get_pdf_text_from_s3(bucket_name,pcl_key)

            # Process raw text to generate API response
            output_text_pcl = generate_answer_PCL(raw_text_1)
            print(output_text_pcl)
            # Parsing JSON content
            try:
                 json_content=json.loads(output_text_pcl)
                 return Response(json_content)
                # start = output_text_pcl.find('{')
                # end = output_text_pcl.rfind('}') + 1
                # json_content = output_text_pcl[start:end]
                # json_content = json_content.replace("None", "")
                # json_content = json_content.replace("null", "")
                # d_pcl = eval(json_content)
                # return Response(d_pcl)
            except Exception as e:
                logger.exception(f"Error occurred while parsing JSON content for PDF '{safe_pdfname}': {str(e)}")
                return Response({'error': 'Failed to parse JSON content'}, status=400)
        
        except ClientError as e:
            # If the file does not exist in the S3 bucket, return an error response
            if e.response['Error']['Code'] == '404':
                return Response({"error": "PDF file not found"}, status=404)
            else:
                logger.exception(f"Error occurred while checking file existence in S3 bucket: {str(e)}")
                return Response({'error': 'Failed to process request'}, status=500)

class Pdf_Details_LOA(APIView):
    
    def get(self, request,pdfname):
        # Sanitize pdfname to prevent directory traversal attacks
        safe_pdfname = os.path.basename(pdfname)
        print(safe_pdfname)
        # Specify the S3 bucket name
        bucket_name = 'lcmbluparrot'
        
        # Construct the S3 key for the PDF file in the "PCL" folder
        pcl_key = f'loa/{safe_pdfname}'

        # Construct the S3 key for the PDF file
        # key = safe_pdfname
        print("i m here")
        try:
            # Initialize the S3 client
            s3 = boto3.client('s3', aws_access_key_id=os.getenv("aws_access_key_id"), aws_secret_access_key=os.getenv("aws_secret_access_key"))
           
            # Check if the file exists in the S3 bucket
            s3.head_object(Bucket=bucket_name, Key=pcl_key)
            print(s3)
            print("not here")
            # If the file exists, proceed with processing
            # Use the appropriate S3 URI if needed (e.g., s3://bucket-name/file.pdf)
            # Assuming get_pdf_text1 function accepts S3 URI for file access
            print("goin")
            file_uri=f's3://{bucket_name}/{pcl_key}'
            raw_text_1 = get_pdf_text_from_s3(bucket_name,pcl_key)

            # Process raw text to generate API response
            output_text_pcl = generate_answer_PCL(raw_text_1)
            print(output_text_pcl)
            # Parsing JSON content
            try:
                 json_content=json.loads(output_text_pcl)
                 return Response(json_content)
                # start = output_text_pcl.find('{')
                # end = output_text_pcl.rfind('}') + 1
                # json_content = output_text_pcl[start:end]
                # json_content = json_content.replace("None", "")
                # json_content = json_content.replace("null", "")
                # d_pcl = eval(json_content)
                # return Response(d_pcl)
            except Exception as e:
                logger.exception(f"Error occurred while parsing JSON content for PDF '{safe_pdfname}': {str(e)}")
                return Response({'error': 'Failed to parse JSON content'}, status=400)
        
        except ClientError as e:
            # If the file does not exist in the S3 bucket, return an error response
            if e.response['Error']['Code'] == '404':
                return Response({"error": "PDF file not found"}, status=404)
            else:
                logger.exception(f"Error occurred while checking file existence in S3 bucket: {str(e)}")
                return Response({'error': 'Failed to process request'}, status=500)
   

class Pdf_Details_RAC(APIView):
    
    def get(self, request,pdfname):
        # Sanitize pdfname to prevent directory traversal attacks
        safe_pdfname = os.path.basename(pdfname)
        print(safe_pdfname)
        # Specify the S3 bucket name
        bucket_name = 'lcmbluparrot'
        
        # Construct the S3 key for the PDF file in the "PCL" folder
        pcl_key = f'rac/{safe_pdfname}'

        # Construct the S3 key for the PDF file
        # key = safe_pdfname
        print("i m here")
        try:
            # Initialize the S3 client
            s3 = boto3.client('s3', aws_access_key_id=os.getenv("aws_access_key_id"), aws_secret_access_key=os.getenv("aws_secret_access_key"))
           
            # Check if the file exists in the S3 bucket
            s3.head_object(Bucket=bucket_name, Key=pcl_key)
            print(s3)
            print("not here")
            # If the file exists, proceed with processing
            # Use the appropriate S3 URI if needed (e.g., s3://bucket-name/file.pdf)
            # Assuming get_pdf_text1 function accepts S3 URI for file access
            print("goin")
            file_uri=f's3://{bucket_name}/{pcl_key}'
            raw_text_1 = get_pdf_text_from_s3(bucket_name,pcl_key)

            # Process raw text to generate API response
            output_text_pcl = generate_answer_PCL(raw_text_1)
            print(output_text_pcl)
            # Parsing JSON content
            try:
                 json_content=json.loads(output_text_pcl)
                 return Response(json_content)
                # start = output_text_pcl.find('{')
                # end = output_text_pcl.rfind('}') + 1
                # json_content = output_text_pcl[start:end]
                # json_content = json_content.replace("None", "")
                # json_content = json_content.replace("null", "")
                # d_pcl = eval(json_content)
                # return Response(d_pcl)
            except Exception as e:
                logger.exception(f"Error occurred while parsing JSON content for PDF '{safe_pdfname}': {str(e)}")
                return Response({'error': 'Failed to parse JSON content'}, status=400)
        
        except ClientError as e:
            # If the file does not exist in the S3 bucket, return an error response
            if e.response['Error']['Code'] == '404':
                return Response({"error": "PDF file not found"}, status=404)
            else:
                logger.exception(f"Error occurred while checking file existence in S3 bucket: {str(e)}")
                return Response({'error': 'Failed to process request'}, status=500)

    
class Pdf_Details_LO(APIView):
    
    def get(self, request,pdfname):
        # Sanitize pdfname to prevent directory traversal attacks
        safe_pdfname = os.path.basename(pdfname)
        print(safe_pdfname)
        # Specify the S3 bucket name
        bucket_name = 'lcmbluparrot'
        
        # Construct the S3 key for the PDF file in the "PCL" folder
        pcl_key = f'lo/{safe_pdfname}'

        # Construct the S3 key for the PDF file
        # key = safe_pdfname
        print("i m here")
        try:
            # Initialize the S3 client
            s3 = boto3.client('s3', aws_access_key_id=os.getenv("aws_access_key_id"), aws_secret_access_key=os.getenv("aws_secret_access_key"))
           
            # Check if the file exists in the S3 bucket
            s3.head_object(Bucket=bucket_name, Key=pcl_key)
            print(s3)
            print("not here")
            # If the file exists, proceed with processing
            # Use the appropriate S3 URI if needed (e.g., s3://bucket-name/file.pdf)
            # Assuming get_pdf_text1 function accepts S3 URI for file access
            print("goin")
            file_uri=f's3://{bucket_name}/{pcl_key}'
            raw_text_1 = get_pdf_text_from_s3(bucket_name,pcl_key)

            # Process raw text to generate API response
            output_text_pcl = generate_answer_PCL(raw_text_1)
            print(output_text_pcl)
            # Parsing JSON content
            try:
                 json_content=json.loads(output_text_pcl)
                 return Response(json_content)
                # start = output_text_pcl.find('{')
                # end = output_text_pcl.rfind('}') + 1
                # json_content = output_text_pcl[start:end]
                # json_content = json_content.replace("None", "")
                # json_content = json_content.replace("null", "")
                # d_pcl = eval(json_content)
                # return Response(d_pcl)
            except Exception as e:
                logger.exception(f"Error occurred while parsing JSON content for PDF '{safe_pdfname}': {str(e)}")
                return Response({'error': 'Failed to parse JSON content'}, status=400)
        
        except ClientError as e:
            # If the file does not exist in the S3 bucket, return an error response
            if e.response['Error']['Code'] == '404':
                return Response({"error": "PDF file not found"}, status=404)
            else:
                logger.exception(f"Error occurred while checking file existence in S3 bucket: {str(e)}")
                return Response({'error': 'Failed to process request'}, status=500)

    
class Pdf_Details_APP(APIView):
    
    def get(self, request,pdfname):
         # Sanitize pdfname to prevent directory traversal attacks
        safe_pdfname = os.path.basename(pdfname)
        print(safe_pdfname)
        # Specify the S3 bucket name
        bucket_name = 'lcmbluparrot'
        
        # Construct the S3 key for the PDF file in the "PCL" folder
        pcl_key = f'app/{safe_pdfname}'

        # Construct the S3 key for the PDF file
        # key = safe_pdfname
        print("i m here")
        try:
            # Initialize the S3 client
            s3 = boto3.client('s3', aws_access_key_id=os.getenv("aws_access_key_id"), aws_secret_access_key=os.getenv("aws_secret_access_key"))
            
            # Check if the file exists in the S3 bucket
            s3.head_object(Bucket=bucket_name, Key=pcl_key)
            print(s3)
            print("not here")
            # If the file exists, proceed with processing
            # Use the appropriate S3 URI if needed (e.g., s3://bucket-name/file.pdf)
            # Assuming get_pdf_text1 function accepts S3 URI for file access
            print("goin")
            file_uri=f's3://{bucket_name}/{pcl_key}'
            raw_text_1 = get_pdf_text_from_s3(bucket_name,pcl_key)

            # Process raw text to generate API response
            output_text_pcl = generate_answer_PCL(raw_text_1)
            print(output_text_pcl)
            # Parsing JSON content
            try:
                 json_content=json.loads(output_text_pcl)
                 return Response(json_content)
                # start = output_text_pcl.find('{')
                # end = output_text_pcl.rfind('}') + 1
                # json_content = output_text_pcl[start:end]
                # json_content = json_content.replace("None", "")
                # json_content = json_content.replace("null", "")
                # d_pcl = eval(json_content)
                # return Response(d_pcl)
            except Exception as e:
                logger.exception(f"Error occurred while parsing JSON content for PDF '{safe_pdfname}': {str(e)}")
                return Response({'error': 'Failed to parse JSON content'}, status=400)
        
        except ClientError as e:
            # If the file does not exist in the S3 bucket, return an error response
            if e.response['Error']['Code'] == '404':
                return Response({"error": "PDF file not found"}, status=404)
            else:
                logger.exception(f"Error occurred while checking file existence in S3 bucket: {str(e)}")
                return Response({'error': 'Failed to process request'}, status=500)

         # Convert the output texts to dictionaries
        # d_pcl = eval(output_text_pcl)
        # d_loa = eval(output_text_loa)

        
        # return Response(d_combined)
    
        # if output_text_pcl is not None:
        #                 start = output_text_pcl.find('{')
        #                 end = output_text_pcl.rfind('}') + 1
        #                 json_content = output_text_pcl[start:end]
        #                 json_content = json_content.replace("None", "")
        #                 json_content = json_content.replace("null", "")
        #                 d_pcl = eval(json_content)
        #                 print("d in pcl : ",d_pcl)
        # if output_text_loa is not None:
        #                 start = output_text_loa.find('{')
        #                 end = output_text_loa.rfind('}') + 1
        #                 json_content = output_text_loa[start:end]
        #                 json_content = json_content.replace("None", "")
        #                 json_content = json_content.replace("null", "")
        #                 d_loa = eval(json_content)
        #                 print("d in loa : ",d_loa) 
        # # Merge dictionaries
        # # Combine dictionaries, giving preference to values from the first prompt
        # d_combined = {}
        # for key_pcl, value_pcl in d_pcl.items():
        #     for key_loa, value_loa in d_loa.items():
        #         if value_pcl == value_loa:
        #             d_combined[key_pcl] = value_pcl
        #             break
        #     else:
        #         d_combined[key_pcl] = value_pcl
        
        # # Add values from the second prompt that are not in the first
        # for key_loa, value_loa in d_loa.items():
        #     if value_loa not in d_pcl.values():
        #         d_combined[key_loa] = value_loa
        #     print("Combined dictionary:", d_combined)
    
        
    
def getpage(request):
     return render(request,"download_pdf.html")


def display_pdf(request):
    pdf_folder = r'E:\Blueparrot\ocr main\ocr_api\PCL'
    pdf_files=[]
    for filename in os.listdir(pdf_folder):
        
        if filename.endswith('.pdf'):
            filepath = os.path.join(pdf_folder, filename)      
            with open(filepath, 'rb') as f:
                #django_file = File(f)
                pdf_file = f.read()
                print("********",filepath)
                print("----",filename)
            # Save the PDF file to the database
            # pdf_file_obj = PdfFile(file=pdf_file)
            
            # pdf_file_obj.save()
            pdf_files.append({'filename':filename,'filepath':filepath})
    #return render(request, 'download_pdf.html', {'pdf_files': PdfFile.objects.all()})
    return render(request, 'download_pdf.html', {'pdf_files': pdf_files})

def save_pdf(request, filename):
    # pdf_folder = r'E:\Blueparrot\ocr main\ocr_api\pdfs'
    pdf_path = os.path.join('E:\Blueparrot\ocr main\ocr_api\pdfs', filename)
    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as pdf_file:
            try:
                return FileResponse(open(pdf_path, 'rb'), as_attachment=True)
            except Exception as e:
                return HttpResponse("Error occurred while opening the file: {}".format(str(e)), status=500)

    else:
        # Handle file not found
        return HttpResponse("File not found", status=404)

# # Create your views here.

# Import the required libraries
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import AnalyzeResults
#from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import sys
import os
import time
from dotenv import load_dotenv


load_dotenv()

cv_key = os.getenv("cv_key")
# Change the cv_endpoint below to your endpoint.
cv_endpoint =os.getenv("cv_endpoint")

# Change the cv_endpoint below to your endpoint.


# Store as enivonmental variables
os.environ['COMPUTER_VISION_SUBSCRIPTION_KEY'] = cv_key
os.environ['COMPUTER_VISION_ENDPOINT'] = cv_endpoint
print(cv_endpoint)

# Get your Computer Vision subscription key from your environment variable.
if 'COMPUTER_VISION_SUBSCRIPTION_KEY' in os.environ:
    subscription_key = os.environ['COMPUTER_VISION_SUBSCRIPTION_KEY']
else:
    print("\nSet the COMPUTER_VISION_SUBSCRIPTION_KEY environment variable.\n**Restart your shell or IDE for changes to take effect.**")
    sys.exit()

# Get your Computer Vision endpoint from your environment variable.
if 'COMPUTER_VISION_ENDPOINT' in os.environ:
    endpoint = os.environ['COMPUTER_VISION_ENDPOINT']
else:
    print("\nSet the COMPUTER_VISION_ENDPOINT environment variable.\n**Restart your shell or IDE for changes to take effect.**")
    sys.exit()

# Authenticate with Azure Cognitive Services.
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

from pdf2image import convert_from_path
from PIL import Image
import tempfile

def get_pdf_files_in_folder(folder_path):
    pdf_files = []
    for file in os.listdir(folder_path):
        if file.lower().endswith(".pdf") :
            pdf_files.append(os.path.join(folder_path, file))
    return pdf_files

folder_name = "LOA"
input_pdf_paths = get_pdf_files_in_folder(os.path.join(os.getcwd(), folder_name))

# Replace double backslashes with single backslashes
#input_pdf_paths = [path.replace('\\\\', '\\') for path in input_pdf_paths]
input_pdf_paths

# from reportlab.pdfgen import canvas
# from reportlab.lib.units import inch
# import math

# def save_as_pdf(file_name,azure_ocr_response):
#     # Create a PDF file
#     c = canvas.Canvas(f"{file_name}.pdf", pagesize=(azure_ocr_response['width'],azure_ocr_response['height']))
#     # c = canvas.Canvas(f"{file_name}.pdf", pagesize=(8.5*inch,11*inch)) # The subsequent output pdf has contents overlapping and out of bounds. Rejected.
    
#     # Extract data from Azure OCR API response
#     for word in azure_ocr_response['lines']:
#         x1, y1, x2, y2, x3, y3, x4, y4 = word['boundingBox']
#         # Calculate the center of the bounding box
#         x_center = (x1 + x2 + x3 + x4) / 4
#         y_center = azure_ocr_response["height"] - (y1 + y2 + y3 + y4) / 4
        
#         # Apply rotation to the bounding box coordinates
#         '''
#         The subsequent output pdf has contents slightly overlapping but a lot of text was found to be out of bounds. Rejected.
#         '''
#         # x_rotated = x_center * math.cos(azure_ocr_response["angle"]) - y_center * math.sin(azure_ocr_response["angle"])
#         # y_rotated = x_center * math.sin(azure_ocr_response["angle"]) + y_center * math.cos(azure_ocr_response["angle"])
        

        
#         # Draw the text on the PDF canvas
#         c.drawString(x_center, y_center, word["text"])


#     c.showPage()  # Add a new page for the next set of text

#     c.save()  # Save the PDF file    

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import math

def save_as_pdf(file_name, pages):
    uploads_folder = 'uploads'
    if not os.path.exists(uploads_folder):
        os.makedirs(uploads_folder)
    file_path = os.path.join(uploads_folder, f"{file_name}.pdf")
    c = canvas.Canvas(file_path)
    for lines, bbs, pw, ph, angle in pages:  
        print(angle)
        c.setPageSize((pw,ph))
        for line, bb in zip(lines, bbs):
            x1, y1, x2, y2, x3, y3, x4, y4 = bb
            cx = (x1 + x2 + x3 + x4) / 4
            cy = ph - ((y1 + y2 + y3 + y4) / 4)  # Adjust y-coordinate based on page height
            angle_rad = math.radians(angle)
            x = cx * math.cos(angle_rad) - cy * math.sin(angle_rad)
            y = cx * math.sin(angle_rad) + cy * math.cos(angle_rad)
            c.drawCentredString(x, y, line)
        c.showPage()  # Add a new page for the next set of text
    c.save()
    print(f"PDF file saved to {file_path}")

# def ocr_main():
#     api_calls=0
#     for path in input_pdf_paths[-6:-5]:
#         name = path.split('/')[-1].split('.')[0]
#         print(name)
#         images = convert_from_path(path)
#         page = []
        
#         for raw_image in images:
#             # Save the image to a temporary file
#             with tempfile.NamedTemporaryFile(dir=os.getcwd(), suffix='.jpg', delete=False) as temp_image_file:
#                 raw_image.save(temp_image_file, format='JPEG')

#             # print(temp_image_file.name)
#             # Call API with image and raw response
#             with open(temp_image_file.name, 'rb') as image_fd:
#                 read_response = computervision_client.read_in_stream(image_fd, raw=True)
#             api_calls+=1
#             os.remove(os.path.join(os.getcwd(),temp_image_file.name))
#             # Get the operation location (URL with ID as last appendage)
#             read_operation_location = read_response.headers["Operation-Location"]

#             # Take the ID off and use to get results
#             operation_id = read_operation_location.split("/")[-1]
            
#             # Call the "GET" API and wait for the retrieval of the results.
#             while True:
#                 read_result = computervision_client.get_read_result(operation_id)
#                 api_calls+=1
#                 print(f"API_ CALLS: {api_calls}")
#                 if read_result.status.lower() not in ['notstarted', 'running']:
#                     break
#                 print('Waiting for result...')
#                 time.sleep(10)
            
#             # Print results, line by line
#             if read_result.status == OperationStatusCodes.succeeded:
#                 bb = []
#                 lines = []
#                 for text_result in read_result.analyze_result.read_results:
#                     x = AnalyzeResults.serialize(text_result)
#                     pw = x['width']
#                     ph = x['height']
#                     angle = x['angle']
#                     for l in x['lines']:
#                         # print(x)
#                         bb.append(l['boundingBox'])
#                         lines.append(l['text'])
#             page.append([lines,bb,pw,ph,angle])
#         save_as_pdf(name, page)
#     return page
        
        
                 

# x = ocr_main()


from pdf2image import convert_from_path


def ocr_main():
    api_calls = 0
    all_pages = []  # Initialize a list to store all pages
    for path in input_pdf_paths[0:1]:
        name = path.split('\\')[-1].split('.')[0]
        # print(name)
        print("path",path)
        images = convert_from_path(path)
        page = []

        for raw_image in images:
            # Save the image to a temporary file
            with tempfile.NamedTemporaryFile(dir=os.getcwd(), suffix='.jpg', delete=False) as temp_image_file:
                raw_image.save(temp_image_file, format='JPEG')
            print('i m here')
            # Call API with image and raw response
            with open(temp_image_file.name, 'rb') as image_fd:
                
                read_response = computervision_client.read_in_stream(image_fd, raw=True)
                print(f":Response: {read_response.response.status_code}")
            api_calls += 1
            os.remove(os.path.join(os.getcwd(), temp_image_file.name))
            # Get the operation location (URL with ID as last appendage)
            read_operation_location = read_response.headers["Operation-Location"]

            # Take the ID off and use to get results
            operation_id = read_operation_location.split("/")[-1]
            print("rol : ",read_operation_location)

            # Call the "GET" API and wait for the retrieval of the results.
            while True:
                read_result = computervision_client.get_read_result(operation_id)
                api_calls += 1
                print(f"API_ CALLS: {api_calls}")
                if read_result.status.lower() not in ['notstarted', 'running']:
                    break
                print('Waiting for result...')
                time.sleep(6)

            # Print results, line by line
            if read_result.status == OperationStatusCodes.succeeded:
                bb = []
                lines = []
                for text_result in read_result.analyze_result.read_results:
                    x = AnalyzeResults.serialize(text_result)
                    pw = x['width']
                    ph = x['height']
                    angle = x['angle']
                    for l in x['lines']:
                        bb.append(l['boundingBox'])
                        lines.append(l['text'])
                page.append([lines, bb, pw, ph, angle])
        
        # Append the page to the list of all pages
        all_pages.append(page)

        # Save the current page
        save_as_pdf(name, page)
    
    # Return all pages
    return all_pages


x = ocr_main()
x
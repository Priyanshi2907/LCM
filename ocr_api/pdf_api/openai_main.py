import os
import google.generativeai as genai
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_google_genai import HarmBlockThreshold
# from langchain_google_genai import HarmCategory
# from langchain.chains.question_answering import load_qa_chain
from langchain_community.document_loaders import PyPDFLoader
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
# from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import openai
from openai import OpenAI
import os 
import time
import json
from spire.doc.common import *
import warnings
import re
warnings.filterwarnings("ignore")
from deep_translator import GoogleTranslator
#from translate import Translator
import tiktoken
from langchain_community.document_loaders import TextLoader
import pdfx
import ocrmypdf
import boto3
from botocore.exceptions import ClientError
from langchain_community.document_loaders import PyPDFLoader
import tempfile
import PyPDF2






load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
api_key=os.environ['OPENAI_API_KEY']
print(api_key)

def save_uploaded_pdf_to_directory(file_path):
    file_name = os.path.basename(file_path)
    if file_name.lower().endswith('.pdf'):
        directory_name = "pdf"
        if not os.path.exists(directory_name):
            file_path1 = os.path.join(directory_name, file_name)
            os.makedirs(directory_name)
            with open(file_path, 'rb') as fsrc:
                with open(file_path1, 'wb') as fdst:
                    fdst.write(fsrc.read())
            return file_path1
        else:
            file_path1 = os.path.join(directory_name, file_name)
            with open(file_path, 'rb') as fsrc:
                with open(file_path1, 'wb') as fdst:
                    fdst.write(fsrc.read())
            return file_path1
    elif file_name.lower().endswith('.xls') or file_name.lower().endswith('.xlsx'):
        directory_name2 = "excel"
        from spire.xls import Workbook, FileFormat
        if not os.path.exists(directory_name2):
            file_path2 = os.path.join(directory_name2, file_name)
            os.makedirs(directory_name2)
            with open(file_path, 'rb') as fsrc:
                with open(file_path2, 'wb') as fdst:
                    fdst.write(fsrc.read())
            workbook = Workbook()
            workbook.LoadFromFile(file_path2)
            pdf_path1 = file_path2.replace(os.path.splitext(file_path2)[1], '.pdf')
            workbook.SaveToFile(pdf_path1, FileFormat.PDF)
            workbook.Dispose()
            return pdf_path1
        else:
            file_path2 = os.path.join(directory_name2, file_name)
            with open(file_path, 'rb') as fsrc:
                with open(file_path2, 'wb') as fdst:
                    fdst.write(fsrc.read())
            workbook = Workbook()
            workbook.LoadFromFile(file_path2)
            pdf_path1 = file_path2.replace(os.path.splitext(file_path2)[1], '.pdf')
            workbook.SaveToFile(pdf_path1, FileFormat.PDF)
            workbook.Dispose()
            return pdf_path1
    elif file_name.lower().endswith('.ppt') or file_name.lower().endswith('.pptx'):
        from spire.presentation import Presentation, FileFormat
        directory_name3 = "ppt"
        if not os.path.exists(directory_name3):
            file_path3 = os.path.join(directory_name3, file_name)
            os.makedirs(directory_name3)
            with open(file_path, 'rb') as fsrc:
                with open(file_path3, 'wb') as fdst:
                    fdst.write(fsrc.read())
            presentation = Presentation()
            presentation.LoadFromFile(file_path3)
            pdf_path2 = file_path3.replace(os.path.splitext(file_path3)[1], '.pdf')
            presentation.SaveToFile(pdf_path2, FileFormat.PDF)
            presentation.Dispose()
            return pdf_path2
        else:
            file_path3 = os.path.join(directory_name3, file_name)
            with open(file_path, 'rb') as fsrc:
                with open(file_path3, 'wb') as fdst:
                    fdst.write(fsrc.read())
            presentation = Presentation()
            presentation.LoadFromFile(file_path3)
            pdf_path2 = file_path3.replace(os.path.splitext(file_path3)[1], '.pdf')
            presentation.SaveToFile(pdf_path2, FileFormat.PDF)
            presentation.Dispose()
            return pdf_path2
    else:
        directory_name1 = "word"
        from spire.doc import Document, FileFormat
        if not os.path.exists(directory_name1):
            file_path4 = os.path.join(directory_name1, file_name)
            os.makedirs(directory_name1)
            with open(file_path, 'rb') as fsrc:
                with open(file_path4, 'wb') as fdst:
                    fdst.write(fsrc.read())
            document = Document()
            document.LoadFromFile(file_path4)
            pdf_path = file_path4.replace(os.path.splitext(file_path4)[1], '.pdf')
            document.SaveToFile(pdf_path, FileFormat.PDF)
            document.Close()
            return pdf_path
        else:
            file_path4 = os.path.join(directory_name1, file_name)
            with open(file_path, 'rb') as fsrc:
                with open(file_path4, 'wb') as fdst:
                    fdst.write(fsrc.read())
            document = Document()
            document.LoadFromFile(file_path4)
            pdf_path = file_path4.replace(os.path.splitext(file_path4)[1], '.pdf')
            document.SaveToFile(pdf_path, FileFormat.PDF)
            document.Close()
            return pdf_path

def get_path(file_path):
    file_name = os.path.basename(file_path)    
    if file_name.lower().endswith('.pdf'):
        directory_name = "pdf"
        file_path = os.path.join(directory_name, file_name)
        return file_path
    elif file_name.lower().endswith('.xls') or file_name.lower().endswith('.xlsx'):
        directory_name2 = "excel"
        file_path2 = os.path.join(directory_name2, file_name)
        pdf_path1 = file_path2.replace(os.path.splitext(file_path2)[1], '.pdf')
        return pdf_path1
    elif file_name.lower().endswith('.ppt') or file_name.lower().endswith('.pptx'):
        directory_name3 = "ppt"
        file_path3 = os.path.join(directory_name3, file_name)
        pdf_path2 = file_path3.replace(os.path.splitext(file_path3)[1], '.pdf')
        return pdf_path2
    else:
        directory_name1 = "word"
        file_path1 = os.path.join(directory_name1, file_name)
        pdf_path = file_path1.replace(os.path.splitext(file_path1)[1], '.pdf')
        return pdf_path

    
        
def calculate_similarity(output_text, document_text):
  vectorizer = CountVectorizer().fit([output_text, document_text])
  X =vectorizer.transform([output_text, document_text])
  similarity = cosine_similarity(X[0], X[1])
  return similarity[0][0]

def get_pdf_text(path):
    pdf_loader = PyPDFLoader(path)
    pages = pdf_loader.load_and_split()
    return pages

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def trim_pages(pages, encoding_name, max_tokens):
    tokens_count = num_tokens_from_string(str(pages), encoding_name)
    
    while tokens_count > max_tokens and len(pages) > 0:
        # Remove the last page and recalculate the token count
        pages.pop()
        tokens_count = num_tokens_from_string(str(pages), encoding_name)
    
    return pages




def get_pdf_text1(file_path):
    print("i am in get_pdf_text")
    path = save_uploaded_pdf_to_directory(file_path)
   # ocrmypdf.ocr(path,path, deskew=True,force_ocr=True,language="eng",pdfa_image_compression="lossless",use_threads=True)
    pdf_loader = PyPDFLoader(path)
    pages = pdf_loader.load_and_split()
    if len(pages)==0:
        ocrmypdf.ocr(path,path, deskew=True,force_ocr=True,language="eng",pdfa_image_compression="lossless",use_threads=True)
        pdf_loader1 = PyPDFLoader(path)
        pages = pdf_loader1.load_and_split()
    return pages

def get_text_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        return text


def save_json_to_directory(file_path, text,safe=True):
    file_name = os.path.basename(file_path)    
    file_name = os.path.splitext(file_name)[0] + ".json"
    directory_name = "json_pcl_openai(new format)" 
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    file_path = os.path.join(directory_name, file_name)
    with open(file_path, 'w') as file:
        json.dump(text, file,indent=5)
    print("The contract details have been saved as a JSON file in the 'json' directory.")

def convert_currency_format(value):
    currency1 = ("RM", "INR", "$")
    for currency in currency1:
        if value and currency in value:
            currency_index = value.find(currency)
            amount = value[currency_index + len(currency):].replace(",", "").strip()
            return {"currency": currency, "value": float(amount)}
        
def remove_parentheses_contents(d):
    new_dict = {}
    for key, value in d.items():
        new_key = re.sub(r"\(.*?\)", "", key).strip()
        
        # Ensuring that the values that are not strings are not processed
        if isinstance(value, str):
            new_value = re.sub(r"\(.*?\)", "", value).strip()
        else:
            new_value = value
        
        new_dict[new_key] = new_value
    return new_dict


def translate_dict(dictionary):
    translated_dict = {}

    for key, value in dictionary.items():
        translated_key =  GoogleTranslator(source='auto', target='en').translate(key) 
        translated_value =  GoogleTranslator(source='auto', target='en').translate(value) 
        translated_dict[translated_key] = translated_value
    return translated_dict

def get_pdf_text_from_s3(bucket_name, pcl_key):
    s3 = boto3.client('s3', aws_access_key_id=os.getenv("aws_access_key_id"), aws_secret_access_key=os.getenv("aws_secret_access_key"))
    
    # Download the PDF file from S3 to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        s3.download_fileobj(bucket_name, pcl_key, temp_file)
        temp_file_path = temp_file.name
    
    # Call the function to process the PDF text
    raw_text = get_pdf_text2(temp_file_path)
    
    # Delete the temporary file
    os.remove(temp_file_path)
    
    return raw_text
def get_pdf_text2(file_path):
    raw_text = ""
    with open(file_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_number in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_number]
            raw_text += page.extract_text()
    return raw_text
def parse_s3_uri(file_uri):
    # Remove the 's3://' prefix
    uri = file_uri[5:]
    
    # Split the URI into bucket name and key
    parts = uri.split('/')
    bucket_name = parts[0]
    key = '/'.join(parts[1:])
    
    return bucket_name, key

def download_file_from_s3(bucket_name, key):
    # Initialize the S3 client
    s3 = boto3.client('s3', aws_access_key_id=os.getenv("aws_access_key_id"), aws_secret_access_key=os.getenv("aws_secret_access_key"))
    
    # Download the file from S3
    try:
        response = s3.get_object(Bucket=bucket_name, Key=key)
        file_bytes = response['Body'].read()
        return file_bytes
    except ClientError as e:
        raise RuntimeError(f"Failed to download file from S3: {e}")

safety_settings = [
    {
      "category": "HARM_CATEGORY_HARASSMENT",
      "threshold": "BLOCK_NONE"
    },
    {
      "category": "HARM_CATEGORY_HATE_SPEECH",
      "threshold": "BLOCK_NONE"
    },
    {
      "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
      "threshold": "BLOCK_NONE"
    },
    {
      "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
      "threshold": "BLOCK_NONE"
    }
    ]       
#PCL
def generate_answer_PCL(url_content):
    keys = """Date,Ref No., Relationship Manager,Lead, Facility, 
    Under Applicant Information: [ Applicant (with Registration No), Business Entity, Name of Directors, Personal Guarantors, Corporate Guarantors, Any adverse findings from bankruptcy, litigation and summonses searches?, 
    Findings, Core Business, Number of Years in Operation, Total Number and Value of Contracts Secured in the Past: Government, GSL, Others ], 
    Under Purpose of Facilities: [ Purpose, Supporting documents], Under Contract Details: [ Contract Awarder, Contracted Services, Nature of Contract, Collection Via, Contract Description, Tenure of Contract, Delivery Period, Contract Value ], 
    Under Proposed Facility: [ Total Purchase Order Amount (for supply of goods), Advance Amount, Proposed Limit, Credit Period, Grace Period, Administration Charge, Profit Rate Tier 1, Profit Rate Tier 2 Pre-Financing, Profit Rate Tier 2 Factoring, Processing Fee, Letter of Undertaking Charge, Late Payment Charge"""
    keys1 = """Under Contract Details: [ Contract Awarder, Contracted Services, Nature of Contract, Collection Via, Contract Description, Tenure of Contract, Delivery Period, Contract Value ] 
    in form of json format strictly with no such symbol: ``` or ` and no text before or after, just need the dictionary NOTHING ELSE STRICTLY. """


    openai.api_key = api_key
    client = OpenAI()
    response = client.chat.completions.create(
            model="gpt-4-0125-preview",
              messages=[
            {
                "role": "user",
                "content": f"extract the following {keys1}  based on the following content and the understanding of the content: {url_content}\nAnswer: , Ensure 100% accuracy and answer should strictly and always be in JSON format. In case multiple answers are ticked, then strictly and necessarily give all the ticked options. If for a category/parameter there are multiple options that are ticked, then strictly give all the ticked (only √) options(only of unicode \u221a). Do not miss or omit any information."        
            },
            {
                "role": "system",
                "content": "Based on the content found in the URL you provided, I can give you specific and accurate answers"
            },
            ],
            temperature=0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
    ans = response.choices[0].message.content
    return ans

#LOA/SST
def generate_answer_LOA(url_content):
    openai.api_key =api_key
    client = OpenAI()
    response = client.chat.completions.create(
            model="gpt-4-0125-preview",
              messages=[
            {
                "role": "user",
                "content": f"extract these points from the document:Company/Receipent Name (Or Organization recieving the contract/ the organization for whom the letter is addressed to) , Contract awarder/Sender name (Or Organization awarding the contract/sending the letter), Contract Title (Or Subject of the letter whichever applicable) , Document Ref No. (Mentioned in the document as Our Ref./Our Reference), Contract/Tender No. or No.Tender/Contract (Whichever applicable) ,  Contract Start Date (As mentioned in the letter implicitly), Contract End Date  (As mentioned in the letter implicitly), Tenure of Contract or Contract Duration (As mentioned in the letter implicitly), Contract Price or Contract Value or Purchase Price or Estimated Contract Value or Contract Sum or Service Price (whichever applicable) based on the following content and the understanding og the content: {url_content}\nAnswer: , Ensure 100% accuracy and answer should strictly and always be in JSON format. If information is not mentioned in the url content, then simply state Information Not Availble."            
            },
            {
                "role": "system",
                "content": "Based on the content found in the URL you provided, I can give you specific answers"
            },
            ],
            temperature=0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
    ans = response.choices[0].message.content
    return ans

#RAC
def generate_answer_RAC(url_content):
    openai.api_key = api_key
    client = OpenAI()
    response = client.chat.completions.create(
            model="gpt-4-0125-preview",
              messages=[
            {
                "role": "user",
                "content": f"extract these points from the document: Name, Business Registration No, Incorporation Date, Paid Up Capital, Total Equity/Net Asset, Current Ratio, Management Team(Name, Designation, Experience)  based on the following content and the understanding of the content: {url_content}\nAnswer: , Ensure 100% accuracy and answer should strictly and always be in JSON format. If information is not mentioned in the url content, then simply state Information Not Availble."            
            },
            {
                "role": "system",
                "content": "Based on the content found in the URL you provided, I can give you specific answers"
            },
            ],
            temperature=0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
    ans = response.choices[0].message.content
    return ans
   
#APP
def generate_answer_APP(url_content):
    openai.api_key = api_key
    client = OpenAI()
    response = client.chat.completions.create(
            model="gpt-4-0125-preview",
              messages=[
            {
                "role": "user",
                "content": f"extract these points from the document: Contract Amount, Contact Person, Name of Company, Type of Company, Bank Account Details  based on the following content and the understanding of the content: {url_content}\nAnswer: , Ensure 100% accuracy and answer should strictly and always be in JSON format. In case multiple answers are ticked, then give all the ticked options. If for a category/parameter there are multiple options that are ticked, then give all the ticked (only √) options(only of unicode \u221a). Do not miss or omit any information. If information is not mentioned in the url content, then simply state Information Not Available."            
            },
            {
                "role": "system",
                "content": "Based on the content found in the URL you provided, I can give you specific answers"
            },
            ],
            temperature=0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
    ans = response.choices[0].message.content
    return ans

#LO Prompt
def generate_answer_LO(url_content):
    openai.api_key = api_key
    client = OpenAI()
    response = client.chat.completions.create(
            model="gpt-4-0125-preview",
              messages=[
            {
                "role": "user",
                "content": f"extract these points from the document: Total and Types of Facility/Contract Amount, Tenure, Client, Factor, Credit Period, Grace Period  based on the following content and the understanding of the content: {url_content}\nAnswer: , Ensure 100% accuracy and answer should strictly and always be in JSON format. If information is not mentioned in the url content, then simply state Information Not Available."            
            },
            {
                "role": "system",
                "content": "Based on the content found in the URL you provided, I can give you specific answers"
            },
            ],
            temperature=0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
    ans = response.choices[0].message.content
    return ans

def main():
    while True:
        try:
            folder_path = r"uploads"
            files = os.listdir(folder_path)
            for file in files:
                print("file me aa rha hun : ",file)
                print("typr of file : ",type(file))
                if os.path.isfile(os.path.join(folder_path, file)):
                    file_path = os.path.join(folder_path, file)
                    print(file_path)
                    #path1 = get_path(file_path)
                    #raw_text = get_pdf_text1(file_path)
                    raw_text = get_pdf_text1(file_path)
                    print("coming in google trans")
                    for i in range(0,len(raw_text)):
                        raw_text[i].page_content = GoogleTranslator(source='auto', target='en').translate(raw_text[i].page_content)
                    print("converted the file")
                    prompt_template ="""Answer the question if can not find the answer just stated one-word: None. If answer not mentioned explicitly, then
                    understand the documents content by translating the context in english if in different and give the implied answer. In case multiple answers are ticked, then give all the ticked options. 
                    The answer/information is inside the document. Answer should be in form of json format stricly with no such symbol: ``` or ` and no text before or after, just need the dictionary NOTHING ELSE STRICTLY. Contract Price or Contract Value or Purchase Price should alway be in numerical form not string. If Contract End Date is not found, then simply find it by 
                    adding Contract Start Date and Tenure of Contract. Do not miss or omit any information and must Ensure maximum accuracy for all extracted information.
                                        Context: \n {context}?\n
                                        Question: \n {question} \n
                                        Answer:
                                    """
                    file_name = os.path.basename(file_path)
                    print("now going in generate answer")  
                    output_text1 = generate_answer_APP(raw_text)
                    print("json text : ",output_text1)
                    if output_text1 is not None:
                        start = output_text1.find('{')
                        end = output_text1.rfind('}') + 1
                        json_content = output_text1[start:end]
                        json_content = json_content.replace("None", "")
                        json_content = json_content.replace("null", "")
                        d = eval(json_content)
                        print(d)
                        save_json_to_directory(file_path,d)
                        os.remove(file_path)
        except Exception as e:
            print(f"An error occurred: {e}. Retrying...")
            break
        else:
            break

           

if __name__ == "__main__":
    main()


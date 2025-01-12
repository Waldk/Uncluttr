import configparser
import zipfile
import os
import fitz
import sys



def is_structured_pdf(file_path):
    with fitz.open(file_path) as doc:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():  
                return True
    return False

def folderAnalysis(path):
    if path is None:
        config = configparser.ConfigParser()
        config.read('configuration/conf.ini')
        path = config['settings']['directory_to_watch']
    
    print(f"Analyzing files in {path}...")
    sys.stdout.flush() 
    for root, dirs, files in os.walk(path):
        for file in files:
            fileAnalysis(os.path.join(root, file))

def fileAnalysis(file_path): 
    root, file = os.path.split(file_path)
    file_type = os.path.splitext(file_path)[1]
    match file_type:
        case '.zip':
            extract_path = os.path.join(root, os.path.splitext(file)[0])
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            os.remove(file_path)  
                
            print(file_path, "extracted.")
            sys.stdout.flush() 
            folderAnalysis(extract_path)

        case '.pdf':
            if is_structured_pdf(file_path):
                print(f"{file_path} is a structured PDF.")
            else:
                print(f"{file_path} is an unstructured PDF.")
            sys.stdout.flush() 
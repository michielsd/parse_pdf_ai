import os
import zipfile
import shutil
from PyPDF2 import PdfMerger

PDFS_FOLDER = "C:/Dashboard/Werk/Begrotingen/2026/Gemeenten/"
TEMP_FOLDER = "C:/Dashboard/Werk/llm_kengetallen/parse_pdf_ai/temp/"
OUTPUT_FOLDER = "C:/Dashboard/Werk/llm_kengetallen/parse_pdf_ai/pdfs/"


def main():
    for file in os.listdir(PDFS_FOLDER):
        if file.endswith(".zip"):
            unzip_and_save(PDFS_FOLDER, file, TEMP_FOLDER, OUTPUT_FOLDER)


def unzip_and_save(zip_folder, zip_file, temp_folder, extract_to_folder):
    with zipfile.ZipFile(os.path.join(zip_folder, zip_file), 'r') as zip_ref:
        zip_ref.extractall(temp_folder)

    # Get begroting
    hits = []
    
    file_list = os.listdir(temp_folder)
    
    # Check if directory
    subdir = ""
    if len(file_list) == 1:
        if os.path.isdir(os.path.join(temp_folder, file_list[0])):
            subdir = file_list[0] + "/"
            file_list = os.listdir(os.path.join(temp_folder, subdir))
    
    # Check if only one file
    if len(file_list) == 1:
        hits.append(file_list[0])
        
    # Check if file w/ same name as zip
    if len(hits) == 0:
        for file in file_list:
            if file == f"{zip_file[:-4]}.pdf":
                hits.append(file)
                break
    
    # Check w/ remaining conditions
    if len(hits) == 0:
        for file in file_list:
            if file.endswith(".pdf"):
                if not any(
                    a in file.lower() for a in [
                        'bijlagen', 'amendement', 'besluit', 
                        'wijziging', 'uitvoeringsinformatie',
                        'vaststelling', 'voorstel', 'motie',
                        'erratum', 'brief', 'nota', 
                        'taakveldenraming', 'vvd', 'sgp',
                        'pvda', 'cda', 'cu', 'getekend',
                        'rbs', 'rb ', 'vaststellen', 
                        'taakveld', 'rv ', 'rv_', 'productenboek',
                        'producten', 'addendum', 'krediet',
                        'in het kort', 'dossier', 'in een oogopslag',
                        'memo', 'rvs', 'cbs', 'detail', 
                        'geamendeerd', 'ondertekend'
                        'format'
                ]) and not file.startswith("AKK"):
                    hits.append(file)

    output_name = f"{zip_file[-8:-4]}.pdf"
    output_path = os.path.join(extract_to_folder, output_name)
    
    # If only one file, rename to GM code
    if len(hits) == 1:
        file_path = temp_folder + subdir + hits[0] # Subdir is empty if no subdirectory
        if not output_name in os.listdir(extract_to_folder):
            os.rename(file_path, output_path)
            print(f"[INFO] {zip_file} saved to {output_name}")
    # Else: merge all files into one
    else:
        if len(hits) == 0:
            hits = [f for f in file_list if f.endswith(".pdf")]        
        
        merge_pdfs(temp_folder + subdir, hits, output_path)
        print(f"[INFO] {len(hits)} of {zip_file} merged into {output_name}")
        
    # Clear temp folder
    for file in os.listdir(temp_folder):
        file_path = os.path.join(temp_folder, file)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

    return True

def merge_pdfs(temp_folder, file_list, output_path):
    merger = PdfMerger()
    
    for filename in file_list:
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(temp_folder, filename)
            merger.append(str(pdf_path))

    merger.write(str(output_path))
    merger.close()

    return output_path

if __name__ == "__main__":
    main()

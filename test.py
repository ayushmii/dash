import PyPDF2
import re
import os

# Open the PDF file in read-binary mode
with open('NCT03455556.pdf', 'rb') as file:
    # Create a PDF reader object
    reader = PyPDF2.PdfReader(file)

    # Create a directory to store the cleaned text files
    if not os.path.exists('cleaned_texts'):
        os.makedirs('cleaned_texts')

    # Loop through each page in the PDF
    for page_num in range(len(reader.pages)):
        # Get the page object
        page = reader.pages[page_num]

        # Extract the text from the page
        text = page.extract_text()

        # Remove table of references using regex
        text = re.sub(r'References\n.*?(\n\n|$)', '', text, flags=re.DOTALL)

        # Remove protocol-version date using regex
        text = re.sub(r'\d{2}\s+\w+\s+\d{4}', '', text)

        # Remove footer using regex
        text = re.sub(r'Footer\s+\d+', '', text)

        # Remove mc117 code using regex
        text = re.sub(r'MC117\s+\d+', '', text)

        # Remove page numbers using regex
        text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text)

        # Remove headers and footers using regex
        text = re.sub(r'^.*?\n', '', text, flags=re.MULTILINE)

        # Create a file name for the cleaned text
        file_name = f'cleaned_text_page_{page_num + 1}.txt'
        file_path = os.path.join('cleaned_texts', file_name)

        # Save the cleaned text to a file
        with open(file_path, 'w', encoding='utf-8') as text_file:
            text_file.write(text)

    print("Cleaned texts saved in the 'cleaned_texts' directory.")
import ipywidgets as widgets
from IPython.display import display
import fitz  # PyMuPDF
import os
from dotenv import load_dotenv
import re
import time

#Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

#Setting up LLM model
from langchain_openai.chat_models import ChatOpenAI
model = ChatOpenAI(openai_api_key = OPENAI_API_KEY, model="gpt-3.5-turbo")

#Set up chain parser
from langchain_core.output_parsers import StrOutputParser
parser = StrOutputParser()

#Set up prompt
from langchain.prompts import ChatPromptTemplate

template = """
Answer the question based on the context below. If you can't answer the question, reply "I don't know".

Context: {context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

global extracted_text
extracted_text = ""  # This will hold the text extracted from the PDF

def pdf_to_text_and_save(pdf_path, output_file_path):
    global extracted_text
    with fitz.open(pdf_path) as doc:
        text = ""
        for page in doc:
            page_text = page.get_text()
            # Sanitize the text to remove non-ASCII characters
            page_text = re.sub(r'[^\x00-\x7F]+', ' ', page_text)
            text += page_text
    extracted_text = text  # Update the global variable with extracted text
    
    # Save the extracted text to the specified output file path, ensuring UTF-8 encoding
    with open(output_file_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(text)
    return output_file_path

def list_pdf_files(directory):
    """
    List all PDF files in the given directory.
    """
    pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
    return pdf_files

def select_file_from_list(pdf_files):
    """
    Display a numbered list of PDF files and let the user select one.
    """
    if not pdf_files:
        print("No PDF files found in the directory.")
        return None
    
    print("PDF files available:")
    for index, file in enumerate(pdf_files, start=1):
        print(f"{index}. {file}")
    
    selection = input("Enter the number of the PDF you want to convert: ").strip()
    if selection.isdigit() and 1 <= int(selection) <= len(pdf_files):
        return pdf_files[int(selection) - 1]
    else:
        print("Invalid selection. Please enter a valid number.")
        return None

def pdf_directory():
    pdf_directory = 'rag'  # Directory where PDFs are located. Adjust as needed.
    output_directory = 'rag'  # Directory where you want to save 'converted.txt'. Adjust as needed.
    output_file_path = os.path.join(output_directory, 'converted.txt')  # Full path to the output file

    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    pdf_files = list_pdf_files(pdf_directory)
    
    selected_pdf = select_file_from_list(pdf_files)
    if selected_pdf:
        pdf_path = os.path.join(pdf_directory, selected_pdf)
        txt_file_path = pdf_to_text_and_save(pdf_path, output_file_path)
        print(f"Converted {selected_pdf} to text and saved to {txt_file_path}.")
    else:
        print("No PDF selected or available for conversion.")

pdf_directory()

print("Please wait while file is being PDF is being converted...")
time.sleep(10)  # Pauses the execution for 10 seconds.


#Load the converted document into memory
from langchain_community.document_loaders import TextLoader

loader = TextLoader(extracted_text)
text_documents = loader.load()
text_documents

#Split the document into smaller chunks so that llm can work with smaller quantities of tokens
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
documents = text_splitter.split_documents(text_documents)

#Embed the chunks
from langchain_openai.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

#Load the document into the vector store
from langchain_community.vectorstores import DocArrayInMemorySearch

vectorstore = DocArrayInMemorySearch.from_documents(documents, embeddings)

#Setup chain with new parameters
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

setup = RunnableParallel(
    context = vectorstore.as_retriever(), question=RunnablePassthrough()
)

chain = setup | prompt | model | parser

chain = (
    {"context": vectorstore.as_retriever(), "question": RunnablePassthrough()}
    | prompt
    | model
    | parser
)

result = chain.invoke("Tell me about the engines in this document.")
print(result)


import fitz  # PyMuPDF
import os
from dotenv import load_dotenv
import re
import time
import warnings

# Set the environment variable to turn off oneDNN custom operations
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Ignore the specific UserWarning from pydantic
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic._migration")

#Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY") # not currently in use

# Setting up Language Model
from langchain_openai.chat_models import ChatOpenAI
model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")

# Set up Chain Components
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

# Parser and Prompt Template
parser = StrOutputParser()
template = """
Answer the question based on the context below. If you can't answer the question, reply "I don't know".

Context: {context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

def pdf_to_text_and_save(pdf_path, output_file_path):
    with fitz.open(pdf_path) as doc:
        text = "".join([re.sub(r'[^\x00-\x7F]+', ' ', page.get_text()) for page in doc])

    with open(output_file_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(text)
    return output_file_path

def list_pdf_files(directory):
    """
    List all PDF files in the given directory.
    """
    return [f for f in os.listdir(directory) if f.endswith('.pdf')]

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
        print("No PDF selected or available for conversion. Exiting.")
        time.sleep(2)
        exit()

def ask_questions():
    while True:
        user_input = input("Ask me anything (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        
        chain = (
            {"context": vectorstore.as_retriever(), "question": RunnablePassthrough()}
            | prompt
            | model
            | parser
        )
        
        result = chain.invoke(user_input)
        print(f"AI: {result}")

if __name__ == "__main__":
    pdf_directory()

    print("Please wait while the PDF file is being converted...")
    time.sleep(10)  # Pauses the execution for 10 seconds.

    #Load the converted document into memory
    loader = TextLoader('rag/converted.txt')
    text_documents = loader.load()

    #Split the document into smaller chunks so that llm can work with smaller quantities of tokens
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
    documents = text_splitter.split_documents(text_documents)

    #Embed the chunks
    embeddings = OpenAIEmbeddings()

    #Load the document into the vector store
    vectorstore = DocArrayInMemorySearch.from_documents(documents, embeddings)

    #Setup chain with new parameters
    setup = RunnableParallel(
        context = vectorstore.as_retriever(), question=RunnablePassthrough()
    )

    chain = setup | prompt | model | parser

    ask_questions()



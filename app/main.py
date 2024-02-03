import spacy
import fitz  # PyMuPDF
import re
from entry_map import entity_mapping
from spacy.pipeline import EntityRuler
from collections import Counter
from tkinter import Tk, filedialog
from summarizer import Summarizer

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ''.join([doc[page_num].get_text() for page_num in range(doc.page_count)])
        doc.close()
        return text
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return ""

def create_entity_ruler(nlp, entity_mapping):
    ruler = nlp.add_pipe("entity_ruler", before="ner")
    patterns = [{"label": label, "pattern": term} for label, terms in entity_mapping.items() for term in terms]
    ruler.add_patterns(patterns)
    return nlp

def process_large_document(document_path):
    document_text = ""
    try:
        if document_path.endswith(".pdf"):
            document_text = extract_text_from_pdf(document_path)
        else:
            with open(document_path, 'r', encoding='utf-8') as file:
                document_text = file.read()
    except Exception as e:
        print(f"Error processing document: {e}")
        return "", [], [], None

    document_text = re.sub(r'\s+', ' ', document_text)  # Normalize whitespace

    nlp_model = "en_core_web_sm" if len(document_text) < 1e6 else "en_core_web_md" if len(document_text) < 1e7 else "en_core_web_lg"
    nlp = spacy.load(nlp_model)
    nlp = create_entity_ruler(nlp, entity_mapping)
    nlp.max_length = max(nlp.max_length, len(document_text) + 1)  # Safely increase max_length if needed

    doc = nlp(document_text)
    formatted_sentences = '\n'.join(sent.text.strip() for sent in doc.sents if sent.text.strip())
    tokens = [token.text for token in doc]
    entities = [(ent.text, ent.label_) for ent in doc.ents]

    return formatted_sentences, tokens, entities, doc

def generate_summary(doc, ratio=0.2):
    text = doc.text
    summarizer = Summarizer()
    try:
        summary = summarizer(text, ratio=ratio)
    except Exception as e:
        print(f"Error generating summary: {e}")
        return []
    return summary.split('\n')

def print_results_to_file(output_file, formatted_sentences, tokens, entities, summary):
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.writelines(["### Sentences ###\n", formatted_sentences + "\n\n",
                             "### Tokens ###\n", ', '.join(tokens) + "\n\n",
                             "### Named Entities ###\n"] +
                            [f"{ent}: {label}\n" for ent, label in entities] +
                            ["\n### Summary ###\n"] +
                            [sentence + "\n" for sentence in summary])
    except Exception as e:
        print(f"Error writing results to file: {e}")

def get_file_path(title):
    root = Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(title=title)
    root.destroy()  # Close the root window after selection
    return file_path

def main():
    print("Welcome to the Boeing NLP Document Processing Program!")
    choice = input("Enter 1 to process a document and generate a summary, or 2 to exit: ")
    if choice == "1":
        document_path = get_file_path("Select Document File (PDF or text file)")
        output_file = get_file_path("Select Output File")
        formatted_sentences, tokens, entities, doc = process_large_document(document_path)
        summary_sentences = generate_summary(doc)
        print_results_to_file(output_file, formatted_sentences, tokens, entities, summary_sentences)
        print(f"Results saved to {output_file}")
    elif choice == "2":
        print("Exiting the program...")
    else:
        print("Invalid option. Please enter 1 or 2.")
        
if __name__ == "__main__":
    main()

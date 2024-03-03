import spacy
import fitz  # PyMuPDF
import re
from tqdm import tqdm
from entry_map import entity_mapping
from spacy.pipeline import EntityRuler
from collections import Counter
from tkinter import Tk, filedialog
from datetime import datetime

# Entity mapping

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""

    for page_num in tqdm(range(doc.page_count), desc="Extracting text from PDF"):
        page = doc[page_num]
        text += page.get_text()

    text = text.replace("�", "•")
    doc.close()
    return text

def create_entity_ruler(nlp, entity_mapping):
    ruler = nlp.add_pipe("entity_ruler")  # Add a new EntityRuler to the pipeline
    patterns = []
    for label, terms in tqdm(entity_mapping.items(), desc="Creating entity patterns"):
        for term in terms:
            patterns.append({"label": label, "pattern": term})
    ruler.add_patterns(patterns)
    return nlp

def process_large_document(document_path):
    print(f'{datetime.now()}: Loading document')
    with tqdm(total=5, desc="Processing", ncols=100) as pbar:
        if document_path.endswith(".pdf"):
            document_text = extract_text_from_pdf(document_path)
        else:
            with open(document_path, 'r', encoding='utf-8') as file:
                document_text = file.read()
        pbar.update()

        document_text = re.sub(r'\.{3,}', ' ', document_text)
        pbar.update()

        # Identify, extract, and process the TOC
        print(f'{datetime.now()}: Identifying TOC')
        toc_entries = identify_toc(document_text)
        print(f'{datetime.now()}: Processing TOC')
        toc = process_toc(toc_entries)
        pbar.update()

        # Write the TOC to output.txt
        print(f'{datetime.now()}: Writing TOC to output.txt')
        with open('data/output.txt', 'w') as file:
            for title, page in toc.items():
                file.write(f'{title} . . . {page}\n')
        pbar.update()

        print(f'{datetime.now()}: loading spacY model and creating entity ruler')
        # load different spaCy models based on document size
        if len(document_text) < 1000000:
            nlp = spacy.load("en_core_web_sm")
        elif len(document_text) < 10000000:
            nlp = spacy.load("en_core_web_md")
        else:
            nlp = spacy.load("en_core_web_lg")
        pbar.update()

        nlp = create_entity_ruler(nlp, entity_mapping)

        # increase the max_length limit
        nlp.max_length = len(document_text) + 1000000

        doc = nlp(document_text)

        sentences = [sent.text + '\n' for sent in doc.sents if sent.text.strip() != '']

        formatted_sentences = ''.join(sentences)

        tokens = [token.text for token in doc]
        entities = [(ent.text, ent.label_) for ent in doc.ents]

    return formatted_sentences, tokens, entities, doc

def identify_toc(document_text):
    # This regular expression matches a line of text followed by dots and a number
    pattern = re.compile(r'.+\.\s+\d+')
    matches = pattern.findall(document_text)
    return matches

def process_toc(toc_entries):
    toc = {}
    for entry in toc_entries:
        # Split the entry into title and page number
        title, page = re.split(r'\.\s+', entry)
        toc[title.strip()] = int(page)
    return toc

def contains_number(sentence):
    return any(char.isdigit() for char in sentence.text)

def generate_summary(doc, top_n=3):
    words = [word.text.lower() for word in doc]
    word_freq = Counter(words)
    
    taxonomy_labels = set(entity_mapping.keys())

    sorted_sentences = sorted(doc.sents, key=lambda sentence: sum(word_freq[word.text.lower()] for word in sentence if word.ent_type_ in taxonomy_labels and not contains_number(word)), reverse=True)

    # filtered_sentences = [sentence for sentence in sorted_sentences if not contains_number(sentence)]

    top_sentences = sorted_sentences[:top_n]

    return top_sentences

def print_results_to_file(output_file, formatted_sentences, tokens, entities, summary):
    with open(output_file, 'w', encoding='utf-8') as file:
        print(f'{datetime.now()}: writing results to output file')
        file.write("### Sentences ###\n")
        file.write(formatted_sentences)

        file.write("\n### Tokens ###\n")
        clean_tokens = [token.replace("\n", "") for token in tokens]
        file.write(str(clean_tokens) + '\n')

        file.write("\n### Named Entities ###\n")
        for entity, label in entities:
            clean_entity = entity.replace("\n", "")
            file.write(f"Entity: {clean_entity}, Label: {label}\n")

        file.write("\n### Summary ###\n")
        file.write(''.join([sentence.text + '\n' for sentence in summary]))

def get_file_path(title):
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title=title)
    return file_path

def main():
    print("Welcome to the Boeing NLP Document Processing Program!")
    print("Please choose an option:")
    print("1. Process a document and generate a summary")
    print("2. Exit")

    choice = input("Enter the option number: ")

    if choice == "1":
        document_path = get_file_path("Select Document File (PDF or text file)")
        output_file = get_file_path("Select Output File")
        
        formatted_sentences, tokens, entities, doc = process_large_document(document_path)
        summary_sentences = generate_summary(doc)
        print_results_to_file(output_file, formatted_sentences, tokens, entities, summary_sentences)
        
        print(f"Results saved to {output_file}")
    elif choice == "2":
        print("Exiting the program.")
    else:
        print("Invalid option. Please choose a valid option.")

if __name__ == "__main__":
    main()

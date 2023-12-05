import spacy
import fitz  # PyMuPDF
import re
from collections import Counter

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""

    for page_num in range(doc.page_count):
        page = doc[page_num]
        text += page.get_text()

    doc.close()
    return text

def process_large_document(document_path):
    if document_path.endswith(".pdf"):
        document_text = extract_text_from_pdf(document_path)
    else:
        with open(document_path, 'r', encoding='utf-8') as file:
            document_text = file.read()

    document_text = re.sub(r'\.{3,}', ' ', document_text)

    nlp = spacy.load("en_core_web_sm")

    doc = nlp(document_text)

    sentences = [sent.text + '\n' for sent in doc.sents if sent.text.strip() != '']
    formatted_sentences = ''.join(sentences)

    tokens = [token.text for token in doc]
    entities = [(ent.text, ent.label_) for ent in doc.ents]

    return formatted_sentences, tokens, entities, doc

def contains_number(sentence):
    return any(char.isdigit() for char in sentence.text)

def generate_summary(doc, top_n=3):
    words = [word.text.lower() for word in doc]
    word_freq = Counter(words)

    sorted_sentences = sorted(doc.sents, key=lambda sentence: sum(word_freq[word.text.lower()] for word in sentence), reverse=True)

    filtered_sentences = [sentence for sentence in sorted_sentences if not contains_number(sentence)]

    top_sentences = filtered_sentences[:top_n]

    return top_sentences

def print_results_to_file(output_file, formatted_sentences, tokens, entities, summary):
    with open(output_file, 'w', encoding='utf-8') as file:
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

def main():
    print("Welcome to the Document Processing Program!")
    print("Please choose an option:")
    print("1. Process a document and generate a summary")
    print("2. Exit")

    choice = input("Enter the option number: ")

    if choice == "1":
        document_path = input("Enter the path to the document (PDF or text file): ")
        output_file = input("Enter the path to the output file: ")

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

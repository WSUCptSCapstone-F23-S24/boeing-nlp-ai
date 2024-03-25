import spacy
import fitz  # PyMuPDF
import re
from entry_map import entity_mapping
from spacy.pipeline import EntityRuler
from collections import Counter
from tkinter import Tk, filedialog
from summarizer import Summarizer
from transformers import T5ForConditionalGeneration, T5Tokenizer
import openai
import gradio

client = openai.OpenAI(
    api_key="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",
)

messages = [{"role": "system", "content": "You are a Boeing Executive that knows all about the company"}]

def CustomChatGPT(user_input):
    messages.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
        )
    ChatGPT_reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": ChatGPT_reply})
    return ChatGPT_reply

def chatGPT_summarize(summary, entities):
    entities_str = ', '.join([f"{ent[0]} ({ent[1]})" for ent in entities]) 
    prompt = f"Document Summary: {summary}\nIdentified Entities: {entities_str}\n\nProvide a detailed summary and critical insights:"

    chat_gpt_response = CustomChatGPT(prompt)
    
    return chat_gpt_response

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


def print_results_to_file(output_file, formatted_sentences, entities, summary):
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            # Replace question mark characters in each section before writing
            formatted_sentences_clean = formatted_sentences.replace('�', '')
            entities_clean = [(ent.replace('�', ''), label) for ent, label in entities]
            
            # Assuming summary_clean is a list of sentences/paragraphs
            summary_clean = [sentence.replace('�', '') for sentence in summary]

            file.write("### Sentences ###\n")
            file.write(formatted_sentences_clean + "\n\n")
            file.write("### Named Entities ###\n")
            for ent, label in entities_clean:
                file.write(f"{ent}: {label}\n")
            file.write("\n### Summary ###\n")
            
            # each sentence/paragraph of the summary on a new line
            for sentence in summary_clean:
                # new line between paragraphs/sentences for better readability -- not functional atm
                file.write(sentence + "/n")
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
        
        # Ask the user for specific entities they want to highlight
        entity_input = input("Enter the entities you want to highlight (separated by comma, e.g., PERSON,ENGINE): ")
        entity_list = [entity.strip().upper() for entity in entity_input.split(',')]
        
        # Ask the user to set the summary length
        summary_length_input = input("Enter the summary length as a percentage of the original text (e.g., 20 for 20%): ")
        try:
            summary_length = float(summary_length_input) / 100
        except ValueError:
            print("Invalid summary length. Setting to default 20%.")
            summary_length = 0.2

        formatted_sentences, tokens, entities, doc = process_large_document(document_path)
        
        # Filter entities based on user selection
        highlighted_entities = [(ent, label) for ent, label in entities if label in entity_list]
        
        summary_sentences = generate_summary(doc, ratio=summary_length)

        response = chatGPT_summarize(summary_sentences, highlighted_entities)
        print(response)
        
        # Call modified print_results_to_file to include only the relevant entities
        print_results_to_file(output_file, formatted_sentences, highlighted_entities, summary_sentences)
        
        print(f"Results saved to {output_file}")
    elif choice == "2":
        print("Exiting the program...")
    else:
        print("Invalid option. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
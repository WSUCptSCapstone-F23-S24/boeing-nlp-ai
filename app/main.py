import spacy
import fitz  # PyMuPDF
import re
from spacy.pipeline import EntityRuler
from collections import Counter
from tkinter import Tk, filedialog

# Entity mapping
entity_mapping = {
    "PERSON": [
        "Pilot", "Co-pilot", "Flight Engineer", "Navigator",
        "Aircraft Mechanic", "Air Traffic Controller",
        "Avionics Technician", "Safety Officer", "Passenger",
    ],

    "EMPENNAGE": [
        "Horizontal Stabilizer", "Vertical Stabilizer", "Elevator", "Rudder",
        "Trim Tabs", "Fin", "Tailplane", "Stabilator", "Raked Wingtips"
    ],

    "FUSELAGE": [
        "Cabin", "Cargo Hold", "Bulkhead", "Hatch", "Airframe", "Cockpit Door",
        "Window", "Fuselage Frame", "Pressure Bulkhead", "Al-Li", "Carbon Composite Materials",
        "Winglets", "Blended Winglets on 737NG", "Raked Wingtips on 787", "Double-Decker Configuration",
        "Overhead Bins", "Lavatories"
    ],

    "COCKPIT": [
        "Control Column", "Instrument Panel", "Throttle Quadrant", "Rudder Pedals",
        "Autopilot Control", "Ejection Seat", "MFD (Multi-Function Display)", "Honeywell Avionics",
        "Rockwell Collins Flight Deck", "Boeing Sky Interior", "Enhanced Flight Vision System (EFVS)",
        "Head-Up Display (HUD)", "Electronic Flight Bag (EFB)", "Flight Director", "Control Display Units",
        "Multi-Functional Display", "Auto-Throttle", "Flight Management Computer (FMC)"
    ],

    "RUNNING_LANDING_GEAR": [
        "Main Gear", "Nose Gear", "Tires", "Brakes", "Shock Absorber", "Retraction Mechanism",
        "Wheel Well", "Landing Gear Doors", "Wheels", "Runway", "Auto-Throttle"
    ],

    "ENGINE": [
        "Turbine", "Compressor", "Combustor", "Fan", "Nozzle", "Exhaust",
        "Fuel Injector", "Thrust Reverser", "Nacelle", "CFM56", "GEnx", "GE90",
        "PW4000", "LEAP-1B", "Rolls-Royce Trent 1000", "Rolls-Royce Trent 800", "PW4090",
        "Rolls-Royce Trent 800", "General Electric GE90", "Pratt & Whitney PW4090"
    ],

    "AIRPLANE_MODEL": [
        "Boeing 720", "Boeing 777", "Convair 990", "Boeing 757",
        "Boeing 767", "Airbus 300", "Boeing 747", "Boeing 777-200ER",
        "Boeing 777-300ER"
    ],

    "AIRCRAFT_SPECIFICATIONS": [
        "Dimensions", "Weights", "Capacity", "Power plants", "Field lengths",
        "Range", "Speed", "Altitude", "Max Take Off Weight (MTOW)", "Fuel Capacity",
        "Cruise Altitude"
    ],

    "OPERATING_PROCEDURES": [
        "Pre-Flight", "Gate departure", "Takeoff", "Climb", "Cruise", "Descent",
        "Approach", "Landing", "Taxi to Terminal", "Securing the Aircraft", "Engine fire",
        "Engine failure", "Power loss", "Gear stuck",  "Pre-Flight Checklist", "Taxi to Terminal",
        "Securing the Aircraft", "Missed Approach Procedure"
    ]

}

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""

    for page_num in range(doc.page_count):
        page = doc[page_num]
        text += page.get_text()

    doc.close()
    return text

def create_entity_ruler(nlp, entity_mapping):
    ruler = EntityRuler(nlp)
    patterns = []
    for label, terms in entity_mapping.items():
        for term in terms:
            patterns.append({"label": label, "pattern": term})
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler, before="ner")
    return nlp

def process_large_document(document_path):
    if document_path.endswith(".pdf"):
        document_text = extract_text_from_pdf(document_path)
    else:
        with open(document_path, 'r', encoding='utf-8') as file:
            document_text = file.read()

    document_text = re.sub(r'\.{3,}', ' ', document_text)

     # load different spaCy models based on document size
    if len(document_text) < 1000000:
        nlp = spacy.load("en_core_web_sm")
    elif len(document_text) < 10000000:
        nlp = spacy.load("en_core_web_md")
    else:
        nlp = spacy.load("en_core_web_lg")
        
    nlp = create_entity_ruler(nlp, entity_mapping)

    # increase the max_length limit
    nlp.max_length = len(document_text) + 1000000

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
    
    taxonomy_labels = set(entity_mapping.keys())

    sorted_sentences = sorted(doc.sents, key=lambda sentence: sum(word_freq[word.text.lower()] for word in sentence if word.ent_type_ in taxonomy_labels), reverse=True)

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

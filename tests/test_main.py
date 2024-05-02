from v1.main import *
import spacy

def test_extract_text_from_pdf_with_valid_path():
    test_pdf_path = "tests/test_files/dummy.pdf"
    expected_text = "Dummy PDF file"
    
    # function to test
    extracted_text = extract_text_from_pdf(test_pdf_path)
    
    # verification
    assert extracted_text.strip() == expected_text, "The extracted text should match the expected text."

def test_extract_text_from_pdf_with_invalid_path():
    extracted_text = extract_text_from_pdf("does/not/exist/pdf.pdf")
    assert extracted_text == '', "Function should return an empty string for invalid paths"

def test_create_entity_ruler():
    pass

def test_process_large_document_with_pdf_file():
    document_path = "../data/test.pdf"
    formatted_sentences, tokens, entities, doc = process_large_document(document_path)
    assert formatted_sentences is not None
    assert tokens is not None
    assert entities is not None
    assert doc is not None

def test_process_large_document_with_txt_file():
    pass

def test_process_large_document_with_invalid_file():
    pass

def test_generate_summary():
    nlp = spacy.blank("en")
    doc = nlp("This is a test document. It contains several sentences. The summary should be concise.")
    summary = generate_summary(doc, ratio=0.5)
    assert isinstance(summary, list)
    assert len(summary) > 0  # Assuming the summarizer reduces the content but still returns something

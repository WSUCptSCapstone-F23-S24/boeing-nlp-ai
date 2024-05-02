import pytest
import os
from v2.boeing_rag_final import pdf_to_text_and_save, list_pdf_files

def test_pdf_to_text_conversion():
    # Assuming you have a test PDF file in your test directory
    test_pdf_path = 'tests/test_files/dummy.pdf'
    output_path = 'tests/test_files/output.txt'
    expected_output = "Dummy PDF file\n"
    
    # Call the function
    result_path = pdf_to_text_and_save(test_pdf_path, output_path)
    
    # Read the output file
    with open(result_path, 'r', encoding='utf-8') as file:
        output = file.read()
    
    # Check if the output matches the expected output
    assert output == expected_output, "The PDF text conversion did not produce the expected text."

def test_list_pdf_files_empty_directory(tmpdir):
    # Use pytest's tmpdir fixture to create a temporary directory
    assert list_pdf_files(tmpdir) == [], "Should return an empty list for an empty directory"

def test_list_pdf_files_non_empty_directory(tmpdir):
    # Create a test PDF file in the temporary directory
    tmpdir.join("sample.pdf").write("content")
    assert list_pdf_files(tmpdir) == ['sample.pdf'], "Should list PDF files in a non-empty directory"
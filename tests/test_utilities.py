from unittest.mock import patch
from v2.boeing_rag_final import select_file_from_list

def test_select_file_from_list_valid_selection():
    pdf_files = ['document1.pdf', 'document2.pdf', 'document3.pdf']
    with patch('builtins.input', return_value='2'):
        selected_file = select_file_from_list(pdf_files)
        assert selected_file == 'document2.pdf', "Should correctly select the second file"

def test_select_file_from_list_invalid_selection():
    pdf_files = ['document1.pdf', 'document2.pdf', 'document3.pdf']
    with patch('builtins.input', return_value='5'):  # Invalid because there are only 3 files
        selected_file = select_file_from_list(pdf_files)
        assert selected_file is None, "Should return None for an invalid selection"

def test_select_file_from_list_empty():
    with patch('builtins.input', return_value='1'):
        selected_file = select_file_from_list([])
        assert selected_file is None, "Should return None when no files are available"
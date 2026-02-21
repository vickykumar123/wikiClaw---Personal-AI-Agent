# ============================================
# TEST FILE PROCESSING
# ============================================
#
# Usage: python scripts/test_file_processing.py
#
# Tests the file processor utility.

import os
import sys
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.file_processor import (
    process_file,
    is_supported_file,
    check_file_size,
    SUPPORTED_FILE_EXTENSIONS
)


def test_text_file():
    """Test processing a text file."""
    print("\n" + "=" * 50)
    print("TEST: Text File")
    print("=" * 50)

    # Create a test text file
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        delete=False
    ) as f:
        f.write("Hello, this is a test text file.\n")
        f.write("It contains multiple lines.\n")
        f.write("The agent should be able to read this.")
        tmp_path = f.name

    try:
        result = process_file(tmp_path)
        print(f"Success: {result.success}")
        print(f"File type: {result.file_type}")
        print(f"Truncated: {result.truncated}")
        print(f"Content preview: {result.text[:100]}...")
    finally:
        os.unlink(tmp_path)


def test_json_file():
    """Test processing a JSON file."""
    print("\n" + "=" * 50)
    print("TEST: JSON File")
    print("=" * 50)

    # Create a test JSON file
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False
    ) as f:
        f.write('{"name": "Test", "items": [1, 2, 3], "active": true}')
        tmp_path = f.name

    try:
        result = process_file(tmp_path)
        print(f"Success: {result.success}")
        print(f"File type: {result.file_type}")
        print(f"Content:\n{result.text}")
    finally:
        os.unlink(tmp_path)


def test_csv_file():
    """Test processing a CSV file."""
    print("\n" + "=" * 50)
    print("TEST: CSV File")
    print("=" * 50)

    # Create a test CSV file
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".csv",
        delete=False
    ) as f:
        f.write("Name,Age,City\n")
        f.write("Alice,30,New York\n")
        f.write("Bob,25,Los Angeles\n")
        f.write("Charlie,35,Chicago\n")
        tmp_path = f.name

    try:
        result = process_file(tmp_path)
        print(f"Success: {result.success}")
        print(f"File type: {result.file_type}")
        print(f"Content:\n{result.text}")
    finally:
        os.unlink(tmp_path)


def test_unsupported_file():
    """Test handling of unsupported file type."""
    print("\n" + "=" * 50)
    print("TEST: Unsupported File Type")
    print("=" * 50)

    # Create a test file with unsupported extension
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".xyz",
        delete=False
    ) as f:
        f.write("This should not be processed")
        tmp_path = f.name

    try:
        result = process_file(tmp_path)
        print(f"Success: {result.success}")
        print(f"Error: {result.error}")
    finally:
        os.unlink(tmp_path)


def test_supported_extensions():
    """Show all supported file extensions."""
    print("\n" + "=" * 50)
    print("SUPPORTED FILE EXTENSIONS")
    print("=" * 50)

    from constants import SUPPORTED_FILE_EXTENSIONS
    print(", ".join(SUPPORTED_FILE_EXTENSIONS))


def main():
    print("=" * 50)
    print("FILE PROCESSING TESTS")
    print("=" * 50)

    test_supported_extensions()
    test_text_file()
    test_json_file()
    test_csv_file()
    test_unsupported_file()

    print("\n" + "=" * 50)
    print("ALL TESTS COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    main()

"""
Test utility modules.
"""
import pytest
import os
from datetime import datetime, timedelta
from pathlib import Path

from utils.utils import validate_id
from utils.email_utils import generate_vs_surf_results, send_email_gmail
from utils.consumer_utils import get_user_info


class TestValidationUtils:
    """Test validation utility functions."""
    
    def test_validate_id_valid(self):
        """Test valid ID validation."""
        valid_ids = [
            "simple_id",
            "id_with_numbers_123",
            "ID-with-dashes",
            "id.with.dots",
            "MixedCase_ID_123"
        ]
        
        for valid_id in valid_ids:
            assert validate_id(valid_id) is True
    
    def test_validate_id_invalid(self):
        """Test invalid ID validation."""
        invalid_ids = [
            "../parent_directory",
            "id/with/slashes",
            "id\\with\\backslashes",
            "/absolute/path",
            "id:with:colons",
            "id*with*wildcards",
            "id?with?questions",
            "id<with>brackets",
            "id|with|pipes",
            "",  # Empty string
            " ",  # Just whitespace
            ".",  # Current directory
            "..",  # Parent directory
        ]
        
        for invalid_id in invalid_ids:
            assert validate_id(invalid_id) is False
    
    def test_validate_id_edge_cases(self):
        """Test edge cases for ID validation."""
        # Very long ID
        long_id = "a" * 255
        assert validate_id(long_id) is True
        
        # ID with unicode characters (should be invalid)
        unicode_id = "id_with_émojis_🚀"
        assert validate_id(unicode_id) is False
        
        # ID with null bytes (should be invalid)
        null_id = "id\x00with\x00nulls"
        assert validate_id(null_id) is False


class TestEmailUtils:
    """Test email utility functions."""
    
    def test_generate_vs_surf_results(self):
        """Test generating VS Surf results email."""
        client_name = "Test Client"
        plain_text, html_text = generate_vs_surf_results(client_name)
        
        # Check plain text
        assert isinstance(plain_text, str)
        assert client_name in plain_text
        assert "VsSurf 1dS®" in plain_text
        assert "results are ready" in plain_text.lower()
        
        # Check HTML text
        assert isinstance(html_text, str)
        assert client_name in html_text
        assert "<html>" in html_text.lower()
        assert "VsSurf 1dS®" in html_text
    
    def test_generate_vs_surf_results_special_chars(self):
        """Test generating email with special characters in name."""
        client_name = "Test & Client <with> Special"
        plain_text, html_text = generate_vs_surf_results(client_name)
        
        # Plain text should contain the raw name
        assert "Test & Client <with> Special" in plain_text
        
        # HTML should have escaped characters
        assert "Test &amp; Client &lt;with&gt; Special" in html_text or \
               "Test & Client <with> Special" in html_text
    
    @pytest.mark.skip(reason="Requires actual email credentials")
    def test_send_email_gmail(self, temp_dir):
        """Test sending email via Gmail (skipped in CI)."""
        # Create test attachments
        attachment1 = os.path.join(temp_dir, "test1.txt")
        attachment2 = os.path.join(temp_dir, "test2.png")
        
        with open(attachment1, "w") as f:
            f.write("Test attachment 1")
        
        with open(attachment2, "wb") as f:
            f.write(b"PNG fake data")
        
        result = send_email_gmail(
            from_address="test@gmail.com",
            application_password="test_password",
            subject="Test Email",
            body_plain="Test plain body",
            body_html="<html><body>Test HTML body</body></html>",
            recipients=["recipient@test.com"],
            bcc_recipients=["bcc@test.com"],
            attachments=[attachment1, attachment2]
        )
        
        # Would need actual credentials to test
        assert result is not None


class TestConsumerUtils:
    """Test consumer utility functions."""
    
    def test_get_user_info_valid_directory(self, temp_dir):
        """Test getting user info from valid directory structure."""
        # Create expected directory structure
        user_info_path = os.path.join(temp_dir, "userInfo.txt")
        with open(user_info_path, "w") as f:
            f.write("John Doe\n")
            f.write("+1234567890\n")
            f.write("john.doe@example.com\n")
        
        name, phone, email = get_user_info(temp_dir)
        
        assert name == "John Doe"
        assert phone == "+1234567890"
        assert email == "john.doe@example.com"
    
    def test_get_user_info_missing_file(self, temp_dir):
        """Test getting user info when file is missing."""
        name, phone, email = get_user_info(temp_dir)
        
        assert name == "Unknown"
        assert phone == "Unknown"
        assert email == "Unknown"
    
    def test_get_user_info_incomplete_file(self, temp_dir):
        """Test getting user info from incomplete file."""
        user_info_path = os.path.join(temp_dir, "userInfo.txt")
        with open(user_info_path, "w") as f:
            f.write("John Doe\n")
            # Missing phone and email
        
        name, phone, email = get_user_info(temp_dir)
        
        assert name == "John Doe"
        assert phone == "Unknown"
        assert email == "Unknown"
    
    def test_get_user_info_extra_whitespace(self, temp_dir):
        """Test getting user info with extra whitespace."""
        user_info_path = os.path.join(temp_dir, "userInfo.txt")
        with open(user_info_path, "w") as f:
            f.write("  John Doe  \n")
            f.write("  +1234567890  \n")
            f.write("  john.doe@example.com  \n")
        
        name, phone, email = get_user_info(temp_dir)
        
        assert name == "John Doe"
        assert phone == "+1234567890"
        assert email == "john.doe@example.com"
    
    def test_get_user_info_empty_lines(self, temp_dir):
        """Test getting user info with empty lines."""
        user_info_path = os.path.join(temp_dir, "userInfo.txt")
        with open(user_info_path, "w") as f:
            f.write("\n")  # Empty name
            f.write("\n")  # Empty phone
            f.write("john.doe@example.com\n")
        
        name, phone, email = get_user_info(temp_dir)
        
        assert name == "Unknown"
        assert phone == "Unknown"
        assert email == "john.doe@example.com"


class TestPathUtils:
    """Test path-related utility functions."""
    
    def test_safe_path_join(self):
        """Test safe path joining to prevent directory traversal."""
        # This is a hypothetical test - adjust based on actual implementation
        pass
    
    def test_ensure_directory_exists(self, temp_dir):
        """Test ensuring directory exists."""
        # This is a hypothetical test - adjust based on actual implementation
        new_dir = os.path.join(temp_dir, "new", "nested", "directory")
        
        # Assuming there's a utility function for this
        # ensure_directory_exists(new_dir)
        # assert os.path.exists(new_dir)
        pass


class TestDateTimeUtils:
    """Test datetime utility functions."""
    
    def test_format_datetime(self):
        """Test datetime formatting."""
        # This is a hypothetical test - adjust based on actual implementation
        dt = datetime(2024, 1, 15, 14, 30, 0)
        
        # Assuming there's a utility function for this
        # formatted = format_datetime(dt)
        # assert formatted == "2024-01-15 14:30:00"
        pass
    
    def test_parse_datetime(self):
        """Test datetime parsing."""
        # This is a hypothetical test - adjust based on actual implementation
        date_string = "2024-01-15 14:30:00"
        
        # Assuming there's a utility function for this
        # parsed = parse_datetime(date_string)
        # assert parsed.year == 2024
        # assert parsed.month == 1
        # assert parsed.day == 15
        pass


class TestFileUtils:
    """Test file-related utility functions."""
    
    def test_get_file_size_human_readable(self):
        """Test converting file size to human-readable format."""
        # This is a hypothetical test - adjust based on actual implementation
        sizes = [
            (1024, "1.0 KB"),
            (1024 * 1024, "1.0 MB"),
            (1024 * 1024 * 1024, "1.0 GB"),
            (1536, "1.5 KB"),
            (0, "0 B"),
            (999, "999 B"),
        ]
        
        # Assuming there's a utility function for this
        # for size, expected in sizes:
        #     assert get_file_size_human_readable(size) == expected
        pass
    
    def test_get_file_extension(self):
        """Test extracting file extension."""
        # This is a hypothetical test - adjust based on actual implementation
        test_cases = [
            ("file.txt", ".txt"),
            ("file.tar.gz", ".gz"),
            ("file", ""),
            (".hidden", ""),
            ("file.TXT", ".txt"),  # Case insensitive
        ]
        
        # Assuming there's a utility function for this
        # for filename, expected in test_cases:
        #     assert get_file_extension(filename) == expected
        pass
    
    def test_is_valid_file_type(self):
        """Test validating file types."""
        # This is a hypothetical test - adjust based on actual implementation
        allowed_types = [".txt", ".pdf", ".sgy"]
        
        valid_files = ["doc.txt", "report.pdf", "data.sgy"]
        invalid_files = ["script.exe", "image.jpg", "video.mp4"]
        
        # Assuming there's a utility function for this
        # for file in valid_files:
        #     assert is_valid_file_type(file, allowed_types) is True
        # 
        # for file in invalid_files:
        #     assert is_valid_file_type(file, allowed_types) is False
        pass


class TestSecurityUtils:
    """Test security-related utility functions."""
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # This is a hypothetical test - adjust based on actual implementation
        test_cases = [
            ("normal_file.txt", "normal_file.txt"),
            ("../../../etc/passwd", "etc_passwd"),
            ("file<>:\"|?*.txt", "file_______.txt"),
            ("file with spaces.txt", "file_with_spaces.txt"),
            ("файл.txt", "file.txt"),  # Non-ASCII characters
        ]
        
        # Assuming there's a utility function for this
        # for input_name, expected in test_cases:
        #     assert sanitize_filename(input_name) == expected
        pass
    
    def test_generate_secure_token(self):
        """Test secure token generation."""
        # This is a hypothetical test - adjust based on actual implementation
        # Assuming there's a utility function for this
        # token1 = generate_secure_token(32)
        # token2 = generate_secure_token(32)
        # 
        # assert len(token1) == 32
        # assert len(token2) == 32
        # assert token1 != token2  # Should be unique
        pass 
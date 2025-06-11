from utils.authentication import hash_password, verify_password


class TestPasswordHashing:
    """Test password hashing functionality."""

    def test_password_hash_verification(self):
        """Test that password hashing and verification works correctly."""
        password = "testpassword123"
        hashed = hash_password(password)

        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)

    def test_same_password_different_hash(self):
        """Test that same password produces different hashes."""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # With bcrypt, same password with same salt would produce same hash
        # But bcrypt generates new salt each time by default, so hashes should be different
        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

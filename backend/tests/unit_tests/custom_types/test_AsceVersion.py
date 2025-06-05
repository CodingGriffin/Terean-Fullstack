import pytest
from fastapi import HTTPException
from utils.custom_types.AsceVersion import AsceVersion


class TestAsceVersion:
    def test_list_values(self):
        values = AsceVersion.list_values()
        assert isinstance(values, list)
        assert all(isinstance(x, str) for x in values)

    def test_list_values_as_string(self):
        values_str = AsceVersion.list_values_as_string()
        assert isinstance(values_str, str)

    @pytest.mark.parametrize("raw, expected", [
        ("ASCE 7-16", AsceVersion.asce_716),
        ("ASCE 7-22", AsceVersion.asce_722),
        ("   ASCE 7-16", AsceVersion.asce_716),
        ("   ASCE 7-22", AsceVersion.asce_722),
        ("ASCE 7-16   ", AsceVersion.asce_716),
        ("ASCE 7-22   ", AsceVersion.asce_722),
        ("   ASCE   7-16   ", AsceVersion.asce_716),
        ("   ASCE   7-22   ", AsceVersion.asce_722),
        ("ASCE7-16", AsceVersion.asce_716),
        ("ASCE7-22", AsceVersion.asce_722),

    ])
    def test_from_str_spaces(self, raw, expected):
        assert AsceVersion.from_str(raw) == expected

    @pytest.mark.parametrize("raw, expected", [
        ("ASCE 7-16", AsceVersion.asce_716),
        ("ASCE 7-22", AsceVersion.asce_722),
        ("asce 7-16", AsceVersion.asce_716),
        ("asce 7-22", AsceVersion.asce_722),
        ("AsCe 7-16", AsceVersion.asce_716),
        ("AsCe 7-22", AsceVersion.asce_722),
    ])
    def test_from_str_case_sensitive(self, raw, expected):
        assert AsceVersion.from_str(raw) == expected

    def test_from_str_invalid(self):
        with pytest.raises(HTTPException) as exc_info:
            AsceVersion.from_str("invalid")
        assert exc_info.value.status_code == 400
        assert "valid options" in str(exc_info.value.detail).lower()

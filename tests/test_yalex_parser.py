# tests/test_yalex_parser.py
import pytest
from models.yalex_parser import YALexParser

@pytest.fixture
def yalex_parser():
    p = YALexParser("inputs/lexer.yal")
    p.parse()
    return p

def test_header_and_trailer(yalex_parser):
    # En lexer.yal hay un header con import myToken
    assert "import myToken" in yalex_parser.header_code
    # Trailer también debe existir 
    assert isinstance(yalex_parser.trailer_code, str)

def test_definitions(yalex_parser):
    defs = yalex_parser.definitions
    # Debimos capturar LETTER y DIGIT
    assert "LETTER" in defs
    assert defs["LETTER"].strip() == "[A-Za-z]"
    assert "DIGIT" in defs
    assert defs["DIGIT"].strip() == "[0-9]"

def test_rules_extracted(yalex_parser):
    rules = yalex_parser.rules
    # Al menos 1 regla
    assert len(rules) > 0
    # Cada regla es (regex, action)
    for regex, action in rules:
        assert isinstance(regex, str) and regex != ""
        assert action.strip().startswith("return")

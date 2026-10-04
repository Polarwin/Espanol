import pytest

from backend.app.services.ai import a2_checker, providers
from backend.app.services.ai.contracts import Correction


@pytest.mark.parametrize('text,replacement', [
    ('Me gusta los idiomas.', 'gustan'),
    ('Me gustan el español.', 'gusta'),
    ('No me gusta las conversaciones rápidas.', 'gustan'),
    ('Me cuesta las conversaciones rápidas.', 'cuestan'),
    ('Me cuestan hablar español.', 'cuesta'),
    ('Me gustan aprender español.', 'gusta'),
    ('Te recomiendo practicas español.', 'practicar'),
    ('Te recomiendo que practicas español.', 'practiques'),
    ('Puedes escuchas la radio.', 'escuchar'),
    ('Hay que estudias cada día.', 'estudiar'),
])
def test_errors(text, replacement):
    issues = a2_checker.detect(text)
    assert len(issues) == 1
    assert issues[0]['replacement'] == replacement
    assert text[issues[0]['start']:issues[0]['end']] == issues[0]['original']


@pytest.mark.parametrize('text', [
    'Me cuestan los idiomas.', 'Me gusta el vocabulario y las conversaciones.',
    'Me gustan el vocabulario y las conversaciones.', 'Me gusta leer y escribir.',
    'Te recomiendo que practiques español.', 'Te recomiendo practicar español.',
    'Te recomiendo este libro.', 'Te recomiendo prácticas de conversación.',
    'Puedes escuchar la radio.', 'Hay que aprender poco a poco.',
    'Me gustan los libros que me has recomendado.',
    'Me gusta el español .', 'Me gustan los idiomas. Me cuesta hablar español.',
    'Me gusta que hables español.', 'Me gustan María y Ana.',
    'Me gustan cantar los pájaros y bailar las hojas.',
    'Me gustan   .', 'Me gusta',
])
def test_valid_or_ambiguous_constructions_are_not_flagged(text):
    assert a2_checker.detect(text) == []


def test_paragraph_offsets_and_local_fallback(monkeypatch):
    monkeypatch.setattr(providers, 'correct', lambda text: Correction(status='unavailable', original=text))
    monkeypatch.setattr(a2_checker.textbook, 'search', lambda *a, **kw: [])
    text = 'Soy Ana 😊. Me gusta los idiomas. Me cuestan hablar. Te recomiendo practicas cada día.'
    result = a2_checker.check(text)
    assert result['suggested'] == 'Soy Ana 😊. Me gustan los idiomas. Me cuesta hablar. Te recomiendo practicar cada día.'
    assert len(result['grammar_check']['issues']) == 3
    assert result['status'] == 'partial'
    assert result['original'] == text


def test_barto_cannot_change_meaning_or_undo_rules(monkeypatch):
    monkeypatch.setattr(providers, 'correct', lambda text: Correction(status='suggestions', original=text, suggested='Me gustan los idiomas.'))
    result = a2_checker.check('Me cuestan los idiomas.')
    assert result['suggested'] is None
    assert result['grammar_check']['model_status'] == 'rejected'
    monkeypatch.setattr(providers, 'correct', lambda text: Correction(status='suggestions', original=text, suggested='Me gusta los idiomas.'))
    result = a2_checker.check('Me gusta los idiomas.')
    assert result['suggested'] == 'Me gustan los idiomas.'
    assert result['status'] == 'partial'


def test_barto_spelling_and_rules_combine(monkeypatch):
    def correction(text):
        assert text == 'Me gustan los idiomas. Practico cada dia.'
        return Correction(status='suggestions', original=text, suggested=text.replace('dia', 'día'), processed=2)
    monkeypatch.setattr(providers, 'correct', correction)
    assert a2_checker.check('Me gusta los idiomas. Practico cada dia.')['suggested'] == 'Me gustan los idiomas. Practico cada día.'


def test_irrelevant_ocr_not_cited(monkeypatch):
    monkeypatch.setattr(a2_checker.textbook, 'search', lambda *a, **kw: [{'source': 'book.pdf', 'page': 2, 'text': 'ABCDE gustar garbled text'}])
    assert a2_checker.references('gustar') == []
    monkeypatch.setattr(a2_checker.textbook, 'search', lambda *a, **kw: [{'source': 'book.pdf', 'page': 36, 'text': 'Nos gustan los deportes.'}])
    assert a2_checker.references('gustar') == [{'source': 'book.pdf', 'page': 36, 'excerpt': 'Nos gustan los deportes'}]

import pytest
import sys
import types

st_stub = types.ModuleType("streamlit")

class _FakeCache:
    def __call__(self, fn):
        return fn

st_stub.cache_resource = _FakeCache()
st_stub.set_page_config = lambda **kw: None
st_stub.title = lambda *a, **kw: None
st_stub.text_area = lambda *a, **kw: ""
st_stub.columns = lambda n: [types.SimpleNamespace(
    __enter__=lambda s: s, __exit__=lambda s, *a: None
)] * n
st_stub.selectbox = lambda *a, **kw: (list(kw.get("options", a[1]))[0] if a[1:] else "")
st_stub.checkbox = lambda *a, **kw: kw.get("value", False)
st_stub.button = lambda *a, **kw: False
st_stub.caption = lambda *a, **kw: None
st_stub.warning = lambda *a, **kw: None
st_stub.subheader = lambda *a, **kw: None
st_stub.write = lambda *a, **kw: None
st_stub.markdown = lambda *a, **kw: None
st_stub.progress = lambda *a, **kw: None
st_stub.error = lambda *a, **kw: None
st_stub.success = lambda *a, **kw: None
st_stub.stop = lambda: None
sys.modules["streamlit"] = st_stub

from app import count_tokens, detect_task, extract_constraints, estimate_basic, estimate_smart

def test_count_tokens_empty_string():
    assert count_tokens("") == 0

def test_count_tokens_single_word():
    assert count_tokens("hello") >= 1

def test_count_tokens_increases_with_length():
    assert count_tokens("hi " * 50) > count_tokens("hi")

def test_detect_task_summarization():
    assert detect_task("Please summarize this article") == "summarization"

def test_detect_task_explanation():
    assert detect_task("Explain how neural networks work") == "explanation"

def test_detect_task_code():
    assert detect_task("Write python code to sort a list") == "code"

def test_detect_task_list():
    assert detect_task("Give me a list of planets") == "list"

def test_detect_task_general():
    assert detect_task("What is the weather today?") == "general"

def test_extract_constraints_word_limit():
    assert extract_constraints("Summarize this in 100 words") == int(100 * 1.3)

def test_extract_constraints_sentence_limit():
    assert extract_constraints("Explain in 5 sentences") == 5 * 20

def test_extract_constraints_no_constraint():
    assert extract_constraints("Tell me about black holes") is None

def test_estimate_basic_concise():
    assert estimate_basic(100, "Concise") == 50

def test_estimate_basic_normal():
    assert estimate_basic(100, "Normal") == 100

def test_estimate_basic_detailed():
    assert estimate_basic(100, "Detailed") == 180

def test_estimate_basic_code():
    assert estimate_basic(100, "Code") == 80

def test_estimate_basic_notebook():
    assert estimate_basic(100, "Notebook") == 300

def test_estimate_smart_uses_constraint():
    _, _, method = estimate_smart(200, "Answer in 50 words", "Normal")
    assert method == "constraint-based"

def test_estimate_smart_summarization():
    tokens, task, method = estimate_smart(200, "Summarize the document", "Normal")
    assert task == "summarization" and method == "task-based"

def test_estimate_smart_general_fallback():
    _, task, method = estimate_smart(100, "What is 2+2?", "Normal")
    assert method == "fallback" and task == "general"

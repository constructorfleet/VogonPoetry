import pytest
from vogonpoetry.tags.tag_score import cosine_similarity, process_tag, TagScore
from vogonpoetry.tags.tag_vector import TagVector

def test_cosine_similarity_identical():
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)
    assert cosine_similarity([0.0, 1.0], [0.0, 1.0]) == pytest.approx(1.0)

def test_cosine_similarity_orthogonal():
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)

def test_cosine_similarity_opposite():
    assert cosine_similarity([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(-1.0)

def test_process_tag_returns_tag_score():
    tag = TagVector(vector=[1.0, 0.0], id="tag1", name="Tag 1.0", description="A test tag", parent=None, sub_tags=[])
    user_vector = [1.0, 0.0]
    scored = process_tag(tag, user_vector)
    assert isinstance(scored, TagScore)
    assert scored.score == pytest.approx(1.0)
import pytest
from vogonpoetry.utils.pattern_matcher import PatternMatcher, MatcherString

@pytest.mark.parametrize(
    "pattern,input_str,expected",
    [
        # Regex pattern
        (MatcherString(r"r'\d{3}-\d{2}-\d{4}'"), "123-45-6789", True),
        (MatcherString(r"r'\d{3}-\d{2}-\d{4}'"), "abc-def-ghij", False),
        # Glob pattern
        (MatcherString("foo*bar"), "foobazbar", True),
        (MatcherString("foo*bar"), "foobar", True),
        (MatcherString("foo*bar"), "foo_bar", True),
        (MatcherString("foo*bar"), "foobazbaz", False),
        (MatcherString("file?.txt"), "file1.txt", True),
        (MatcherString("file?.txt"), "file12.txt", False),
        # Snake case pattern
        (MatcherString("snake_case"), "snake_case", True),
        (MatcherString("snake_case"), "snake_case_pace", True),
        (MatcherString("snake_case"), "snakecase", False),
        (MatcherString("snake_case"), "SNAKE_CASE", False),
        (MatcherString("snake_case"), "snake-case", False),
        (MatcherString("snake_case"), "case_snake", False),
        (MatcherString("snake_case"), "case_of_snake", False),
        (MatcherString("snake_case"), "dog_case", False),
    ]
)
def test_patternmatcher_matches(pattern, input_str, expected):
    matcher = PatternMatcher(pattern=pattern)
    assert matcher.matches(input_str) == expected

def test_patternmatcher_regex_quotes():
    # Should match regex with double quotes
    matcher = PatternMatcher(pattern=MatcherString('r"foo.*bar"'))
    assert matcher.matches("foo123bar")
    assert not matcher.matches("barfoo")

def test_patternmatcher_glob_special_chars():
    matcher = PatternMatcher(pattern=MatcherString("data[0-9].csv"))
    assert matcher.matches("data1.csv")
    assert matcher.matches("data9.csv")
    assert not matcher.matches("data10.csv")

def test_patternmatcher_snake_case_partial():
    matcher = PatternMatcher(pattern=MatcherString("foo_bar"))
    assert matcher.matches("the_foo_bar_baz")
    assert not matcher.matches("thefoobarbaz")
    assert not matcher.matches("barfoo")

def test_patternmatcher_repr_and_config():
    matcher = PatternMatcher(pattern=MatcherString("foo_bar"))
    assert matcher.pattern == "foo_bar"
    assert matcher.model_config.get("arbitrary_types_allowed") is True
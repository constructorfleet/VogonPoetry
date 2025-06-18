import pytest
from typing import Any, List
from pydantic import ValidationError
from regex import P
from vogonpoetry.utils.filter_config import FilterConfig, FilterUtility
from vogonpoetry.utils.pattern_matcher import PatternMatcher,MatcherString

def test_filterconfig_whitelist_filters_items():
    whitelist = [PatternMatcher(pattern=MatcherString("a")), PatternMatcher(pattern=MatcherString("b")), PatternMatcher(pattern=MatcherString("c"))]
    config = FilterConfig(whitelist=whitelist)
    items = ["a", "b", "c"]
    # All DummyMatcher(True) will match all items
    filtered = config.filter(items)
    assert filtered == items

def test_filterconfig_blacklist_filters_items():
    blacklist = [PatternMatcher(pattern=MatcherString("a")), PatternMatcher(pattern=MatcherString("b")), PatternMatcher(pattern=MatcherString("c"))]
    config = FilterConfig(blacklist=blacklist)
    items = ["a", "b", "c"]
    # All items should be filtered out
    filtered = config.filter(items)
    assert filtered == []

def test_filterconfig_no_list_returns_all():
    config = FilterConfig()
    items = ["a", "b"]
    filtered = config.filter(items)
    assert filtered == items

def test_filterconfig_exclusive_fields_raises():
    with pytest.raises(ValidationError):
        FilterConfig(whitelist=[PatternMatcher(pattern=MatcherString("1"))], blacklist=[PatternMatcher(pattern=MatcherString("2"))])

def test_filterutility_filters_multiple_configs():
    # First filter keeps all, second filter removes all
    filters = [
        FilterConfig(whitelist=[PatternMatcher(pattern=MatcherString(".*"))]),
        FilterConfig(blacklist=[PatternMatcher(pattern=MatcherString(".*"))])
    ]
    items = ["x", "y"]
    filtered = FilterUtility.filter_items(filters, items)
    assert filtered == []

def test_filterconfig_with_custom_prop_fn():
    class Obj:
        def __init__(self, val): self.val = val
    items = [Obj("foo"), Obj("bar")]
    # Only match if value is "foo"
    class MatchFoo:
        def matcher(self, value): return value == "foo"
    config = FilterConfig(whitelist=[PatternMatcher(pattern=MatcherString("foo"))])
    filtered = config.filter(items, prop_fn=lambda o: o.val)
    assert filtered == [items[0]]
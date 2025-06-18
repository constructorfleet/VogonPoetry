from typing import Any, Callable, Generic, TypeVar, Optional, MutableSequence
from pydantic import BaseModel, Field, model_validator

from vogonpoetry.utils.pattern_matcher import PatternMatcher

T = TypeVar('T')

def default_prop_fn(item: Any) -> str:
    return str(item)

class FilterConfig(BaseModel):
    whitelist: Optional[MutableSequence[PatternMatcher]] = Field(default=None, description="Allowlist patterns.")
    blacklist: Optional[MutableSequence[PatternMatcher]] = Field(default=None, description="Blocklist patterns.")

    @model_validator(mode="after")
    def check_exclusive_fields(self) -> "FilterConfig":
        if self.whitelist and self.blacklist:
            raise ValueError("Only one of 'whitelist' or 'blacklist' can be set, not both.")
        return self
    
    def filter(self, items: MutableSequence[T], prop_fn: Callable[[T], str] = default_prop_fn) -> MutableSequence[T]:
        if self.whitelist:
            return [item for item in items if any(matcher.matcher(prop_fn(item)) for matcher in self.whitelist)]
        elif self.blacklist:
            return [item for item in items if not any(matcher.matcher(prop_fn(item)) for matcher in self.blacklist)]
        else:
            return items

class FilterUtility(Generic[T]):
    @staticmethod
    def filter_items(filters: MutableSequence[FilterConfig], items: MutableSequence[T], prop_fn: Callable[[T], str] = default_prop_fn) -> MutableSequence[T]:
        for filter_config in filters:
            items = filter_config.filter(items, prop_fn)
        return items
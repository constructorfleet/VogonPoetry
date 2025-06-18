import re
import fnmatch
from typing import Callable, Union
from pydantic import BaseModel, Field, field_validator

Matcher = Callable[[str], bool]

class MatcherString(str):
    pass

class MatchMode(str):
    regex = "regex"
    glob = "glob"
    snake = "snake"

class PatternMatcher(BaseModel):
    pattern: MatcherString = Field(..., description="A regex (r'...'), glob (*foo*), or snake_case string")

    model_config = {
        "arbitrary_types_allowed": True,
    }

    @field_validator("pattern", mode="after")
    def resolve_pattern(cls, value: str) -> str:
        return value

    def model_post_init(self, __context):
        self._matcher = self._build_matcher(self.pattern)

    def _build_matcher(self, value: str) -> Matcher:
        if value.startswith("r'") or value.startswith('r"'):
            # Regex pattern
            pattern = value[2:-1]
            regex = re.compile(pattern)
            return lambda s: regex.search(s) is not None
        elif value.startswith("/") and value.endswith("/"):
            # Regex pattern with slashes
            pattern = value[1:-1]
            regex = re.compile(pattern)
            return lambda s: regex.search(s) is not None
        elif "*" in value or "?" in value or "[" in value:
            # Glob pattern
            return lambda s: fnmatch.fnmatch(s, value)
        else:
            # Snake case match
            return lambda s: value in s
        
    def matches(self, value: str) -> bool:
        return self._matcher(value)
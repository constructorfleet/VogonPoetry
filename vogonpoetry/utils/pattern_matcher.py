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
    matcher: Matcher = Field(init=False)

    @field_validator("pattern", mode="after")
    def resolve_pattern(cls, value: str) -> str:
        return value

    def model_post_init(self, __context):
        self.matcher = self._build_matcher(self.pattern)

    def _build_matcher(self, value: str) -> Matcher:
        if value.startswith("r'") or value.startswith('r"'):
            # Regex pattern
            pattern = value[2:-1]
            regex = re.compile(pattern)
            return lambda s: bool(regex.search(s))
        elif "*" in value or "?" in value or "[" in value:
            # Glob pattern
            return lambda s: fnmatch.fnmatch(s, value)
        else:
            # Snake case match
            canonical = value.replace("_", "").lower()
            return lambda s: canonical in s.replace("_", "").lower()
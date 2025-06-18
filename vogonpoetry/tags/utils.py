
from typing import Callable, Generic, MutableMapping, MutableSequence, Optional, Sequence, TypeVar, Union, cast

from vogonpoetry.tags.tag import TTag, Tag
from vogonpoetry.tags.tag_score import TagScore
from vogonpoetry.tags.tag_vector import TagVector

TagIn = TypeVar("TagIn", bound=Tag)
TagOut = TypeVar("TagOut", bound=Tag)

class TagUtilities(Generic[TagIn, TagOut]):
    @staticmethod
    def gather_tags(all_tags: MutableMapping[str, TagIn], tags: Sequence[TagIn], parent: Optional[TagIn] = None) -> MutableMapping[str, TagIn]:
        """Recursively extract tags from a tag object."""
        for tag in tags:
            if isinstance(tag, dict):
                if tag.get("parent") is not None:
                    tag["parent"] = all_tags.get(tag["parent"])
                    all_tags[tag["id"]] = tag
                    if tag.get("sub_tags") is not None:
                        all_tags = TagUtilities[TagIn, TagOut].gather_tags(all_tags, tag["sub_tags"], tag)
            else:
                if isinstance(tag, Tag) and parent is not None and isinstance(parent, Tag):
                    tag.parent = parent
                all_tags[tag.id] = tag
                if tag.sub_tags is not None:
                    all_tags = TagUtilities[TagIn, TagOut].gather_tags(all_tags, tag.sub_tags, tag)
        return all_tags

    @staticmethod
    def flatten_tags(tags: Sequence[TagIn]) -> list[TagIn]:
        """Flatten a nested list of tags into a single list."""
        flat_list: list[TagIn] = []
        for tag in tags:
            flat_list.append(tag)
            if isinstance(tag, dict):
                if tag.get("sub_tags") is not None:
                    flat_list.extend(TagUtilities[TagIn, TagOut].flatten_tags(tag["sub_tags"])) # type: ignore
            else:
                if tag.sub_tags is not None:
                    flat_list.extend(TagUtilities[TagIn, TagOut].flatten_tags(tag.sub_tags)) # type: ignore
        return flat_list
    
    @staticmethod
    def build_tag_map(tags: Sequence[TagIn], factory: Callable[[TagIn], TagOut]) -> dict[str, TagOut]:
        flat_tags = TagUtilities[TagIn, TagOut].flatten_tags(tags)
        tag_map = {tag.id: factory(tag) for tag in flat_tags}

        for tag in flat_tags:
            typed = tag_map[tag.id]
            if tag.parent and tag.parent.id in tag_map:
                parent = tag_map[tag.parent.id]
                if parent.sub_tags is None:
                    parent.sub_tags = cast(MutableSequence[TagOut], [])
                if typed.id not in [t.id for t in parent.sub_tags]:
                    parent.sub_tags.append(typed)
                typed.parent = parent

        return tag_map

    @staticmethod
    def vectored_tag_map(tags: Sequence[TagIn], embed_func: Callable[[TagIn], list[float]]) -> dict[str, TagVector]:
        return cast(dict[str, TagVector], TagUtilities[TagIn, TagVector].build_tag_map(
            tags,
            lambda tag: TagVector(
                id=tag.id,
                name=tag.name,
                description=tag.description,
                vector=embed_func(tag),
                parent=None,
                sub_tags=None
            )
        ))

    @staticmethod
    def scored_tag_map(tags: Sequence[TagIn], score_func: Callable[[TagIn], float]) -> dict[str, TagScore]:
        return cast(dict[str, TagScore], TagUtilities[TagIn, TagScore].build_tag_map(
            tags,
            lambda tag: TagScore(
                id=tag.id,
                name=tag.name,
                description=tag.description,
                score=score_func(tag),
                parent=None,
                sub_tags=None
            )
        ))
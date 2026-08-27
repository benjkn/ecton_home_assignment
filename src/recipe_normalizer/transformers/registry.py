"""Registered recipe transformers."""

from recipe_normalizer.transformers.base import Transformer
from recipe_normalizer.transformers.identity import IdentityTransformer
from recipe_normalizer.transformers.metric import MetricTransformer

_TRANSFORMERS: dict[str, Transformer] = {
    "metric": MetricTransformer(),
    "none": IdentityTransformer(),
}

AVAILABLE_TRANSFORMS = tuple(_TRANSFORMERS)


def get_transformer(name: str) -> Transformer:
    try:
        return _TRANSFORMERS[name]
    except KeyError as exc:
        known = ", ".join(AVAILABLE_TRANSFORMS)
        raise ValueError(f"Unknown transform {name!r}. Choose one of: {known}") from exc

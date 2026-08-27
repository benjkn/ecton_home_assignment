"""Identity transformer: schema only, no unit conversion."""

from recipe_normalizer.models import Recipe


class IdentityTransformer:
    name = "none"

    def apply(self, recipe: Recipe) -> Recipe:
        return recipe

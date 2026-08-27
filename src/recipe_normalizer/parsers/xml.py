"""XML recipe parser."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from recipe_normalizer.exceptions import ParseError
from recipe_normalizer.models import Recipe, recipe_from_mapping


def _text(element: ET.Element | None) -> str | None:
    if element is None or element.text is None:
        return None
    text = element.text.strip()
    return text or None


def _child_text(parent: ET.Element, tag: str) -> str | None:
    return _text(parent.find(tag))


def _preparations_from_xml(root: ET.Element) -> list[str] | str | None:
    block = root.find("preparations")
    if block is not None:
        children = list(block)
        if children:
            return [_text(child) or "" for child in children]
        return _text(block)
    steps = [_text(el) or "" for el in root.findall("preparation")]
    steps += [_text(el) or "" for el in root.findall("step")]
    return steps or None


def _ingredients_from_xml(root: ET.Element) -> list[dict[str, str]]:
    nodes = list(root.findall("ingredients")) + list(root.findall("ingredient"))
    ingredients: list[dict[str, str]] = []
    for node in nodes:
        item = _child_text(node, "item") or (node.get("item") or "").strip()
        quantity = _child_text(node, "quantity")
        if quantity is None:
            quantity = node.get("quantity")
        mapping: dict[str, str] = {}
        if item:
            mapping["item"] = item
        if quantity is not None:
            mapping["quantity"] = quantity
        unit = _child_text(node, "unit")
        if unit is None:
            unit = (node.get("unit") or "").strip() or None
        if unit:
            mapping["unit"] = unit
        comment = _child_text(node, "comment")
        if comment is None:
            comment = (node.get("comment") or "").strip() or None
        if comment:
            mapping["comment"] = comment
        ingredients.append(mapping)
    return ingredients


def _recipe_from_element(root: ET.Element) -> Recipe:
    mapping = {
        "name": _child_text(root, "name") or (root.get("name") or "").strip(),
        "ingredients": _ingredients_from_xml(root),
        "preparations": _preparations_from_xml(root),
    }
    return recipe_from_mapping(mapping)


class XmlParser:
    def parse(self, path: Path) -> list[Recipe]:
        try:
            tree = ET.parse(path)
        except ET.ParseError as exc:
            raise ParseError(f"Invalid XML: {exc}", path) from exc
        root = tree.getroot()
        tag = root.tag.lower().rsplit("}", 1)[-1]
        try:
            if tag in {"recipes", "collection"}:
                children = [child for child in list(root) if child.tag.rsplit("}", 1)[-1].lower() in {"recipe", "root"}]
                if not children:
                    children = list(root)
                return [_recipe_from_element(child) for child in children]
            return [_recipe_from_element(root)]
        except ParseError as exc:
            raise ParseError(str(exc), path) from exc

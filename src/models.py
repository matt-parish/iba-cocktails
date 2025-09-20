from dataclasses import dataclass
from typing import List, Optional
import json


@dataclass
class Ingredient:
    """Represents a single cocktail ingredient with measurement."""
    amount: str
    name: str

    def to_dict(self) -> dict:
        return {
            "amount": self.amount,
            "name": self.name
        }


@dataclass
class Cocktail:
    """Represents a complete cocktail recipe."""
    name: str
    category: str
    ingredients: List[Ingredient]
    method: str
    garnish: str
    views: str
    url: str
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    image_path: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category,
            "ingredients": [ingredient.to_dict() for ingredient in self.ingredients],
            "method": self.method,
            "garnish": self.garnish,
            "views": self.views,
            "url": self.url,
            "video_url": self.video_url,
            "image_url": self.image_url,
            "image_path": self.image_path
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert cocktail to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


@dataclass
class CocktailSummary:
    """Represents basic cocktail info from the list page."""
    name: str
    category: str
    views: str
    url: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category,
            "views": self.views,
            "url": self.url
        }
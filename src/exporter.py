import json
import logging
from pathlib import Path
from typing import List
from models import Cocktail


class JSONExporter:
    """Handles exporting cocktail data to JSON format."""

    def __init__(self, output_dir: str = "data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def export_cocktails(self, cocktails: List[Cocktail], filename: str = "cocktails.json") -> str:
        """Export list of cocktails to JSON file."""
        output_path = self.output_dir / filename
        
        # Convert cocktails to dictionaries
        cocktails_data = {
            "total_cocktails": len(cocktails),
            "scraped_date": None,  # Will be set in main script
            "cocktails": [cocktail.to_dict() for cocktail in cocktails]
        }

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(cocktails_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported {len(cocktails)} cocktails to {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {e}")
            raise

    def export_summary(self, cocktails: List[Cocktail], filename: str = "cocktails_summary.json") -> str:
        """Export a summary of cocktails (names and categories only)."""
        output_path = self.output_dir / filename
        
        summary_data = {
            "total_cocktails": len(cocktails),
            "categories": {},
            "cocktails_by_category": {}
        }

        # Group by category
        for cocktail in cocktails:
            category = cocktail.category or "Unknown"
            if category not in summary_data["categories"]:
                summary_data["categories"][category] = 0
                summary_data["cocktails_by_category"][category] = []
            
            summary_data["categories"][category] += 1
            summary_data["cocktails_by_category"][category].append({
                "name": cocktail.name,
                "views": cocktail.views,
                "url": cocktail.url
            })

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported summary to {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error exporting summary: {e}")
            raise
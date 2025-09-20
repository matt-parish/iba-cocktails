#!/usr/bin/env python3
"""
IBA Cocktails Scraper
Scrapes all cocktail details from the International Bartenders Association website.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from scrapers import IBAScraper
from exporter import JSONExporter
from utils import setup_logging, ProgressTracker


def main():
    """Main entry point for the scraper."""
    
    parser = argparse.ArgumentParser(description="Scrape IBA cocktails data")
    parser.add_argument("--output", "-o", default="data/cocktails.json",
                       help="Output JSON file path (default: data/cocktails.json)")
    parser.add_argument("--delay", "-d", type=float, default=1.0,
                       help="Delay between requests in seconds (default: 1.0)")
    parser.add_argument("--no-images", action="store_true",
                       help="Skip downloading images (default: download images)")
    parser.add_argument("--log-level", default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level (default: INFO)")
    parser.add_argument("--log-file", help="Log file path (optional)")
    parser.add_argument("--limit", type=int,
                       help="Limit number of cocktails to scrape (for testing)")
    
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging(args.log_level, args.log_file)
    
    try:
        logger.info("=" * 50)
        logger.info("IBA COCKTAILS SCRAPER STARTED")
        logger.info("=" * 50)
        logger.info(f"Output file: {args.output}")
        logger.info(f"Request delay: {args.delay} seconds")
        logger.info(f"Download images: {not args.no_images}")
        if args.limit:
            logger.info(f"Limiting to: {args.limit} cocktails")
        
        # Initialize scraper
        scraper = IBAScraper(delay=args.delay, download_images=not args.no_images)
        
        # Initialize progress tracker
        tracker = ProgressTracker()
        
        # Get list of cocktails to scrape from all pages
        logger.info("Fetching cocktail list from all pages...")
        cocktail_summaries = scraper.get_all_cocktail_pages()
        
        if not cocktail_summaries:
            logger.error("No cocktails found! Check the website structure.")
            sys.exit(1)
        
        # Apply limit if specified
        if args.limit and args.limit < len(cocktail_summaries):
            cocktail_summaries = cocktail_summaries[:args.limit]
            logger.info(f"Limited to first {args.limit} cocktails")
        
        tracker.set_total(len(cocktail_summaries))
        
        # Scrape detailed information for each cocktail
        cocktails = []
        for summary in cocktail_summaries:
            tracker.start_cocktail(summary.name)
            
            cocktail = scraper.scrape_cocktail_details(summary)
            if cocktail:
                cocktails.append(cocktail)
                tracker.complete_cocktail(success=True)
            else:
                tracker.complete_cocktail(success=False)
        
        # Export results
        logger.info("Exporting results...")
        exporter = JSONExporter()
        
        # Add scraping metadata
        if cocktails:
            # Update the exporter to include timestamp
            output_path = Path(args.output)
            output_path.parent.mkdir(exist_ok=True)
            
            cocktails_data = {
                "metadata": {
                    "total_cocktails": len(cocktails),
                    "scraped_date": datetime.now().isoformat(),
                    "scraper_version": "1.0",
                    "source_url": "https://iba-world.com/cocktails/all-cocktails/"
                },
                "cocktails": [cocktail.to_dict() for cocktail in cocktails]
            }
            
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(cocktails_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results exported to: {output_path}")
            
            # Export summary as well
            summary_path = output_path.parent / "cocktails_summary.json"
            exporter.export_summary(cocktails, summary_path.name)
        
        # Print final summary
        tracker.print_summary()
        
        logger.info("Scraping completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Scraping failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
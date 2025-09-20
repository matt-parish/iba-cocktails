# IBA Cocktails Scraper

A comprehensive Python scraper to extract all cocktail details from the International Bartenders Association website. Features dynamic pagination discovery, image downloading, and HTML-to-markdown conversion for reliable parsing.

A pre-prepared JSON of [cocktails available as of September 2025](https://github.com/matt-parish/iba-cocktails/blob/main/data/cocktails.json) is available.

## Features

- **Complete data extraction**: All 102+ cocktails with ingredients, methods, garnish, categories, views, and video links
- **Dynamic pagination**: Automatically discovers all pages without hard-coding page limits
- **Image downloading**: Downloads cocktail images and references them in the JSON output
- **Robust parsing**: Uses HTML-to-markdown conversion resistant to DOM structure changes
- **Future-proof**: Automatically adapts when new cocktails are added to the website
- **Rate limiting**: Respectful delays between requests (configurable)
- **Progress tracking**: Comprehensive logging with success rates and timing
- **JSON export**: Clean structured data with metadata
- **Error handling**: Graceful failure handling with detailed logging
- **CLI interface**: Multiple options for customization

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py
```

The scraped data will be saved to `data/cocktails.json` with a summary in `data/cocktails_summary.json`.

### Options

- `--output`, `-o`: Specify output file path (default: `data/cocktails.json`)
- `--delay`, `-d`: Set delay between requests in seconds (default: 1.0)
- `--no-images`: Skip downloading images (default: downloads images)
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `--log-file`: Save logs to file
- `--limit`: Limit number of cocktails to scrape (for testing)

### Examples

```bash
# Basic usage - scrape all cocktails with images
python src/main.py

# Scrape without downloading images
python src/main.py --no-images

# Custom output file and faster scraping
python src/main.py --output my_cocktails.json --delay 0.5

# Scrape only first 10 cocktails for testing
python src/main.py --limit 10 --log-level DEBUG

# Save logs to file
python src/main.py --log-file logs/scraping.log
```

## Data Structure

Each cocktail includes:
- **Name**: Official cocktail name
- **Category**: "The Unforgettables", "Contemporary Classics", or "New Era"
- **Ingredients**: List with amounts and ingredient names
- **Method**: Step-by-step preparation instructions
- **Garnish**: Garnish and serving instructions
- **Views**: Popularity metrics from the website
- **URL**: Direct link to the cocktail page
- **Video URL**: YouTube instructional video (if available)
- **Image URL**: Direct link to the cocktail image
- **Image Path**: Local path to downloaded image file

## Technical Details

- **Dynamic pagination discovery**: Automatically finds all available pages without hard-coding limits
- **Image downloading**: Finds and downloads cocktail-specific images to local storage
- **HTML-to-Markdown conversion**: More reliable than DOM parsing for extracting structured data
- **Regex-based extraction**: Robust text parsing for ingredients, methods, and garnish
- **Respectful scraping**: Built-in delays and proper User-Agent headers
- **Comprehensive error handling**: Continues scraping even if individual cocktails fail
- **Future-proof**: Adapts automatically when new cocktails are added to the website

## Project Structure

- `src/` - Source code
  - `models.py` - Data models and structures
  - `scrapers.py` - Web scraping logic with pagination and image handling
  - `exporter.py` - JSON export utilities
  - `utils.py` - Logging and progress tracking
  - `main.py` - Main CLI application
- `data/` - Output directory for scraped JSON data
- `images/` - Downloaded cocktail images (excluded from git)
- `requirements.txt` - Python dependencies

## Output

The scraper generates:
- `data/cocktails.json` - Complete cocktail database with metadata
- `data/cocktails_summary.json` - Summary statistics
- `images/` - Directory containing all cocktail images (102+ files)
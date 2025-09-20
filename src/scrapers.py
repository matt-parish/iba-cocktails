import requests
from bs4 import BeautifulSoup
import html2text
from typing import List, Optional
import re
import time
import logging
import os
from urllib.parse import urljoin, urlparse

from models import Cocktail, CocktailSummary, Ingredient


class IBAScraper:
    """Scraper for the IBA World cocktails website."""

    def __init__(self, base_url: str = "https://iba-world.com", delay: float = 1.0, download_images: bool = True):
        self.base_url = base_url
        self.delay = delay
        self.download_images = download_images
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        })
        self.logger = logging.getLogger(__name__)
        
        # Create images directory if downloading images
        if self.download_images:
            self.images_dir = "images"
            os.makedirs(self.images_dir, exist_ok=True)

    def _get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page."""
        try:
            self.logger.debug(f"Fetching: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            # Add delay to be respectful
            time.sleep(self.delay)
            
            return BeautifulSoup(response.content, 'html.parser')
        except requests.HTTPError as e:
            if response.status_code == 404:
                self.logger.debug(f"Page not found (404): {url}")
            else:
                self.logger.error(f"HTTP error fetching {url}: {e}")
            return None
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None

    def _find_and_download_cocktail_image(self, cocktail_url: str, cocktail_name: str) -> tuple[Optional[str], Optional[str]]:
        """Find and download the cocktail image. Returns (image_url, local_path) tuple."""
        if not self.download_images:
            return None, None
            
        try:
            # Get the cocktail page
            soup = self._get_page(cocktail_url)
            if not soup:
                return None, None
            
            # Extract cocktail slug from URL for matching
            cocktail_slug = cocktail_url.split('/iba-cocktail/')[-1].rstrip('/')
            
            # Find all images
            images = soup.find_all('img')
            
            best_image_url = None
            
            # Look for images that contain the cocktail name in the filename
            for img in images:
                src = img.get('src', '')
                if not src:
                    continue
                    
                # Check if the cocktail slug appears in the image URL
                if cocktail_slug.replace('-', '_') in src.lower() or cocktail_slug in src.lower():
                    best_image_url = src
                    self.logger.debug(f"Found matching image for {cocktail_name}: {src}")
                    break
            
            # Fallback: look for images with wp-image class (main content images)
            if not best_image_url:
                for img in images:
                    src = img.get('src', '')
                    classes = img.get('class', [])
                    
                    if 'wp-image' in ' '.join(classes) and 'iba-cocktail' in src.lower():
                        best_image_url = src
                        self.logger.debug(f"Found fallback image for {cocktail_name}: {src}")
                        break
            
            if not best_image_url:
                self.logger.warning(f"No image found for {cocktail_name}")
                return None, None
            
            # Download the image
            return self._download_image(best_image_url, cocktail_name)
            
        except Exception as e:
            self.logger.error(f"Error finding/downloading image for {cocktail_name}: {e}")
            return None, None

    def _download_image(self, image_url: str, cocktail_name: str) -> tuple[str, Optional[str]]:
        """Download an image and return (image_url, local_path) tuple."""
        try:
            # Get the file extension from the URL
            parsed_url = urlparse(image_url)
            filename = os.path.basename(parsed_url.path)
            
            # If no extension, default to .webp (most IBA images are webp)
            if '.' not in filename:
                filename = f"{cocktail_name.replace(' ', '_').lower()}.webp"
            
            # Sanitize filename
            safe_filename = re.sub(r'[^\w\-_.]', '_', filename)
            local_path = os.path.join(self.images_dir, safe_filename)
            
            # Skip download if file already exists
            if os.path.exists(local_path):
                self.logger.debug(f"Image already exists: {local_path}")
                return image_url, local_path
            
            # Download the image
            self.logger.debug(f"Downloading image: {image_url}")
            response = self.session.get(image_url)
            response.raise_for_status()
            
            # Save the image
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            self.logger.debug(f"Saved image: {local_path}")
            return image_url, local_path
            
        except Exception as e:
            self.logger.error(f"Error downloading image {image_url}: {e}")
            return image_url, None

    def get_cocktail_list(self, page_number: int = 1) -> List[CocktailSummary]:
        """Scrape a specific page of cocktails for all cocktail links."""
        if page_number == 1:
            cocktails_url = f"{self.base_url}/cocktails/all-cocktails/"
        else:
            cocktails_url = f"{self.base_url}/cocktails/all-cocktails/page/{page_number}/"
            
        soup = self._get_page(cocktails_url)
        
        if not soup:
            return []

        cocktails = []
        
        # Find all cocktail links - they follow pattern /iba-cocktail/cocktail-name/
        cocktail_links = soup.find_all('a', href=re.compile(r'/iba-cocktail/[^/]+/$'))
        
        for link in cocktail_links:
            try:
                # Get the full URL
                url = urljoin(self.base_url, link['href'])
                
                # Extract text and split by whitespace to get name, category, and views
                link_text = link.get_text(strip=True)
                if not link_text:
                    continue
                
                # The format is typically "NAME  Category  Views"
                # Split by multiple spaces to separate the parts
                parts = re.split(r'\s{2,}', link_text)  # Split on 2+ consecutive spaces
                
                name = parts[0].strip() if len(parts) > 0 else ""
                category = parts[1].strip() if len(parts) > 1 else ""
                views = parts[2].strip() if len(parts) > 2 else ""
                
                # If splitting by multiple spaces didn't work, try a different approach
                if len(parts) == 1:
                    # Sometimes the text might be "NAMECategoryViews" - let's try regex
                    # Look for pattern: WORD(S) + "The unforgettables" or "Contemporary Classics" or "New Era" + views
                    match = re.match(r'(.+?)(The [Uu]nforgettables|Contemporary Classics|New Era)(.+)', link_text)
                    if match:
                        name = match.group(1).strip()
                        category = match.group(2).strip()
                        views = match.group(3).strip()
                
                if not name:
                    continue
                
                cocktail_summary = CocktailSummary(
                    name=name,
                    category=category,
                    views=views,
                    url=url
                )
                cocktails.append(cocktail_summary)
                self.logger.debug(f"Found cocktail: {name} | {category} | {views}")
                
            except Exception as e:
                self.logger.error(f"Error parsing cocktail link: {e}")
                continue
        
        self.logger.info(f"Found {len(cocktails)} cocktails on page {page_number}")
        return cocktails

    def get_all_cocktail_pages(self) -> List[CocktailSummary]:
        """Scrape all pages of cocktails dynamically until no more pages are found."""
        all_cocktails = []
        page = 1
        
        while True:
            self.logger.info(f"Scraping page {page}")
            page_cocktails = self.get_cocktail_list(page)
            
            if not page_cocktails:
                self.logger.info(f"No cocktails found on page {page}, stopping pagination")
                break
                
            all_cocktails.extend(page_cocktails)
            self.logger.info(f"Page {page}: found {len(page_cocktails)} cocktails (total so far: {len(all_cocktails)})")
            page += 1
            
        self.logger.info(f"Found total of {len(all_cocktails)} cocktails across {page - 1} pages")
        return all_cocktails

    def scrape_cocktail_details(self, cocktail_summary: CocktailSummary) -> Optional[Cocktail]:
        """Scrape detailed information for a single cocktail using markdown conversion."""
        soup = self._get_page(cocktail_summary.url)
        
        if not soup:
            return None

        try:
            # Convert HTML to markdown for easier parsing
            h = html2text.HTML2Text()
            h.ignore_links = True
            h.ignore_images = True
            h.body_width = 0  # Don't wrap lines
            markdown_content = h.handle(str(soup))
            
            # Extract ingredients
            ingredients = []
            ingredients_match = re.search(r'#### Ingredients\s*\n\n(.*?)\n\n#### Method', markdown_content, re.DOTALL | re.IGNORECASE)
            if ingredients_match:
                ingredients_text = ingredients_match.group(1).strip()
                # Parse bullet points - look for lines starting with * or numbers or just plain text
                ingredient_lines = re.findall(r'^\s*[\*\-\+]?\s*(.+)$', ingredients_text, re.MULTILINE)
                
                for line in ingredient_lines:
                    line = line.strip()
                    if line:
                        # Try to parse amount and ingredient name
                        match = re.match(r'^([^a-zA-Z]*(?:\d+(?:\.\d+)?\s*(?:ml|cl|oz|tsp|tbsp|dash|splash|cube|slice|drop|part)|A\s+\w+(?:\s+of)?|Few\s+\w+|Half|One|Two|Three))\s+(.+)$', line, re.IGNORECASE)
                        
                        if match:
                            amount = match.group(1).strip()
                            name = match.group(2).strip()
                        else:
                            # If no clear amount pattern, treat whole line as ingredient name
                            amount = ""
                            name = line
                        
                        if name:
                            ingredients.append(Ingredient(amount=amount, name=name))

            # Extract method
            method = ""
            method_match = re.search(r'#### Method\s*\n\n(.*?)\n\n#### Garnish', markdown_content, re.DOTALL | re.IGNORECASE)
            if method_match:
                method = method_match.group(1).strip()
                # Clean up markdown formatting
                method = re.sub(r'\n+', ' ', method)  # Replace multiple newlines with single space
                method = re.sub(r'\s+', ' ', method)  # Normalize whitespace

            # Extract garnish
            garnish = ""
            garnish_match = re.search(r'#### Garnish\s*\n\n(.*?)(?:\n\n####|\n\n#####|$)', markdown_content, re.DOTALL | re.IGNORECASE)
            if garnish_match:
                garnish = garnish_match.group(1).strip()
                # Clean up markdown formatting
                garnish = re.sub(r'\n+', ' ', garnish)  # Replace multiple newlines with single space
                garnish = re.sub(r'\s+', ' ', garnish)  # Normalize whitespace

            # Look for YouTube video link (in original HTML)
            video_url = None
            video_link = soup.find('a', href=re.compile(r'youtube\.com/watch'))
            if video_link:
                video_url = video_link['href']

            # Find and download cocktail image
            image_url, image_path = self._find_and_download_cocktail_image(cocktail_summary.url, cocktail_summary.name)

            cocktail = Cocktail(
                name=cocktail_summary.name,
                category=cocktail_summary.category,
                ingredients=ingredients,
                method=method,
                garnish=garnish,
                views=cocktail_summary.views,
                url=cocktail_summary.url,
                video_url=video_url,
                image_url=image_url,
                image_path=image_path
            )

            self.logger.debug(f"Scraped details for: {cocktail.name} - {len(ingredients)} ingredients")
            return cocktail

        except Exception as e:
            self.logger.error(f"Error scraping details for {cocktail_summary.name}: {e}")
            return None

    def scrape_all_cocktails(self) -> List[Cocktail]:
        """Scrape all cocktails with full details from all pages."""
        cocktail_summaries = self.get_all_cocktail_pages()
        cocktails = []

        self.logger.info(f"Starting to scrape details for {len(cocktail_summaries)} cocktails")

        for i, summary in enumerate(cocktail_summaries):
            self.logger.info(f"Scraping {i+1}/{len(cocktail_summaries)}: {summary.name}")
            
            cocktail = self.scrape_cocktail_details(summary)
            if cocktail:
                cocktails.append(cocktail)
            else:
                self.logger.warning(f"Failed to scrape details for: {summary.name}")

        self.logger.info(f"Successfully scraped {len(cocktails)} cocktails")
        return cocktails
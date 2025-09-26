# Cocktail Compendium (UK Edition)

## Purpose
This compendium provides a methodology and example for deeply researching and recommending specific bottles for classic cocktails, tailored for a country's availability (in my case, UK). It is designed so others can replicate the process using the provided `cocktails.json` data.

## Research Prompt Used
The following prompt was used in four passes (to avoid overwhelming Gemini with too much research at once):

```
Take the full list of cocktails and their ingredients provided by the user. (2) For each cocktail on the list, conduct targeted research to find specific bottle recommendations for its ingredients. The research will focus on recommendations contextualized by the cocktail name (e.g., "best gin for a Negroni," not just "best gin"). (3) Identify specific brand and variant recommendations from bartending forums, spirits review sites, and community platforms (like Reddit). (4) Verify the general availability of these recommended bottles in the UK by checking major supermarkets and specialist spirits retailers. (5) Rank the recommendations for each ingredient within each cocktail based on the frequency and prominence of mentions from bartenders and enthusiasts. (6) For ingredients where a brand is already specified in the user's query, confirm if it is the standard choice and note any highly-regarded alternatives. (7) Compile the final report with a section on each cocktail, subsection for each ingredient, and a description of the bottles to consider when making this cocktail in the UK.
```

## How to Replicate
1. **Extract Data:** Chunk the cocktail list and ingredients from `cocktails.json`.  I was able ot use 4 chunks.
2. **Apply the Prompt:** For each chunk, using Gemini Deep Research (or similar).
3. **Merge:** Merge the chunked output into a country-specific version for you.

## Example Output Structure
- Each cocktail has a section listing recommended bottles for each ingredient, with notes on why they were chosen and where to buy them in the UK.
- See [`uk/cocktail_compendium_uk_full.md`](uk/cocktail_compendium_uk_full.md) for a full example.

## Data Sources
- `cocktails.json`: The base list of cocktails and ingredients.
- Bartending forums, spirits review sites, Reddit, UK retailer inventories.

## Project Links
- [Main Project README](../../README.md)
- [Full UK Compendium](uk/cocktail_compendium_uk_full.md)
- [Recommended Spirits for UK (YAML)](uk/cocktail_compendium_uk_recommended_spirits.yml)

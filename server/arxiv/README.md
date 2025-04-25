# ArXiv Paper Search Tool

This tool provides a convenient interface to search for academic papers on arXiv by title or ID. It's designed to simplify the research process by quickly retrieving essential information about papers.

## Features

- Search papers using arXiv ID (e.g., 2207.02727v2)
- Search papers by title or keywords in the title (e.g., "SNN", "Neural Networks")
- Returns comprehensive paper information including:
 - Full title
 - Publication date
 - Author list
 - Direct PDF download link
 - Paper abstract/summary

## Usage

### Search by exact arXiv ID:
query="id:2207.02727v2"

### Search by title or keywords:
query="ti:Neural Network"

## Example Output

For each matching paper, the tool returns a structured response containing all relevant metadata, allowing you to quickly assess the paper's relevance to your research without having to visit multiple webpages.

## Implementation Notes

This tool is implemented as a Master Control Program (MCP) server that interfaces directly with arXiv's database to retrieve up-to-date information on published papers. Check config.json for more details.

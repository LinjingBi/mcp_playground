# PDF Tools for MCP Server

Download remote PDFs. The tool saves PDFs to the ~/genai/pdf/ directory by default. This location is automatically created if it doesn't exist.
## Features

- Download remote pdfs

  No authentication is currently supported for PDF downloads
  When providing a filename, it's recommended to construct it from the last part of the URL plus an 8-character random alphanumeric string
  Example: if URL is https://arxiv.org/pdf/paper_id.pdf, filename could be paper_id_7f3a2b9e.pdf

## Implementation Notes

Check config.json for Claude Desktop setup.

## Todo

Improve error handling
Add context handling for better integration
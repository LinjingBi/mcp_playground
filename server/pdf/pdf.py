import os
import httpx
from mcp.server.fastmcp import FastMCP, Context

GENAI_PDF_DIR = os.path.join(os.environ['HOME'], 'genai', 'pdf')
os.makedirs(GENAI_PDF_DIR, exist_ok=True)

mcp = FastMCP('pdf')

# TODO: better error handling, maybe ctx(Context)??


@mcp.tool()
async def download_pdf_url(url: str, filename: str) -> str:
    """
    MCP tool to download remote pdf using url.
    Args:
        url: pdf url. No auth supported currently.
        filename: construct from the last part of the url plus an 8-character random alphanumeric string.
        f.e. if url is https://arxiv.org/pdf/paper_id.pdf, filename could be paper_id_7f3a2b9e.pdf.
    Return:
        pdf filename
    """

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

        filename = os.path.join(GENAI_PDF_DIR, filename)
        with open(filename, 'wb') as f:
            f.write(response.content)
    return filename

"""
read_pdf won't work when client is Claude Desktop. Reasons answered by Claude:
1. We're accessing the raw PDF file from your local filesystem
2. The entire raw PDF data (including binary data, encoding, etc.) needs to be returned in the conversation
3. We're limited by the maximum response size (1,048,576 characters)
4. The raw data appears directly in our conversation

So if need it to understand pdf/paper, can, first of all, use tool download_pdf and then upload from Claude desktop directly.
When you upload a PDF directly to Claude through the web interface/Claude desktop:
1. The PDF is processed on Anthropic's servers
2. The content is extracted and chunked appropriately
3. Claude can work with much larger documents because of specialized processing
4. You don't see the raw data in the conversation
"""

# @mcp.tool()
# async def read_pdf(path: str) -> bytes:
#     """
#     read local pdf file
#     Args:
#         path: abs pdf file path. Remind user it is abs path.
#     """
#     with open(path, 'rb') as f:
#         return f.read()


if __name__ == '__main__':
    mcp.run(transport='stdio')

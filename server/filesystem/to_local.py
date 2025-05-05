import time
import os

from mcp.server.fastmcp import FastMCP

storage_dir = os.path.join(os.environ['HOME'], '.bot1d', 'storage')
short_memory_dir = os.path.join(storage_dir, 'short-memory')

mcp = FastMCP('self-filesystem')


def write_to_file(content: any, file_dir: str, file_name: str=None) -> str:
    """
    Write to a local file under storage path. Return file path.
    """
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir)
    file_name = file_name if file_name else str(time.time())
    full_path = os.path.join(file_dir, file_name)
    with open(full_path, 'w') as f:
        f.write(content)
    return file_name

def list_directory(directory: str) -> list:
    """
    List all files under the given directory.
    Args:
        directory: The directory path to list files from
    Returns:
        List of file names if directory exists, None otherwise
    """

    if not os.path.exists(directory):
        return []
    return os.listdir(directory)


@mcp.tool()
async def save_short_memory(memory: str) -> str:
    """
    Save a concise storyline/thought-of-chain of the current conversation to a local file.
    The summary should be condensed to less than 500 words before saving.
    If there are exact numbers or dates, MUST include them in the summary.
    Args:
        memory: The conversation content to be summarized and saved
    Returns:
        The filename where the summary was saved
    """
    return write_to_file(memory, short_memory_dir)

@mcp.tool()
async def delete_short_memory(file_name: str) -> None:
    """
    Delete a short memory file. Only files under short memory path are allowed.
    Args:
      file_name: short memory filename.
    """
    full_path = os.path.join(short_memory_dir, file_name)
    if not os.path.isfile(full_path):
        raise ValueError('Filename does not exist under short memory directoy.')
    os.remove(full_path)


# don't want to send LLM too many info, changed this part to pure logic in MCP client.
# @mcp.tool()
# async def list_short_memory() -> list:
#     """
#     Retrieve a list of all saved conversation summary files from the local storage.
#     Returns:
#         A list of filenames containing conversation summaries
#     """
#     return list_directory(short_memory_dir)


if __name__ == '__main__':
    mcp.run(transport='stdio')

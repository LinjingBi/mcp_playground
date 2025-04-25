from arxiv_httpx import ArxivX
from mcp.server.fastmcp import FastMCP

mcp = FastMCP('ArxivMCP')

arxiv = ArxivX()


@mcp.tool()
async def search(query: str, max_result: int = 5):
    """
    search paper on arxiv by title or id. Must provide either title or id.
    Args:
        query: it is the combination of title(ti) and arxiv id(id).
        If only title is given, query is ti:<title>. If only id is given, query is id:<id>.
        If both are given, query is ti:<title>+AND+id:<id>.
        max_result: max return numbers. Default is 5
    """

    papers = await arxiv.search(query, max_result)
    results = []
    for ent in papers:
        results.append({
            "title": ent['title'],
            "authors": ent['authors'],
            "link": ent['link'],
            "summary": ent['summary'],
            "published": ent['published'],
        })
        for link in ent['links']:
            if link['type'] == 'application/pdf':
                results[-1]['pdf'] = link['href']
                break
    return results


if __name__ == "__main__":
    print('arxiv server staring..')
    mcp.run(transport='stdio')

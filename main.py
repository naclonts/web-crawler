from bs4 import BeautifulSoup
from typing import Set
import requests
import enum
from urllib.parse import urljoin, urlparse, urlunparse, ParseResult


class NodeState(enum.Enum):
    UNDISCOVERED = 'undiscovered'
    DISCOVERED = 'discovered'
    FULLY_EXPLORED = 'fully explored'


class Node():
    def __init__(self, data):
        self.data = data
        self.nodes: Set[Node] = set()
        self.vertices: Set[Node] = set()
        self.state = NodeState.UNDISCOVERED

    def add_vertex(self, node):
        # this is an undirected graph
        self.vertices.add(node)
        node.vertices.add(self)

class Graph():
    def __init__(self):
        self.nodes: set[Node] = set()
        self.explore_queue: Set[Node] = set()

def get_html(url: str) -> str:
    resp = requests.get(url)
    html = str(resp.content)
    return html

def get_href_links(html: str, filter_base: ParseResult) -> Set[str]:
    """Returns in `html` hrefs that have the same netloc as `filter_netloc`."""
    soup = BeautifulSoup(html, 'html.parser')
    links = set()

    for link in soup.findAll('a'):
        href = link.get('href')
        parsed = urlparse(href)
        # if netloc is empty, assume it's a link to the same domain
        # (e.g., `href='/about'`)
        if parsed.netloc in ['', filter_base.netloc]:
            filter_base_url = f'{filter_base.scheme}://{filter_base.netloc}'
            links.add(urljoin(filter_base_url, parsed.path))

    return links



def crawl_site(base_url: str) -> Graph:
    base_url = urlparse(base_url)

    graph = Graph()

    node = Node(urlunparse(base_url))
    # node.state = NodeState.DISCOVERED
    graph.nodes.add(node)
    graph.explore_queue.add(node)

    while len(graph.explore_queue):
        node = graph.explore_queue.pop()
        print(f'- Working through node "{node.data}"')

        url = node.data
        html = get_html(url)
        links = get_href_links(html, base_url)

        for link in links:
            exists = link in [n.data for n in graph.nodes]
            if exists:
                continue

            print(f'---- New link found: {link}')
            link_node = Node(link)
            link_node.state = NodeState.DISCOVERED

            node.add_vertex(link_node)
            graph.nodes.add(link_node)
            graph.explore_queue.add(link_node)

        node.state = NodeState.FULLY_EXPLORED

    return graph


if __name__ == '__main__':
    base_url = 'https://nathanclonts.com'

    graph = crawl_site(base_url)
    print(graph)

import httpx
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Referer": "https://www.google.com",
}


async def fetch_website(url: str) -> tuple[str, str]:
    async with httpx.AsyncClient(headers=HEADERS) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            return (url, f"Error: {e}")
        return (url, response.text)


def parse_website_metadata(content: str) -> dict:
    # Parse the HTML content
    soup = BeautifulSoup(content, "html.parser")

    # Extract the title
    title = soup.title.string if soup.title else "No title found"

    # Extract the subtitle (assuming it's in an <h2> tag)
    subtitle = (
        soup.find("h2").get_text(strip=True) if soup.find("h2") else "No subtitle found"
    )

    # Extract the main text (assuming it's in <p> tags)
    paragraphs = soup.find_all("p")
    text = (
        " ".join([para.get_text() for para in paragraphs])
        if paragraphs
        else "No text found"
    )

    # Extract code blocks (assuming they are in <pre> or <code> tags)
    code_blocks = []
    for pre in soup.find_all("pre"):
        code_blocks.append(pre.get_text(strip=True))
    for code in soup.find_all("code"):
        code_blocks.append(code.get_text(strip=True))

    # Extract all links (URLs)
    links = [a["href"] for a in soup.find_all("a", href=True)]

    # Return the extracted metadata
    return {
        "title": title,
        "subtitle": subtitle,
        "text": text,
        "code_blocks": code_blocks,
        "links": links,
    }

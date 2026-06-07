from __future__ import annotations

import re

_WS = re.compile(r"[ \t]+")
_BLANKS = re.compile(r"\n\s*\n+")


def html_to_text(html: str) -> str:
    if not html:
        return ""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    # Preserve links so claim URLs survive into the cleaned text (get_text drops hrefs).
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("http://", "https://")):
            a.append(f" ({href})")
    text = soup.get_text("\n")
    lines = [_WS.sub(" ", ln).strip() for ln in text.splitlines()]
    text = "\n".join(ln for ln in lines if ln)
    return _BLANKS.sub("\n\n", text).strip()

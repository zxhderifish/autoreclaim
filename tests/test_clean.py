from autoreclaim.clean import html_to_text


def test_strips_tags_scripts_and_collapses_whitespace():
    html = """
    <html><head><style>.x{}</style><script>var a=1;</script></head>
    <body><h1>Acme   Settlement</h1><p>Deadline:  2026-09-01</p></body></html>
    """
    text = html_to_text(html)
    assert "Acme Settlement" in text
    assert "Deadline: 2026-09-01" in text
    assert "var a" not in text          # script dropped
    assert ".x{}" not in text           # style dropped


def test_empty_input_returns_empty():
    assert html_to_text("") == ""


def test_keeps_http_link_url_inline():
    text = html_to_text('<p>Acme Settlement</p><a href="https://x.com/claim">File a claim</a>')
    assert "File a claim" in text
    assert "https://x.com/claim" in text


def test_does_not_append_non_http_links():
    text = html_to_text('<a href="mailto:a@b.com">email us</a><a href="/rel">rel</a>')
    assert "mailto:" not in text
    assert "/rel)" not in text  # relative href not appended

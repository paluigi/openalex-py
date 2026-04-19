from __future__ import annotations

from openalexpy.config import config
from openalexpy.content import PDF
from openalexpy.content import TEI
from openalexpy.content import ContentDownloader


class TestContentDownloader:
    def test_pdf_url(self):
        d = ContentDownloader("W4412002745", ".pdf")
        assert d.url == "https://content.openalex.org/works/W4412002745.pdf"

    def test_tei_url(self):
        d = ContentDownloader("W4412002745", ".grobid-xml")
        assert d.url == "https://content.openalex.org/works/W4412002745.grobid-xml"

    def test_custom_content_base(self):
        original = config.content_base_url
        try:
            config.content_base_url = "https://custom.openalex.org"
            d = ContentDownloader("W123", ".pdf")
            assert d.url == "https://custom.openalex.org/works/W123.pdf"
        finally:
            config.content_base_url = original


class TestPDF:
    def test_pdf_url(self):
        p = PDF("W4412002745")
        assert p.url == "https://content.openalex.org/works/W4412002745.pdf"


class TestTEI:
    def test_tei_url(self):
        t = TEI("W4412002745")
        assert t.url == "https://content.openalex.org/works/W4412002745.grobid-xml"

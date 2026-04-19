# Content Download

Retrieve full-text content (PDF and TEI XML) for works that have open access content available.

## Basic Usage

```python
work = await openalexpy.Works().get_by_id("W4412002745")

# Get PDF content as bytes
pdf_bytes = await work._pdf.get()

# Download PDF to a file
await work._pdf.download("paper.pdf")

# Get TEI XML content
tei_bytes = await work._tei.get()

# Download TEI to a file
await work._tei.download("paper.xml")

# Get content URL without downloading
print(work._pdf.url)  # https://content.openalex.org/works/W4412002745.pdf
print(work._tei.url)  # https://content.openalex.org/works/W4412002745.grobid-xml
```

## Sync Usage

```python
work = openalexpy.WorksSync().get_by_id("W4412002745")
pdf_bytes = work._pdf.sync_get()
work._pdf.sync_download("paper.pdf")
```

## Two-Step Redirect

The content API returns a 302 redirect to a signed CDN URL. The library handles this correctly:

1. First request captures rate-limit headers from the 302 response
2. Then follows the redirect to the CDN URL to download content

This ensures rate-limit information is not lost during the redirect chain.

## Cost

Content downloads cost **$10 per 1,000 calls** (i.e., $0.01 per PDF). With the free $1/day tier, you can download up to 100 PDFs per day.

## Availability

Content availability depends on the publisher's open access policies and licensing agreements. Not all works have downloadable PDFs.


# Broken Link Checker GitHub Action

Automatically checks your website sitemap for broken links and generates CSV/HTML reports.

## Usage

jobs:

Add the following to your workflow YAML:

```yaml
name: Broken Link Checker
on: [push]
jobs:
  check-broken-links:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Run Broken Link Checker
        uses: itusebastian/seo-broken-link-checker-action@main
        env:
          SITEMAP_URL: ${{ secrets.SITEMAP_URL }}
```

## Environment Variables
- `SITEMAP_URL`: The sitemap XML URL to check (required)

## Outputs
- `broken_links_report.csv`: CSV report of broken links
- `broken_links_report.html`: HTML report of broken links

## Example
Set your sitemap URL as a secret in your repository settings (e.g., `SITEMAP_URL`).

## License
MIT

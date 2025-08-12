import argparse
import csv
import sys
import requests
import time
import logging
import yaml
from lxml import etree
from io import StringIO, BytesIO
from urllib.parse import urlparse
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def load_config(config_path):
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return {}

def parse_sitemap(sitemap_url, seen=None):
    if seen is None:
        seen = set()
    if sitemap_url in seen:
        return []
    seen.add(sitemap_url)
    logging.info(f"Fetching sitemap: {sitemap_url}")
    resp = requests.get(sitemap_url, timeout=20)
    resp.raise_for_status()
    tree = etree.parse(BytesIO(resp.content))
    root = tree.getroot()
    nsmap = root.nsmap.copy()
    nsmap[None] = nsmap.get(None, '')
    urls = []
    # Detect sitemap index
    if root.tag.endswith('sitemapindex'):
        sitemap_tags = root.findall('.//{*}sitemap', namespaces=nsmap)
        for sitemap in sitemap_tags:
            loc = sitemap.find('{*}loc', namespaces=nsmap)
            if loc is not None and loc.text:
                urls.extend(parse_sitemap(loc.text.strip(), seen))
    else:
        url_tags = root.findall('.//{*}url', namespaces=nsmap)
        for url in url_tags:
            loc = url.find('{*}loc', namespaces=nsmap)
            if loc is not None and loc.text:
                urls.append(loc.text.strip())
    logging.info(f"Found {len(urls)} URLs in sitemap: {sitemap_url}")
    return urls

def parse_url_file(file_path):
    with open(file_path, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    logging.info(f"Loaded {len(urls)} URLs from file.")
    return urls

def check_link(url, timeout=10):
    try:
        resp = requests.head(url, allow_redirects=True, timeout=timeout)
        if resp.status_code >= 400 or resp.status_code < 100:
            resp = requests.get(url, allow_redirects=True, timeout=timeout)
        return resp.status_code
    except Exception as e:
        logging.warning(f"Error checking {url}: {e}")
        return None

def find_broken_links(urls, timeout=10):
    broken = []
    for i, url in enumerate(urls, 1):
        logging.info(f"[{i}/{len(urls)}] Checking: {url}")
        status = check_link(url, timeout)
        if status is None or status >= 400 or status < 100:
            broken.append({'url': url, 'status': status})
    return broken

def save_csv_report(broken_links, output_path):
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['url', 'status'])
        writer.writeheader()
        for row in broken_links:
            writer.writerow(row)
    logging.info(f"CSV report saved to {output_path}")

def save_html_report(broken_links, output_path):
    html = '<html><head><title>Broken Links Report</title></head><body>'
    html += '<h1>Broken Links Report</h1>'
    html += '<table border="1"><tr><th>URL</th><th>Status</th></tr>'
    for row in broken_links:
        html += f'<tr><td>{row["url"]}</td><td>{row["status"]}</td></tr>'
    html += '</table></body></html>'
    with open(output_path, 'w') as f:
        f.write(html)
    logging.info(f"HTML report saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Broken Link Checker')
    parser.add_argument('--sitemap', help='Sitemap XML URL')
    parser.add_argument('--url-file', help='File with list of URLs (one per line)')
    parser.add_argument('--output', default='broken_links_report.csv', help='CSV output file')
    parser.add_argument('--html', action='store_true', help='Also output HTML report')
    parser.add_argument('--config', default='config.yaml', help='Config YAML file')
    args = parser.parse_args()

    config = load_config(args.config)
    sitemap_url = args.sitemap or config.get('default_sitemap_url')
    output_path = args.output or config.get('default_output_path', 'broken_links_report.csv')

    if args.url_file:
        urls = parse_url_file(args.url_file)
    elif sitemap_url:
        urls = parse_sitemap(sitemap_url)
    else:
        logging.error('Must provide --sitemap or --url-file')
        sys.exit(2)

    broken_links = find_broken_links(urls)
    save_csv_report(broken_links, output_path)
    if args.html:
        html_path = output_path.replace('.csv', '.html')
        save_html_report(broken_links, html_path)

    if broken_links:
        logging.error(f"Found {len(broken_links)} broken links!")
        sys.exit(1)
    else:
        logging.info("No broken links found.")
        sys.exit(0)

if __name__ == '__main__':
    main()

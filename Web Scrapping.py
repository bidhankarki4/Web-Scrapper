#!/usr/bin/env python3
"""
Author: Bidhan Karki
Date: 03/05/2021

Program to get news titles from CNN.

cnn_titles.py visits three CNN news categories pages
and takes headlines and URLs from them.

The results are sent to stdout in JSON
which is both machine and human readable.

In case of error, it tries to continue operation but
sends error information to stderr. The exit code in
this case is 1.

Invocation:
    ./cnn_titles.py      # Linux
    python cnn_titles.py # Windows

Requirements:
    - Python 3 (tested on 3.8.7)
    - The program depends on lxml library as built-in
    xml.etree can't parse html

CSE Machine(Putty):
    chmod +x cnn_titles.py
    ./cnn_titles.py

"""

import json
import re
import sys
import urllib.parse
import urllib.request

import lxml.etree as ET

BASE_URL = 'https://cnn.com/'
CATEGORIES = ('style', 'entertainment', 'business')


def main():
    status = 0
    result_data = {}

    for category in CATEGORIES:
        try:
            category_url = urllib.parse.urljoin(BASE_URL, category)
            category_html = get_html(category_url)
            titles = get_category_page_titles(category_html)

            # If there is no headlines found on category page, it might be
            # sign that they changed the html.
            # We don't want get_category_page_titles() to throw
            # exception in this case, but instead to just return
            # an empty list.
            if not len(titles):
                print_stderr(f"zero titles found on {category}")
                status = 1

            result_data[category] = titles

        except Exception as e:
            # In case of some unexpected failure, we log it and set the
            # status code to non-zero but continue with other categories.
            print_stderr(f"error while processing {category}: {str(e)}")
            status = 1

    output_results(result_data)

    return status


def print_stderr(message):
    """Prints to stderr"""
    # For convenience of passing Exception instances.
    message = str(message)
    sys.stderr.write(message + "\n")


def load_html_with_lxml(html):
    """Parse HTML with lxml and return root node"""
    return ET.fromstring(html, parser=ET.HTMLParser())


def get_category_page_titles(html):
    """Extracts headlines and urls from a category page"""
    root = load_html_with_lxml(html)

    # contains() is used because they add additional
    # CSS class names for some titles.
    search_expr = """
        //a[contains(@class, 'CardBasic__title')
            or contains(@class, 'CardHero__title')]
        | //h3[contains(@class, 'cd__headline')]/a
    """
    headline_link_nodes = root.xpath(search_expr)

    # Extracting text from HTML node
    return [clean_text(get_node_text(n)) for n in headline_link_nodes]


def clean_text(text):
    """Converts multiline text to single line,
    removes leading and trailing whitespace.
    """
    return re.sub("[\n\r]", ' ', text).strip()


def get_node_text(node):
    """Collects plain text from a node its children.
    Example: <span><strong>Opinion: </strong>A financial...</span>
    Returns empty string if node have neither text nor children.
    """
    return ET.tostring(node, method="text", encoding='unicode')


def get_html(url):
    """Makes an HTTP request and returns a response"""
    # urlopen() throws an exception for non-200 HTTP responses,
    # so we don't have to check that with .getcode()
    with urllib.request.urlopen(url) as http_response:
        response_body = http_response.read()

    html = response_body.decode('utf8')
    return html


def output_results(categories):
    """Presents results to stdout"""
    print(json.dumps(categories, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())


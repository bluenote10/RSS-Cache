#!/usr/bin/env python
"""
Inspired by: https://stackoverflow.com/a/42685246/1804173
"""

from __future__ import print_function, unicode_literals

import fnmatch
import os

import xml.etree.ElementTree


def find_all_files(base, pattern="*"):
    matches = []
    for root, dirnames, filenames in os.walk(base):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(root, filename))
    return sorted(matches, reverse=True)    # newer first


def parse(feed_file):

    et = xml.etree.ElementTree.parse(feed_file)
    root = et.getroot()

    items = []

    channel_el = root.find("channel")
    for child in channel_el:
        if child.tag == "item":
            # title_el = child.find("title")
            # pub_date_el = child.find("pubDate")
            # print("{:<80s} - {}".format(title_el.text, pub_date_el.text))
            items.append(child)

    return et, root, items


FEEDS = {
    "sedaily": "https://softwareengineeringdaily.com/category/podcast/feed"
}


def fetch_feed(name, url, basedir):
    wayback_dir = os.path.join(basedir, "wayback")

    lastest = os.path.join(basedir, "latest.xml")
    existing = os.path.join(basedir, "feed.xml")
    waybacks = find_all_files(wayback_dir)

    previous = [existing] + waybacks

    et, root, items = parse(lastest)

    for item in items:
        title_el = item.find("title")
        pub_date_el = item.find("pubDate")
        print("{:<80s} - {}".format(title_el.text, pub_date_el.text))

    existing_items = items

    for prev in previous:
        print(prev)
        et, root, items = parse(prev)

        for item in items:
            title = item.find("title").text
            pub_date = item.find("pubDate").text

            exists = any(
                True for existing_item in existing_items
                if existing_item.find("title").text == title
            )

            if not exists:
                print("{:<80s} - {} - from: {}".format(title, pub_date, prev))
                existing_items.append(item)
                root.find("channel").append(item)

    et.write(os.path.join(basedir, "feed_all.xml"))

    import IPython; IPython.embed()


def main():
    for feed_name, feed_url in FEEDS.items():
        basedir = os.path.join(os.path.dirname(__file__), "fetched", feed_name)
        if not os.path.exists(basedir):
            print("Feed directory does not exist: {}".format(basedir))
        fetch_feed(feed_name, feed_url, basedir)





if __name__ == "__main__":
    main()
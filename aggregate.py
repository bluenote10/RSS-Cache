#!/usr/bin/env python
"""
Inspired by: https://stackoverflow.com/a/42685246/1804173
"""

from __future__ import print_function, unicode_literals

import argparse
import datetime
import fnmatch
import os

import xml.etree.ElementTree

import jinja2


def find_all_files(base, pattern="*"):
    matches = []
    for root, dirnames, filenames in os.walk(base):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(root, filename))
    return sorted(matches, reverse=True)    # newer first


def load_feed(feed_file):

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
    "sedaily": "https://softwareengineeringdaily.com/category/podcast/feed",
    "changelog": "https://changelog.com/podcast/feed",
}


def aggregate_feed(name, url, base_dir):
    wayback_dir = os.path.join(base_dir, "wayback")

    lastest = os.path.join(base_dir, "latest.xml")
    existing = os.path.join(base_dir, "feed.xml")
    waybacks = find_all_files(wayback_dir)

    previous = [existing] + waybacks

    et, root, items = load_feed(lastest)

    num_entries = 0
    for item in items:
        title_el = item.find("title")
        pub_date_el = item.find("pubDate")
        print("{:<80s} - {}".format(title_el.text, pub_date_el.text))
        num_entries += 1

    existing_items = items

    for prev in previous:
        # print(prev)
        _, _, items = load_feed(prev)

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
                num_entries += 1

    outpath = os.path.join(base_dir, "feed_all.xml")
    et.write(outpath)

    return outpath, num_entries


def render_index(root_dir, links):
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(searchpath=root_dir),
        autoescape=jinja2.select_autoescape(['html', 'xml'])
    )
    template = env.get_template("template.html")
    output = template.render(
        links=links,
    )
    with open(os.path.join(root_dir, "index.html"), "w") as f:
        f.write(output)


def parse_args():
    parser = argparse.ArgumentParser(description="Fuse RSS entries")
    parser.add_argument(
        "show",
        required=True,
        help="The show name to fuse"
    )
    args = parser.parse_args()
    return args


def main():
    #args = parse_args()

    root_dir = os.path.dirname(__file__)

    links = []

    for feed_name, feed_url in FEEDS.items():
        base_dir = os.path.join(root_dir, "fetched", feed_name)
        if not os.path.exists(base_dir):
            print("Feed directory does not exist: {}".format(base_dir))
        outpath, num_entries = aggregate_feed(feed_name, feed_url, base_dir)

        links.append({
            "name": feed_name,
            "num_entries": num_entries,
            "target": os.path.relpath(outpath, root_dir),
            "time_updated": str(datetime.datetime.now()),
        })

    render_index(root_dir, links)


if __name__ == "__main__":
    main()
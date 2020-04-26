#!/bin/bash

FEED_URL=https://softwareengineeringdaily.com/category/podcast/feed

cd $(dirname $0)

mkdir -p wayback

waybackpack ${FEED_URL} \
  -d ./wayback \
  --from-date 2015 \
  --follow-redirects

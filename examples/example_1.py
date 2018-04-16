#!/usr/bin/env python

import os
import sys
import json
from contextlib import contextmanager
import requests

import logging

sys.path.append('/Users/demitri/Documents/Repositories/GitHub/wordpress_orm')
import wordpress_orm as wp
from wordpress_orm import wp_session, exc

logger = logging.getLogger("wordpress_orm")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler() # output to console
ch.setLevel(logging.DEBUG)   # set log level for output
logger.addHandler(ch)        # add to logger

# WP API demo site: https://demo.wp-api.org/wp-json/
api = wp.API(url="http://brie6.cshl.edu/wordpress/index.php/wp-json/wp/v2/")

with wp_session(api):
	pr = api.PostRequest()
#	pr.arguments = {
#			"orderby":"date",
#			"order":"desc"
#	}
	pr.orderby = "date"
	pr.order = "desc"
#	pr.arguments["filter[category_name]"] = "blog"
	posts = pr.get()

for post in posts:
	print(post)

post = api.post(id=1)

print (post)
media = api.media(id=32)

print(media)

#user = api.user(id=1)
#print("{0}".format(user))

user = api.user(username="muna")
#user = api.user(slug="muna")

print(user)

for post in user.posts:
	print("    {}".format(post.featured_media.s.source_url))

print (" ========== Categories =========== ")
#cr = api.CategoryRequest()
try:
	slug = "dfszdfsa"
	news_category = api.category(slug=slug)
	print(news_category)
except exc.NoEntityFound:
	print ("No category found with slug '{0}'.".format(slug))
	category_names = [x.s.name for x in api.CategoryRequest().get()]
	print ("Available categories: {0}".format(", ".join(category_names)))

print()

post = api.post(slug='the-bloomless-mutant-a-paragon-of-modern-sorghum-genetic-and-genomic-resources')
print(post)

raise Exception()


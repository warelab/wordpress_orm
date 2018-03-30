
import os
import sys
from contextlib import contextmanager
import requests

import logging

sys.path.append('/Users/demitri/Documents/Repositories/GitHub/wordpress_orm')
import wordpress_orm as wp

logger = logging.getLogger("wordpress_orm")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler() # output to console
ch.setLevel(logging.DEBUG)   # set log level for output
logger.addHandler(ch)        # add to logger

api = wp.API(url="http://brie6.cshl.edu/wordpress/index.php/wp-json/wp/v2/")

@contextmanager
def wp_session(api=None):
	api.session = requests.Session()
	yield api
	api.session.close()
	api.session = None

if True:
	with wp_session(api):
		pr = api.PostRequest()
		pr.arguments = {
				"orderby":"date",
				"order":"desc",
				"filter[category_name]":"blog"
		}
	#	pr.arguments["orderby"] = "date"
	#	pr.arguments["order"] = "desc"
	#	pr.arguments["filter[category_name]"] = "blog"
		posts = pr.get()

	for post in posts:
		print(post.wpid)

post = api.post(wpid=1)

print (post)
media = api.media(wpid=32)

print(media)

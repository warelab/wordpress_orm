
#from .entities.post import Post, PostRequest
#from .entities.media import Media, MediaRequest
#from .entities.user import User, UserRequest

import logging
from contextlib import contextmanager

import requests

from .entities import post, user, media, category
from . import exc

logger = logging.getLogger("{}".format(__loader__.name.split(".")[0])) # package name

@contextmanager
def wp_session(api=None):
	api.session = requests.Session()
	yield api
	api.session.close()
	api.session = None

class API:
	'''
	
	'''
	def __init__(self, url=None):
		self.base_url = url
		self.session = None
		
	def PostRequest(self):
		''' Factory method that returns a new PostRequest attached to this API. '''
		return post.PostRequest(api=self)

	def post(self, wpid=None):
		'''
		Returns a Post object from the WordPress API with the provided ID.
		
		wpid : WordPress ID
		'''
		pr = post.PostRequest(api=self)
		if wpid is not None:
			pr.wpid = wpid
			
		posts = pr.get()
		
		if len(posts) == 1:
			return posts[0]
		elif len(posts) == 0:
			raise exc.NoEntityFound()
		else:
			# more than one found
			assert False, "Should not get here!"
	
	def MediaRequest(self):
		''' Factory method that returns a new MediaRequest attached to this API. '''
		return media.MediaRequest(api=self)

	def media(self, wpid=None):
		'''
		Returns a Media object from the WordPress API with the provided ID.
		
		wpid : WordPress ID
		'''
		mr = media.MediaRequest(api=self)
		if wpid is not None:
			mr.wpid = wpid

		media_list = mr.get()

		if len(media_list) == 1:
			return posts[0]
		elif len(media_list) == 0:
			raise exc.NoEntityFound()
		else:
			# more than one found
			assert False, "Should not get here!"
	
	def user(self, wpid=None, username=None):
		'''
		Returns a User object from the WordPress API with the provided ID.
		
		wpid : WordPress ID
		'''
		if all([wpid, username]):
			raise Exception("Only the WordPress id (wpid) or the username can be specified, not both.")

		ur = user.UserRequest(api=self)
		if wpid:
			ur.wpid = wpid
		elif username:
			ur.search = username

		users = ur.get()

		if len(users) == 1:
			return posts[0]
		elif len(users) == 0:
			raise exc.NoEntityFound()
		else:
			# more than one found
			assert False, "Should not get here!"

	def UserRequest(self):
		''' Factory method that returns a new UserRequest attached to this API. '''
		return user.UserRequest(api=self)
		
	def category(self, wpid=None, slug=None, name=None):
		'''
		Returns a Category object from the WordPress API by ID, slug, or name.
		
		wpid : WordPress ID
		'''
		if len([x for x in [wpid, slug, name] if x is not None]) > 1:
			raise Exception("Only one of 'wpid', 'slug', 'name' can be specified.")
		
		cr = category.CategoryRequest(api=self)

		if wpid:
			cr.wpid = wpid
		elif slug:
			cr.slug = slug

		categories = cr.get()
		if len(categories) == 1:
			return categories[0]
		elif len(categories) == 0:
			raise exc.NoEntityFound()
		else:
			# more than one found
			assert False, "Should not get here!"

	def CategoryRequest(self):
		''' Factory method that returns a new CategoryRequest attached to this API. '''
		return category.CategoryRequest(api=self)












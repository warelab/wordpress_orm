
#from .entities.post import Post, PostRequest
#from .entities.media import Media, MediaRequest
#from .entities.user import User, UserRequest

import logging
from contextlib import contextmanager

import requests

from .entities import post, user, media, category, comment
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

	def post(self, id=None, slug=None):
		'''
		Returns a Post object from the WordPress API with the provided ID.
		
		id : WordPress ID
		'''
		if len([x for x in [id, slug] if x is not None]) > 1:
			raise Exception("Only one of [id, slug] can be specified at a time.")
		
		
		pr = post.PostRequest(api=self)
		if id is not None:
			pr.id = id
		
		if slug:
			pr.slug = slug
			
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

	def media(self, id=None):
		'''
		Returns a Media object from the WordPress API with the provided ID.
		
		id : WordPress ID
		'''
		mr = media.MediaRequest(api=self)
		if id is not None:
			mr.id = id

		media_list = mr.get()

		if len(media_list) == 1:
			return media_list[0]
		elif len(media_list) == 0:
			raise exc.NoEntityFound()
		else:
			# more than one found
			assert False, "Should not get here!"
	
	def user(self, id=None, username=None, slug=None):
		'''
		Returns a User object from the WordPress API with the provided ID.
		
		id : WordPress ID
		'''
		if len([x for x in [id, username, slug] if x is not None]) > 1:
			raise Exception("Only one of [id, username, slug] can be specified at a time.")

		ur = user.UserRequest(api=self)
		if id:
			ur.id = id
		elif username:
			ur.search = username
		elif slug:
			ur.slug = slug

		users = ur.get()

		if len(users) == 1:
			return users[0]
		elif len(users) == 0:
			raise exc.NoEntityFound()
		else:
			# more than one found
			logger.debug(users)
			assert False, "Should not get here! Request: {0}".format(ur.request.url)

	def UserRequest(self):
		''' Factory method that returns a new UserRequest attached to this API. '''
		return user.UserRequest(api=self)
		
	def category(self, id=None, slug=None, name=None):
		'''
		Returns a Category object from the WordPress API by ID, slug, or name.
		
		id : WordPress ID
		'''
		if len([x for x in [id, slug, name] if x is not None]) > 1:
			raise Exception("Only one of 'id', 'slug', 'name' can be specified.")
		
		cr = category.CategoryRequest(api=self)

		if id:
			cr.id = id
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

	def comment(self, id=None):
		'''
		Returns a Comment object from the WordPress API by ID.
		'''
		if id is None:
			raise Exception("A comment 'id' must be specified.")
			
			cr = comment.CommentRequest(api=self)
			
			if id:
				cr.id = id
			
			comments = cr.get()
			if len(comments) == 1:
				return comments[0]
			elif len(comments) == 0:
				raise exc.NoEntityFound()
			else:
				# more than one found
				assert False, "Should not get here!"

	def CommentRequest(self):
		''' Factory method that returns a new CommentRequest attached to this API. '''
		return comment.CommentRequest(api=self)








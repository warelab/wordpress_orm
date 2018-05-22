
import logging
from contextlib import contextmanager

import requests

from .entities import post, user, media, category, comment
from . import exc
from .cache import WPORMCache, WPORMCacheObjectNotFoundError

from .entities import Category
from .entities import Comment
from .entities import Media
#from .entities import Page
#from .entities import PostRevision
#from .entities import PostStatus
#from .entities import PostType
from .entities import Post
#from .entities import Settings
#from .entities import Tag
#from .entities import Taxonomy
from .entities import User

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
		
		self.wordpress_object_cache = WPORMCache() # dict() # key = class name, value = object
		#
		# individual caches
		# each class has two key that can be accessed (i.e. appears twice in dictionary)
		#		key = WP id as string, value = object
		#       key = slug, value = object
		#
		#for custom_class in [Category, Comment, Post, User]:
		#	self.register_custom_class(custom_class)
		#	#self.wordpress_object_cache[key] = dict()
	
	def __repr__(self):
		return "<WP {0} object at {1} base='{2}'>".format(self.__class__.__name__, hex(id(self)), self.base_url)

	def register_custom_class(self, theclass):
		'''
		Register a custom subclass of WPEntity with the API.
		'''
		# set up cache dictionary
		assert False, "finish code"
#		class_name = theclass.__name__
#		if class_name not in self.wordpress_object_cache:
#			self.wordpress_object_cache[class_name] = dict()
	
	def PostRequest(self, **kwargs):
		''' Factory method that returns a new PostRequest attached to this API. '''
		return post.PostRequest(api=kwargs.pop('api', self), **kwargs)

	def post(self, id=None, slug=None):
		'''
		Returns a Post object from the WordPress API with the provided ID.
		
		id : WordPress ID
		'''
		if len([x for x in [id, slug] if x is not None]) > 1:
			raise Exception("Only one of [id, slug] can be specified at a time.")
		
		# check cache first
		try:
			if id:
				post = self.wordpress_object_cache.get(class_name=Post.__name__, key=str(id))
			elif slug:
				post = self.wordpress_object_cache.get(class_name=Post.__name__, key=slug)
			logger.debug("Post cache hit {0}".format(post.s.slug))
			return post
		except WPORMCacheObjectNotFoundError:
			pass # not found, fetch below
		
		pr = self.PostRequest(api=self)
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
	
	def MediaRequest(self, **kwargs):
		''' Factory method that returns a new MediaRequest attached to this API. '''
		return media.MediaRequest(api=kwargs.pop('api', self), **kwargs)

	def media(self, id=None, slug=None):
		'''
		Returns a Media object from the WordPress API with the provided ID.
		
		id : WordPress ID
		'''
		if len([x for x in [id, slug] if x is not None]) > 1:
			raise Exception("Only one of [id, slug] can be specified at a time.")
		elif id is None and slug is None:
			# be careful of id=0 case
			raise Exception("At least one of 'id' or 'slug' must be specified.")

		# check cache first
		try:
			if id is not None: # id could be zero
				media = self.wordpress_object_cache.get(class_name=Media.__name__, key=str(id))
			elif slug is not None:
				media = self.wordpress_object_cache.get(class_name=Media.__name__, key=slug)
			print(id, slug)
			logger.debug("Media cache hit ({0})".format(media.s.slug))
			return media
		except WPORMCacheObjectNotFoundError:
			#logger.debug("Media cache fail")
			pass # not found, fetch below

		mr = self.MediaRequest(api=self)
		if id:
			mr.id = id
		elif slug:
			mr.slug = slug

		media_list = mr.get()

		if len(media_list) == 1:
			return media_list[0]
		elif len(media_list) == 0:
			raise exc.NoEntityFound()
		else:
			# more than one found
			logger.debug(media_list)
			assert False, "Should not get here!"
	
	def user(self, id=None, username=None, slug=None):
		'''
		Returns a User object from the WordPress API with the provided ID.
		
		id : WordPress ID
		'''
		if len([x for x in [id, username, slug] if x is not None]) > 1:
			raise Exception("Only one of [id, username, slug] can be specified at a time.")
		if (any[id, slug]) is False:
			raise Exception("At least one of 'id' or 'slug' must be specified.")

		# check cache first
		try:
			if id:
				user = self.wordpress_object_cache.get(class_name=User.__name__, key=str(id))
			elif slug:
				user = self.wordpress_object_cache.get(class_name=User.__name__, key=slug)
			logger.debug("User cache hit ({0})".format(user.s.username))
			return user
		except WPORMCacheObjectNotFoundError:
			#logger.debug("User cache fail")
			pass # not found, fetch below

		ur = self.UserRequest(api=self)
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

	def UserRequest(self, **kwargs):
		''' Factory method that returns a new UserRequest attached to this API. '''
		return user.UserRequest(api=kwargs.pop('api', self), **kwargs)
		
	def category(self, id=None, slug=None, name=None):
		'''
		Returns a Category object from the WordPress API by ID, slug, or name.
		
		id : WordPress ID
		'''
		if len([x for x in [id, slug, name] if x is not None]) > 1:
			raise Exception("Only one of 'id', 'slug', 'name' can be specified.")
		
		# check cache first
		try:
			if id:
				category = self.wordpress_object_cache.get(class_name=Category.__name__, key=str(id))
			elif slug:
				category = self.wordpress_object_cache.get(class_name=Category.__name__, key=slug)
			logger.debug("Category cache hit ({0})".format(category.s.name))
			return category
		except WPORMCacheObjectNotFoundError:
			#logger.debug("Category cache fail")
			pass # not found, fetch below

		cr = self.CategoryRequest(api=self)

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

	def CategoryRequest(self, **kwargs):
		''' Factory method that returns a new CategoryRequest attached to this API. '''
		return category.CategoryRequest(api=kwargs.pop('api', self), **kwargs)

	def comment(self, id=None):
		'''
		Returns a Comment object from the WordPress API by ID.
		'''
		if id is None:
			raise Exception("A comment 'id' must be specified.")
			
		# check cache first
		try:
			if id:
				comment = self.wordpress_object_cache.get(class_name=Comment.__name__, key=str(id))
			elif slug:
				comment = self.wordpress_object_cache.get(class_name=Comment.__name__, key=slug)
			logger.debug("Comment cache hit")
			return comment
		except WPORMCacheObjectNotFoundError:
			#logger.debug("Comment cache fail")
			pass # not found, fetch below

		cr = self.CommentRequest(api=self)
		
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

	def CommentRequest(self, **kwargs):
		''' Factory method that returns a new CommentRequest attached to this API. '''
		return comment.CommentRequest(api=kwargs.pop('api', self), **kwargs)








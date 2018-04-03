
#from .entities.post import Post, PostRequest
#from .entities.media import Media, MediaRequest
#from .entities.user import User, UserRequest

import logging

from .entities import post, user, media

#import wordpress_orm

logger = logging.getLogger("{}".format(__loader__.name.split(".")[0])) # package name

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
		# fetch the post from the provided WordPress ID
#		pr = PostRequest(api=self.api)
#		pr.wpid = wpid
#		self = pr.get()[0]
		'''
		Returns a Post object from the WordPress API.
		
		Returns all 'media' objects if no id is provided.
		'''
		pr = post.PostRequest(api=self)
		if wpid is not None:
			pr.wpid = wpid
		return_value = pr.get()
		if return_value is None:
			return None
		else:
			return return_value[0]
	
	def MediaRequest(self):
		''' Factory method that returns a new MediaRequest attached to this API. '''
		return media.MediaRequest(api=self)

	def media(self, wpid=None):
		'''
		Returns a Media object from the WordPress API.
		
		wpid : WordPress ID
		
		Returns all 'media' objects if no id is provided.
		'''
		mr = media.MediaRequest(api=self)
		if wpid is not None:
			mr.wpid = wpid
		return_value = mr.get()
		if return_value is None:
			return None
		else:
			return return_value[0]
	
	def user(self, wpid=None, username=None):
		'''
		Returns a User object from the WordPress API.
		
		wpid : WordPress ID
		
		Returns all 'user' objects if no id is provided.
		'''
		if all([wpid, username]):
			raise Exception("Only the WordPress id (wpid) or the username can be specified, not both.")

		if wpid:
			ur = user.UserRequest(api=self)
			ur.wpid = wpid
			return_value = ur.get()
			if return_value is None:
				return None
			else:
				return return_value[0]
		elif username:
			ur = user.UserRequest(api=self)
			ur.parameters = {
				"search":username
			}
			return_value = ur.get()
			if return_value is None:
				return None
			else:
				return return_value[0]

	def UserRequest(self):
		''' Factory method that returns a new UserRequest attached to this API. '''
		return user.UserRequest(api=self)

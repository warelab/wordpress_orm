'''
WordPress API reference: https://developer.wordpress.org/rest-api/reference/comments/
'''

import json
import logging
#import requests

from .wordpress_entity import WPEntity, WPRequest, context_values
from .post import PostRequest
from ..import exc

logger = logging.getLogger("{}".format(__loader__.name.split(".")[0])) # package name

order_values = ["asc", "desc"]
orderby_values = ["date", "date_gmt", "id", "include", "post", "parent", "type"]

class Comment(WPEntity):
	
	def __init__(self, id=None, session=None, api=None):
		super().__init__(api=api)
	
	def __repr__(self):
		if len(self.s.content) < 11:
			truncated_content = self.s.content
		else:
			truncated_content = self.s.content[0:10] + "..."
		return "<WP {0} object at {1} content='{2}'>".format(self.__class__.__name__, hex(id(self)), truncated_content)
	
	@property
	def schema_fields(self):
		return ["id", "author", "author_email", "author_ip", "author_name",
				"author_url", "author_user_agent", "content", "date",
				"date_gmt", "link", "parent", "post", "status", "type",
				"author_avatar_urls", "meta"]
	
	def author(self):
		'''
		Return the WordPress User object that wrote this comment, if it was a WP User, None otherwise.
		'''
		if self.author:
			ur = self.api.UserRequest()
			ur.id = self.author # 'author' field is user ID
			users = ur.get()
			if len(users) > 0:
				return users[0]
			else:
				return None
		else:
			return None

class CommentRequest(WPRequest):
	'''
	A class that encapsulates requests for WordPress comments.
	'''

	def __init__(self, api=None):
		super().__init__(api=api)
		self.id = None # WordPress ID
		
		self._context = None
		
		# parameters that undergo validation, i.e. need custom setter
		#
		# ...
		
	@property
	def parameter_names(self):
		return ["context ", "page", "per_page", "search", "after", "author",
				"author_exclude", "author_email", "before", "exclude", "include",
				"offset", "order", "orderby", "parent", "parent_exclude", "post",
				"status", "type", "password"]
	
	def get(self):
		'''
		Returns a list of 'Comment' objects that match the parameters set in this object.
		'''
		self.url = self.api.base_url + "comments"
		
		if self.id:
			self.url += "/{}".format(self.id)
		
		# -------------------
		# populate parameters
		# -------------------
		if self.context:
			self.parameters["context"] = self.context
			request_context = self.context
		else:
			request_context = "view" # default value
		
		if self.password:
			self.parameters["password"] = self.password
			
		if self.post:
			self.parameters["post"] = self.post # post ID
		# -------------------

		try:
			self.get_response()
			logger.debug("URL='{}'".format(self.request.url))
		except requests.exceptions.HTTPError:
			logger.debug("Post response code: {}".format(self.response.status_code))
			if self.response.status_code == 400: # bad request
				logger.debug("URL={}".format(self.response.url))
				raise exc.BadRequest("400: Bad request. Error: \n{0}".format(json.dumps(self.response.json(), indent=4)))
			elif self.response.status_code == 404: # not found
				return None

		comments_data = self.response.json()
		
		if isinstance(comments_data, dict):
			# only one object was returned, make it a list
			comments_data = [comments_data]
			
		comments = list()
		for d in comments_data:
			comment = Comment(api=self.api)
			comment.json = d
			
			# Properties applicable to 'view', 'edit', 'embed' query contexts
			#
			comment.s.id = d["id"]
			comment.s.author = d["author"]
			comment.s.author_name = d["author_name"]
			comment.s.author_url = d["author_url"]
			comment.s.content = d["content"]["rendered"]
			comment.s.date = d["date"]
			comment.s.link = d["link"]
			comment.s.parent = d["parent"]
			comment.s.type = d["type"]
			comment.s.author_avatar_urls = d["author_avatar_urls"]

			# Properties applicable to only 'view', 'edit' query contexts:
			#
			if request_context in ["view", "edit"]:
				comment.s.date_gmt = d["date_gmt"]
				comment.s.post = d["post"]
				comment.s.status = d["status"]
				comment.s.meta = d["meta"]
			
			
			# Properties applicable to only 'edit' query contexts:
			#
			if request_context in ["edit"]:
				comment.s.author_email = d["author_email"]
				comment.s.author_ip = d["author_ip"]
				comment.s.author_user_agent = d["author_user_agent"]

			comments.append(comment)
		
		return comments
		
	@property
	def context(self):
		if self._context is None:
			self._context = None
		return self._context
	
	@context.setter
	def context(self, value):
		if value is None:
			self._context =  None
			return
		else:
			try:
				value = value.lower()
				if value in ["view", "embed", "edit"]:
					self._context = value
					return
			except:
				pass
			raise ValueError ("'context' may only be one of ['view', 'embed', 'edit']")

	@property
	def order(self):
		return self._order;
		#return self.api_params.get('order', None)
		
	@order.setter
	def order(self, value):
		if value is None:
			self._order = None
		else:
			if isinstance(value, str):
				value = value.lower()
				if value not in order_values:
					raise ValueError('The "order" parameter must be one '+\
									 'of these values: {}'.format(order_values))
				else:
					#self.api_params['order'] = value
					self._order = value
			else:
				raise ValueError('The "order" parameter must be one of '+\
								 'these values: {} (or None).'.format(order_values))
		return self._order

	@property
	def orderby(self):
		return self.api_params.get('orderby', None)
		
	@orderby.setter
	def orderby(self, value):
		if value is None:
			self._orderby = None
		else:
			if isinstance(value, str):
				value = value.lower()
				if value not in orderby_values:
					raise ValueError('The "orderby" parameter must be one '+\
									 'of these values: {}'.format(orderby_values))
				else:
					#self.api_params['orderby'] = value
					self._orderby = value
			else:
				raise ValueError('The "orderby" parameter must be one of these '+\
								 'values: {} (or None).'.format(orderby_values))
		return self._orderby


















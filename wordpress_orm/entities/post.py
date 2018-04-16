
'''

WordPress API reference: https://developer.wordpress.org/rest-api/reference/posts/
'''

import json
import logging
import requests

from .wordpress_entity import WPEntity, WPRequest, context_values
from .user import User
from .. import exc

logger = logging.getLogger("{}".format(__loader__.name.split(".")[0])) # package name

order_values = ["asc", "desc"]
orderby_values = ["author", "date", "id", "include", "modified", "parent",
				  "relevance", "slug", "title"]

class Post(WPEntity):

	def __init__(self, id=None, session=None, api=None):
		super().__init__(api=api)
			
	def __repr__(self):
		if len(self.s.title) < 11:
			truncated_title = self.s.title
		else:
			truncated_title = self.s.title[0:10] + "..."
		return "<WP {0} object at {1}, id={2}, title='{3}'>".format(self.__class__.__name__, hex(id(self)), self.s.id, truncated_title)

	@property
	def schema_fields(self):
		return ["date", "date_gmt", "guid", "id", "link", "modified", "modified_gmt",
			   "slug", "status", "type", "password", "title", "content", "author",
			   "excerpt", "featured_media", "comment_status", "ping_status", "format",
			   "meta", "sticky", "template", "categories", "tags"]

	@property
	def featured_media(self):
		'''
		Returns the 'Media' object that is the "featured media" for this post.
		'''
		mr = self.api.MediaRequest()
		mr.id = self.s.featured_media
		media_list = mr.get()
		if len(media_list) == 1:
			return media_list[0]
		else:
			return None
			
	@property
	def user(self):
		'''
		Returns the author of this post, class: 'Author'.
		'''
		ur = self.api.UserRequest()
		ur.id = self.author # ID for the author of the object
		user_list = ur.get()
		if len(user_list) == 1:
			return user_list[0]
		else:
			raise exc.UserNotFound("User ID '{0}' not found.".format(self.author))
	

class PostRequest(WPRequest):
	'''
	A class that encapsulates requests for WordPress posts.
	'''		
	def __init__(self, api=None):		
		super().__init__(api=api)
		self.id = None # WordPress ID

		# parameters that undergo validation, i.e. need custom setter
		#self._author = None
		self._order = None
		self._orderby = None
		self._status = None
		
	@property
	def parameter_names(self):
		'''
		'''
		return ["context", "page", "per_page", "search", "after", "author",
				"author_exclude", "before", "exclude", "include", "offset",
				"order", "orderby", "slug", "status", "categories",
				"categories_exclude", "tags", "tags_exclude", "sticky"]

	def get(self):
		'''
		Returns a list of 'Post' objects that match the parameters set in this object.
		'''
		self.url = self.api.base_url + "posts"
		
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
			
		if self._status:
			self.parameters["status"] = ",".join(self.status)
			
		if self.slug:
			self.parameters["slug"] = self.slug
		
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
			
		posts_data = self.response.json()

		if isinstance(posts_data, dict):
			# only one object was returned; make it a list
			posts_data = [posts_data]
	
		posts = list()
		for d in posts_data:
			post = Post(api=self.api)
			post.json = d
			
			# Properties applicable to 'view', 'edit', 'embed' query contexts
			#
			post.s.date = d["date"]
			post.s.id = d["id"]
			post.s.link = d["link"]
			post.s.slug = d["slug"]
			post.s.type = d["type"]
			post.s.author = d["author"]
			post.s.excerpt = d["excerpt"]
			post.s.featured_media = d["featured_media"]
			
			# Properties applicable to only 'view', 'edit' query contexts:
			#
			if request_context in ["view", "edit"]:
				view_edit_properties = ["date_gmt", "guid", "modified", "modified_gmt", "status",
										"content", "comment_status", "ping_status", "format", "meta",
										"sticky", "template", "categories", "tags"]
				for key in view_edit_properties:
					setattr(post, key, d[key])
#				post.s.date_gmt = d["date_gmt"]
#				post.s.guid = d["guid"]
#				post.s.modified = d["modified"]
#				post.s.modified_gmt = d["modified_gmt"]
#				post.s.status = d["status"]
#				post.s.content = d["content"]
#				post.s.comment_status = d["comment_status"]
#				post.s.ping_status = d["ping_status"]
#				post.s.format = d["format"]
#				post.s.meta = d["meta"]
#				post.s.sticky = d["sticky"]
#				post.s.template = d["template"]
#				post.s.categories = d["categories"]
#				post.s.tags = d["tags"]
				
			# Properties applicable to only 'edit' query contexts
			#
			if request_context in ['edit']:
				post.s.password = d["password"]
			
			# Properties applicable to only 'view' query contexts
			#
			if request_context == 'view':
				post.s.title = d["title"]["rendered"]
			else:
				# not sure what the returned 'title' object looks like
				logger.debug(d)
				logger.debug(d["title"])
				logger.debug(request_context)
				raise NotImplementedError
			
			posts.append(post)
			
		return posts
	
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
	def author(self):
		#return self._author
		return self.parameters.get("author", None)
		
	@author.setter
	def author(self, value):
		''' Set author parameter for this request; stores WordPress user ID. '''
		if value is None:
			self.parameters.pop("author", None) # remove key
			self.g = None

		elif isinstance(value, User):
			self.parameters["author"] = value.s.id
			#self._author = value.id

		elif isinstance(value, int):
			self.parameters["author"] = value # assuming WordPress ID
			#self._author = value

		elif isinstance(value, str):
			# is this string value the WordPress user ID?
			try:
				self.parameters["author"] = int(value)
			except ValueError:
				pass
			# is this string value the WordPress username? If so, try to get the User object
			user = self.api.user(username=value) # raises exception
			self.parameters["author"] = user.s.id
			#self._author = user
							
		else:
			raise ValueError("Unexpected value type passed to 'author' (type: '{1}')".format(type(value)))

	
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

	@property
	def status(self):
		return self._status
	
	@status.setter
	def status(self, value):
		'''
		
		Note that 'status' may contain one or more values.
		Ref: https://developer.wordpress.org/rest-api/reference/posts/#arguments
		'''
		if value is None:
			self._status = None # set default value
			return
		try:
			value = value.lower()
			if value in ["draft", "pending", "private", "publish", "future"]:
				# may be one or more values; store as a list
				if self._status:
					self._status.append(value)
				else:
					self._status = [value]
				return
		except:
			pass
		raise ValueError("'status' must be one of ['draft', 'pending', 'private', 'publish', 'future'] ('{0}' given)".format(value))

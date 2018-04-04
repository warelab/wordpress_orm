
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

#logger = logging.getLogger("{}".format(__loader__.name.split(".")[0])) # package name

class Post(WPEntity):

	def __init__(self, wpid=None, session=None, api=None):
		super().__init__(api=api)
			
	def __repr__(self):
		if len(self.title) < 11:
			truncated_title = self.title
		else:
			truncated_title = self.title[0:10] + "..."
		return "<{0} object at {1}, id={2}, title='{3}'>".format(self.__class__.__name__, hex(id(self)), self.wpid, truncated_title)

	@property
	def schema(self):
		return ["date", "date_gmt", "guid", "id", "link", "modified", "modified_gmt",
			   "slug", "status", "type", "password", "title", "content", "author",
			   "excerpt", "featured_media", "comment_status", "ping_status", "format",
			   "meta", "sticky", "template", "categories", "tags"]

	@property
	def featured_media_object(self):
		mr = self.api.MediaRequest()
		mr.wpid = self.featured_media
		media_list = mr.get()
		if len(media_list) == 1:
			return media_list[0]
		else:
			return None
	

class PostRequest(WPRequest):
	'''
	'''
		
	def __init__(self, api=None):		
		super().__init__(api=api)
		self.wpid = None # WordPress ID

		# parameters that undergo validation, i.e. need custom setter
		self._author = None
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
		
		if self.wpid:
			self.url += "/{}".format(self.wpid)

		# populate parameters
		#
		if self.context:
			self.parameters["context"] = self.context
		if self._status:
			self.parameters["status"] = ",".join(self.status)
		
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
			post.date = d["date"]
			post.wpid = d["id"]
			post.link = d["link"]
			post.slug = d["slug"]
			post.type = d["type"]
			post.author = d["author"]
			post.excerpt = d["excerpt"]
			post.featured_media = d["featured_media"]
			
			# Properties applicable to only 'view', 'edit' query contexts:
			#
			if self.context in ["view", "edit"]:
				view_edit_properties = ["date_gmt", "guid", "modified", "modified_gmt", "status",
										"content", "comment_status", "ping_status", "format", "meta",
										"sticky", "template", "categories", "tags"]
				for key in view_edit_properties:
					setattr(post, key, d[key])
#				post.date_gmt = d["date_gmt"]
#				post.guid = d["guid"]
#				post.modified = d["modified"]
#				post.modified_gmt = d["modified_gmt"]
#				post.status = d["status"]
#				post.content = d["content"]
#				post.comment_status = d["comment_status"]
#				post.ping_status = d["ping_status"]
#				post.format = d["format"]
#				post.meta = d["meta"]
#				post.sticky = d["sticky"]
#				post.template = d["template"]
#				post.categories = d["categories"]
#				post.tags = d["tags"]
				
			# Properties applicable to only 'edit' query contexts
			#
			if self.context in ['edit']:
				post.password = d["password"]
			
			# Properties applicable to only 'view' query contexts
			#
			if self.context == 'view':
				post.title = d["title"]["rendered"]
			else:
				# not sure what the returned 'title' object looks like
				logger.debug(d)
				logger.debug(d["title"])
				logger.debug(self.context)
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
		return self._author
		
	@author.setter
	def author(self, value):
		''' Set author parameter for this request; stores WordPress user ID. '''
		if value is None:
			self.parameters.pop("author", None) # remove key
			self._author = None

		elif isinstance(value, User):
			self.parameters["author"] = value.wpid
			self._author = value.wpid

		elif isinstance(value, int):
			self.parameters["author"] = value # assuming WordPress ID
			self._author = value

		elif isinstance(value, str):
			# is this string value the WordPress user ID?
			try:
				self.parameters["author"] = int(value)
			except ValueError:
				pass
			# is this string value the WordPress username? If so, try to get the User object
			user = self.api.user(username=value) # raises exception
			self.parameters["author"] = user.wpid
			self._author = user
							
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

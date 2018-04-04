
'''

WordPress API reference: https://developer.wordpress.org/rest-api/reference/posts/
'''

import json
import logging
import requests

from .wordpress_entity import WPEntity, WPRequest, context_values
from .post import PostRequest
from ..import exc

logger = logging.getLogger("{}".format(__loader__.name.split(".")[0])) # package name

order_values = ["asc", "desc"]
orderby_values = ["id", "include", "name", "slug", "term_group", "description", "count"]

class Category(WPEntity):
	
	def __init__(self, wpid=None, session=None, api=None):
		super().__init__(api=api)
		
	def __repr__(self):
		return "<{0} object at {1} name='{2}'>".format(self.__class__.__name__, hex(id(self)), self.name)
	
	@property
	def schema(self):
		return ["id", "count", "description", "link",
				"name", "slug", "taxonomy", "parent", "meta"]
	
	def posts(self):
		pr = self.api.PostRequest()
		pr.categories.append(self)
		posts = pr.get()
		return posts

class CategoryRequest(WPRequest):
	'''
	'''
	
	def __init__(self, api=None):
		super().__init__(api=api)
		self.wpid = None # WordPress ID
		
		# parameters that undergo validation, i.e. need custom setter
		#
		self._hide_empty = None
		self._per_page = None
		
	@property
	def parameter_names(self):	
		return ["id", "count", "description", "link",
				"name", "slug", "taxonomy", "parent", "meta"]
	
	def get(self):
		'''
		Returns a list of 'Post' objects that match the parameters set in this object.
		'''
		self.url = self.api.base_url + "categories"
		
		if self.wpid:
			self.url += "/{}".format(self.wpid)

		# populate parameters
		#
		for param in ["context", "page", "per_page", "search", "exclude",
					  "include", "exclude", "include", "order", "orderby",
					  "hide_empty", "parent", "post", "slug"]:
			if getattr(self, param, None):
				self.parameters[param] = getattr(self, param)

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
				
		categories_data = self.response.json()
		
		if isinstance(categories_data, dict):
			# only one object was returned, make it a list
			categories_data = [categories_data]
			
		categories = list()
		for d in categories_data:
			#print(d)
			category = Category(api=self.api)
			category.json = d
			
			# Properties applicable to 'view', 'edit', 'embed' query contexts
			#
			category.id = d["id"]
			category.link = d["link"]
			category.name = d["name"]
			category.slug = d["slug"]
			category.taxonomy = d["taxonomy"]
			
			# Properties applicable to only 'view', 'edit' query contexts:
			#
			if self.context in ["view", "edit"]:
				category.count = d["count"]
				category.description = d["description"]
				category.parent = d["parent"]
				category.meta = d["meta"]
			
			categories.append(category)
		
		return categories

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

	@property
	def hide_empty(self):
		return self._hide_empty
	
	@hide_empty.setter
	def hide_empty(self, value):
		if isinstance(value, bool) or value is None:
			self._hide_empty = value
		else:
			raise ValueError("The property 'hide_empty' must be a Boolean value "+\
							"('{0}' provided).".format(type(value)))

	@property
	def per_page(self):
		return self._per_page
	
	@per_page.setter
	def per_page(self, value):
		if isinstance(value, str):
			try:
				value = int(value)
			except ValueError:
				raise ValueError("The 'per_page' parameter should be a number.")
			
		if isinstance(value, int):
			if value < 0:
				raise ValueError("The 'per_page' parameter should greater than zero.")
			else:
				self._per_page = value
		else:
			raise ValueError("The 'per_page' parameter should be a number.")
	
	












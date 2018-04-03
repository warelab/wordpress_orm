'''

WordPress API reference: https://developer.wordpress.org/rest-api/reference/posts/
'''

import logging
import requests

#from .post import PostRequest
from . import post
from .wordpress_entity import WPEntity, WPRequest, context_values

logger = logging.getLogger("{}".format(__loader__.name.split(".")[0])) # package name

class User(WPEntity):
	
	def __init__(self, wpid=None, session=None, api=None):
		super().__init__(api=api)
	
		# parameters that undergo validation, i.e. need custom setter
		self._context = None

	@property
	def schema(self):
		return ["id", "username", "name", "first_name", "last_name", "email", "url",
			   "description", "link", "locale", "nickname", "slug", "registered_date",
			   "roles", "password", "capabilities", "extra_capabilities", "avatar_urls", "meta"]

	@property
	def posts(self):
		pr = self.api.PostRequest()
		pr.author = self
		posts = pr.get()
		return posts
	

	def __repr__(self):
		return "<{0} object at {1}, id={2}, name='{3}'>".format(self.__class__.__name__, hex(id(self)), self.wpid, self.name)
	


class UserRequest(WPRequest):
	'''
	
	'''
	def __init__(self, api=None):
		super().__init__(api=api)
		self.wpid = None
		
	@property
	def parameter_names(self):
		return ["context", "page", "per_page", "search", "exclude",
				   "include", "offset", "order", "orderby", "slug", "roles"]
		
	def get(self):
		'''
		'''
		self.url = self.api.base_url + 'users'
		
		if self.wpid:
			self.url += "/{}".format(self.wpid)
				
		# populate parameters
		#
		if self.context:
			self.parameters["context"] = self.context

		try:
			self.get_response()
			logger.debug("URL='{}'".format(self.request.url))
		except requests.exceptions.HTTPError:
			logger.debug("User response code: {}".format(self.response.status_code))
			if self.response.status_code == 404:
				return None
			elif self.response.status_code == 404:
				return None

		users_data = self.response.json()
		
		if isinstance(users_data, dict):
			# only one object was returned; make it a list
			users_data = [users_data]
	
		users = list()
		for d in users_data:
			user = User(api=self.api)
			user.json = d
			
			# Properties applicable to 'view', 'edit', 'embed' query contexts
			#
			#   "id", "name", "url", "description", "link", "slug", "avatar_urls"
			#
			user.wpid = d["id"]
			user.name = d["name"]
			user.url = d["url"]
			user.description = d["description"]
			user.link = d["link"]
			user.slug = d["slug"]
			user.avatar_urls = d["avatar_urls"]

			# Properties applicable to only 'view', 'edit' query contexts:
			#
			if self.context in ["view", "edit"]:
				user.meta = d["meta"]
			
			# Properties applicable to only 'edit' query contexts
			#
			if self.context in ["edit"]:
				user.username = d["username"]
				user.first_name = d["first_name"]
				user.last_name = d["last_name"]
				user.email = d["email"]
				user.locale = d["locale"]
				user.nickname = d["nickname"]
				user.registered_date = d["registered_date"]
				user.roles = d["roles"]
				user.capabilities = d["capabilities"]
				user.extra_capabilities = d["extra_capabilities"]
			
			users.append(user)

		return users

	@property
	def context(self):
		return self._context
	
	@context.setter
	def context(self, value):
		if value is None:
			self._context = None
			return
		else:
			try:
				value = value.lower()
				if value in ["view", "embed", "edit"]:
					self._context = value
					return
			except:
				pass
		raise ValueError ("'context' may only be one of ['view', 'embed', 'edit'] ('{0}' given)".format(value))
				
			







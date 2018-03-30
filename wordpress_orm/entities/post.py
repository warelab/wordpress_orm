
'''

WordPress API reference: https://developer.wordpress.org/rest-api/reference/posts/
'''

from . import logger
from .wordpress_entity import WPEntity, WPRequest, context_values

order_values = ["asc", "desc"]
orderby_values = ["author", "date", "id", "include", "modified", "parent",
				  "relevance", "slug", "title"]

#logger = logging.getLogger("{}".format(__loader__.name.split(".")[0])) # package name

class Post(WPEntity):

	def __init__(self, wpid=None, session=None, api=None):

		super().__init__(api=api)

		# WordPress 'post' object schema
		# ------------------------------
		for label in self.schema:
			setattr(self, label, None)
			
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

class PostRequest(WPRequest):
	'''
	'''
		
	def __init__(self, api=None):
		super().__init__(api=api)
		self.wpid = None # WordPress id

	@property
	def argument_names(self):
		'''
		'''
		return ["context", "page", "per_page", "search", "after", "author",
				"author_exclude", "before", "exclude", "include", "offset",
				"order", "orderby", "slug", "statis", "categories",
				"categories_exclude", "tags", "tags_exclude", "sticky"]

	def get(self):
		'''
		Returns a list of 'Post' objects that match the parameters set in this object.
		'''
		self.url = self.api.base_url + "posts"
		
		if self.wpid:
			self.url += "/{}".format(self.wpid)
		
		logger.debug("URL='{}'".format(self.url))

		try:
			self.get_response()
		except requests.exceptions.HTTPError:
			logger.debug("Post response code: {}".format(self.response.status_code))
			if self.response.status_code == 404:
				return None
			elif self.response.status_code == 404:
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
	def order(self):
		return self.api_params.get('order', None)
		
	@order.setter
	def order(self, value):
		value = value.lower()
		if value not in order_values:
			raise ValueError('The "order" parameter must be one of these values: {}'.format(order_values))
		else:
			self.api_params['order'] = value

	@property
	def orderby(self):
		return self.api_params.get('orderby', None)
		
	@orderby.setter
	def orderby(self, value):
		value = value.lower()
		if value not in orderby_values:
			raise ValueError('The "orderby" parameter must be one of these values: {}'.format(orderby_values))
		else:
			self.api_params['orderby'] = value

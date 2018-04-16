
'''

WordPress API reference: https://developer.wordpress.org/rest-api/reference/media/
'''

import os
import logging

import requests

from .wordpress_entity import WPEntity, WPRequest, context_values

logger = logging.getLogger("{}".format(__loader__.name.split(".")[0])) # package name

status_values = ["publish", "future", "draft", "pending", "private"]

class Media(WPEntity):
	
	def __init__(self, id=None, api=None):
		super().__init__(api=api)
			
	def __repr__(self):
		return "<WP {0} object at {1}, id={2}, type='{3}', file='{4}'>".format(self.__class__.__name__, hex(id(self)),
																			self.s.id,
																			self.s.mime_type,
																			os.path.basename(self.s.source_url))

	@property																			
	def schema_fields(self):
		return ["date", "date_gmt", "guid", "id", "link", "modified", "modified_gmt",
			    "slug", "status", "type", "title", "author", "comment_status",
			    "ping_status", "meta", "template", "alt_text", "caption", "description",
			    "media_type", "mime_type", "media_details", "post", "source_url"]
	

class MediaRequest(WPRequest):
	'''
	'''

	def __init__(self, api=None):
		super().__init__(api=api)
		self.id = None # WordPress id
	
		# parameters that undergo validation, i.e. need custom setter
		# default values set here
		self._context = None #"view"

	@property
	def parameter_names(self):
		return ["context", "page", "per_page", "search", "after", "author",
				"author_exclude", "before", "exclude", "include", "offset",
				"order", "orderby", "parent", "parent_exclude", "slug", "status",
				"media_type", "mime_type"]
	
	def get(self):
		self.url = self.api.base_url + "media"
		
		if self.id:
			self.url += "/{}".format(self.id)
		
		logger.debug("URL='{}'".format(self.url))

		# set parameters
		if self.context:
			self.parameters["context"] = self.context
			request_context = self.context
		else:
			request_context = "view" # default value
		
		try:
			self.get_response()
		except requests.exceptions.HTTPError:
			logger.debug("Media response code: {}".format(self.response.status_code))
			if self.response.status_code == 404:
				return None
			elif self.response.status_code == 404:
				return None

		media_data = self.response.json()

		if isinstance(media_data, dict):
			# only one object was returned; make it a list
			media_data = [media_data]

		media_objects = list()
		for d in media_data:
			media = Media(api=self.api)

			# Properties applicable to 'view', 'edit', 'embed' query contexts
			#
			#logger.debug(d)
			media.s.date = d["date"]
			media.s.id = d["id"]
			media.s.link = d["link"]
			media.s.slug = d["slug"]
			media.s.type = d["type"]
			media.s.title = d["title"]
			media.s.author = d["author"]
			media.s.alt_text = d["alt_text"]
			media.s.caption = d["caption"]
			media.s.media_type = d["media_type"]
			media.s.mime_type = d["mime_type"]
			media.s.media_details = d["media_details"]
			media.s.source_url = d["source_url"]

			# Properties applicable only to 'view', 'edit' query contexts
			#
			if request_context in ["view", "edit"]:
				media.s.date_gmt = d["date_gmt"]
				media.s.guid = d["guid"]
				media.s.modified = d["modified"]
				media.s.modified_gmt = d["modified_gmt"]
				media.s.status = d["status"]
				media.s.comment_status = d["comment_status"]
				media.s.ping_status = d["ping_status"]
				media.s.meta = d["meta"]
				media.s.template = d["template"]
				media.s.description = d["description"]
				media.s.post = d["post"]
				
			media_objects.append(media)
		
		return media_objects
	
	@property
	def context(self):
		return self._context
	
	@context.setter
	def context(self, value):
		if value is None:
			self._context = None
		else:
			try:
				value = value.lower()
				if value in ["view", "embed", "edit"]:
					self._context = value
					return
			except:
				pass
			raise ValueError ("'context' may only be one of ['view', 'embed', 'edit']")


	

			



















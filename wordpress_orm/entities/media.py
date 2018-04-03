
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
	
	def __init__(self, wpid=None, api=None):
		super().__init__(api=api)
			
	def __repr__(self):
		return "<{0} object at {1}, id={2}, type='{3}', file='{4}'>".format(self.__class__.__name__, hex(id(self)),
																			self.id,
																			self.mime_type,
																			os.path.basename(self.source_url))

	@property																			
	def schema(self):
		return ["date", "date_gmt", "guid", "id", "link", "modified", "modified_gmt",
			    "slug", "status", "type", "title", "author", "comment_status",
			    "ping_status", "meta", "template", "alt_text", "caption", "description",
			    "media_type", "mime_type", "media_details", "post", "source_url"]
	

class MediaRequest(WPRequest):
	'''
	'''

	def __init__(self, api=None):
		super().__init__(api=api)
		self.wpid = None # WordPress id
	
		# parameters that undergo validation, i.e. need custom setter
		# default values set here
		self._context = "view"

	@property
	def parameter_names(self):
		return ["context", "page", "per_page", "search", "after", "author",
				"author_exclude", "before", "exclude", "include", "offset",
				"order", "orderby", "parent", "parent_exclude", "slug", "status",
				"media_type", "mime_type"]
	
	def get(self):
		self.url = self.api.base_url + "media"
		
		if self.wpid:
			self.url += "/{}".format(self.wpid)
		
		logger.debug("URL='{}'".format(self.url))

		# set parameters
		if self.context:
			self.parameters["context"] = self.context
		
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
			media.date = d["date"]
			media.id = d["id"]
			media.link = d["link"]
			media.slug = d["slug"]
			media.type = d["type"]
			media.title = d["title"]
			media.author = d["author"]
			media.alt_text = d["alt_text"]
			media.caption = d["caption"]
			media.media_type = d["media_type"]
			media.mime_type = d["mime_type"]
			media.media_details = d["media_details"]
			media.source_url = d["source_url"]

			# Properties applicable only to 'view', 'edit' query contexts
			#
			if self.context in ["view", "edit"]:
				media.date_gmt = d["date_gmt"]
				media.guid = d["guid"]
				media.modified = d["modified"]
				media.modified_gmt = d["modified_gmt"]
				media.status = d["status"]
				media.comment_status = d["comment_status"]
				media.ping_status = d["ping_status"]
				media.meta = d["meta"]
				media.template = d["template"]
				media.description = d["description"]
				media.post = d["post"]
				
			media_objects.append(media)
		
		return media_objects
	
	@property
	def context(self):
		return self._context
	
	@context.setter
	def context(self, value):
		if value is None:
			self._context =  "view" # default
		else:
			try:
				value = value.lower()
				if value in ["view", "embed", "edit"]:
					self._context = value
					return
			except:
				pass
			raise ValueError ("'context' may only be one of ['view', 'embed', 'edit']")


	

			



















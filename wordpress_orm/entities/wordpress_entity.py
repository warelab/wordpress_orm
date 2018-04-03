
from abc import ABCMeta, abstractmethod, abstractproperty

import requests

context_values = ["view", "embed", "edit"]

class WPEntity(metaclass=ABCMeta):
	'''
	Abstract superclass for all entities of the WordPress API.
	'''
	def __init__(self, api=None):
		
		if api is None:
			raise Exception("Use the 'API.{0}()' method to create a new '{0}' object.".format(self.__class__.__name__))
		
		self.api = api
		self.json = None
		
		for label in self.schema:
			setattr(self, label, None)
		
	@abstractproperty
	def schema(self):
		pass

class WPRequest(metaclass=ABCMeta):
	'''
	Abstract superclass for WordPress requests.
	'''
	def __init__(self, api=None):
		
		if api is None:
			raise Exception("Create this object ('{}') from the API object, not directly.".format(self.__class__.__name__))
		
		self.api = api
		self.parameters = dict()
		self.response = None
		
		for arg in self.parameter_names:
			setattr(self, arg, None)

		self.context = "view" # default value
	
#	@property
#	def context(self):
#		# 'view' is default value in API
#		return self.arguments.get("context", "view")

	@abstractproperty
	def parameter_names(self):
		pass

	@abstractmethod
	def get(self):
		pass
		
	def get_response(self):
		if self.response is None:
			if self.api.session is None:
				self.response = requests.get(url=self.url, params=self.parameters)
			else:
				# use existing session
				self.response = self.api.session.get(url=self.url, params=self.parameters)
		self.response.raise_for_status()
		#return self.response
	
	@property
	def request(self):
		if self.response:
			return self.response.request
		else:
			return None
#		else:
#			return self.response.request


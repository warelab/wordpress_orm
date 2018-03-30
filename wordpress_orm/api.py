
from .entities.post import Post, PostRequest
from .entities.media import Media, MediaRequest

class API:
	'''
	
	'''
	def __init__(self, url=None):
		self.base_url = url
		self.session = None
		
	def PostRequest(self):
		''' Factory method that returns a new PostRequest. '''
		return PostRequest(api=self)

	def post(self, wpid=None):
		# fetch the post from the provided WordPress ID
#		pr = PostRequest(api=self.api)
#		pr.wpid = wpid
#		self = pr.get()[0]
		'''
		Returns a Post object from the WordPress API.
		
		Returns all 'media' objects if no id is provided.
		'''
		pr = PostRequest(api=self)
		if wpid is not None:
			pr.wpid = wpid
		return_value = pr.get()
		if return_value is None:
			return None
		else:
			return pr.get()[0]
	
	def MediaRequest(self):
		''' Factory method that returns a new MediaRequest. '''
		return MediaRequest(api=self)

	def media(self, wpid=None):
		'''
		Returns a Media object from the WordPress API.
		
		wpid : WordPress ID
		
		Returns all 'media' objects if no id is provided.
		'''
		mr = MediaRequest(api=self)
		if wpid is not None:
			mr.wpid = wpid
		return_value = mr.get()
		if return_value is None:
			return None
		else:
			return mr.get()[0]

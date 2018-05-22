
class WPORMCacheObjectNotFoundError(Exception):
	pass

class WPORMCache:
	def __init__(self):
		self.cache = dict()

	def get(self, class_name=None, key=None):
		'''
		Method to retrieve wordpress-orm entity from cache; key can be WordPress 'id' or slug.
		'''
		if class_name not in self.cache:
			self.cache[class_name] = dict()
		try:
			return self.cache[class_name][key] #.get(key, None) # return 'None' if key is not found
		except KeyError:
			raise WPORMCacheObjectNotFoundError("Object of class '{0}' with key='{1}' not found".format(class_name, key))
	
	def set(self, class_name=None, key=None, value=None):
		'''
		Method to set values in the cache.
		'''
		if class_name not in self.cache:
			self.cache[class_name] = dict()
		self.cache[class_name][key] = value
		#for key in keys:
		#	self.cache[class_name][key] = value


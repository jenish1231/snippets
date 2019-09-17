import sys

from django.contrib.auth.models import User
from django.db.models import Q
from .models import *


class SelfField:
   pass

class RelatedField:

	def __init__(self, search):
		super().__init__()
		self.search = search
		print(self.search,'\n')

	@property
	def search_class(self):
		""" returns search class object """
		if self.search:
			if type(self.search) == str:
				try:
					return getattr(sys.modules[__name__], self.search)
				except:
					pass
			else:
				return self.search

		return None

	def get_ql(self, field, query):
		q = list()
		for item in self.search_class().get_mql(query=query):
			for key, value in item.items():
				q.append({field+'__'+key : value})
				
		return q


class Search:
	# returns field name of self class  
	def get_fields(self):
			return [field for field in dir(self) if not callable(getattr(self, field)) and not field.startswith('__')]
		
	def get_ql(self, field, query):
		""" Returns generated lookups for single word in a query for a field"""
		q = list()
		for item in query.split(' '): # split query for multiple word search
			q.append({ field + '__istartswith': item })
		return q 

	def get_mql(self, query):
		fields = self.get_fields()
		mql = list()
		for field in fields:
			field_obj = getattr(self, field)

			if type(field_obj) == SelfField: # calls the mql generator of self model
				mql += self.get_ql(field=field, query=query)

			elif type(field_obj) == RelatedField: # calls the mql generator of related model 
				mql += field_obj.get_ql(field=field, query=query)

		return mql

	def get_full_mql(self, query):
		q = None
		for item in self.get_mql(query=query):
			if not q:
				q = Q(**item)
			else:
				q = q | Q(**item)
		return q 		
		
	def search(self,query):
		mql = self.get_full_mql(query=query)
		return self.Meta.model.objects.filter(mql).distinct()


#
#------------------------------------------------------------
#

class UserSearch(Search):
	username = SelfField()
	first_name = SelfField()
	last_name = SelfField()
	
	class Meta:
		model = User

class CallTypeSearch(Search):
	name = SelfField()

	class Meta:
		model = CallType

class CallPurposeSearch(Search):
	name = SelfField()

	class Meta:
		model = CallPurpose

class CallStatusSearch(Search):
	name = SelfField()

	class Meta:
		model = CallStatus		

class CommunicationMediumSearch(Search):
	name = SelfField()

	class Meta:
		model = CommunicationMedium	

class CallSearch(Search):
	call_type = RelatedField(search=CallTypeSearch)
	purpose = RelatedField(search=CallPurposeSearch)
	status = RelatedField(search=CallStatusSearch)
	class Meta:
		model = Call

class DealSearch(Search):	
	title = SelfField()
	
	class Meta:
		model = Deal

class EventSearch(Search):
	print('bikash saerch type')
	location = SelfField()
	subject = SelfField()
	class Meta:
		model = Event	

class FeedSearch(Search):
	employee = RelatedField(search = UserSearch)
	date = SelfField()
	deal = RelatedField(search = DealSearch )	
	
	class Meta:
		model = Feeds

from django import forms

class SearchForm(forms.Form):
	"""
	A form to submit search criteria information
	"""

	thread = forms.ChoiceField()
	remote = forms.BooleanField(default=False)
	onsite = forms.BooleanField(default=False)
	visa = forms.BooleanField(default=False)
	interns = forms.BooleanField(default=False)
	keywords = forms.CharField()
	title_keywords = forms.CharField()

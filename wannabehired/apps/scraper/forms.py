from django import forms

from .models import Thread, Job


class SearchForm(forms.Form):
    """
    A form to submit search criteria information
    """

    thread = forms.ChoiceField(required=False)
    remote = forms.BooleanField(required=False)
    onsite = forms.BooleanField(required=False)
    visa = forms.BooleanField(required=False)
    interns = forms.BooleanField(required=False)
    keywords = forms.CharField(required=False)
    title_keywords = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['thread'].choices = [(x.pk, x.title) for x in Thread.objects.all()]
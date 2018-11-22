# from crequest.middleware import CrequestMiddleware
from django import forms

from servey.models import Answer, Question


class QuestionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.URL = kwargs.pop('URL', None)
        super.__init__(*args, **kwargs)

    def save(self, commit=True):
        question = super().save(commit=False)
        question.URL = self.URL
        question.save()



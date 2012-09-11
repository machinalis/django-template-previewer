from django import forms

class ParseForm(forms.Form):
    template = forms.CharField()

class RenderForm(forms.Form):
    template = forms.CharField()
    context = forms.CharField(widget=forms.HiddenInput)


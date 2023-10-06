from django import forms

class MessageForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, label='Message Text')

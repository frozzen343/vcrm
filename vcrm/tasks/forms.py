from django import forms

from tasks.models import Comment


class CommentEditForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']

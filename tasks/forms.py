from django import forms

from tasks.models import Comment, Task
from users.models import User


class CommentEditForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']


class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'performer', 'status', 'hours_cost', 'contacts',
                  'client', 'fire', 'drive', 'description']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        if not user.has_perm('perms.change_performer'):
            self.fields['performer'].queryset = User.objects.filter(pk=user.pk)

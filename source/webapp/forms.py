from django import forms
from .models import Article, Comment
from django.core.exceptions import ValidationError


class ArticleForm(forms.ModelForm):
    tags = forms.CharField(max_length=20, required=False, label='Тэги')

    class Meta:
        model = Article
        exclude = ['created_at', 'updated_at', 'tags']

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        tags_list = tags.split(',')
        for tag in tags_list:
            if len(tag.strip()) < 1:
                raise ValidationError('This field value should consist of tags, each of them should be greater than '
                                      '1 symbols long', code='tag_too_short')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ['created_at', 'updated_at']


class ArticleCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author', 'text']


class SimpleSearchForm(forms.Form):
    search = forms.CharField(max_length=100, required=False, label="Найти")

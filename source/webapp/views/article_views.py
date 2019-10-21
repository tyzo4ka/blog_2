from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import urlencode
from django.views.generic import ListView, DetailView, CreateView, \
    UpdateView, DeleteView
from ..forms import ArticleForm, ArticleCommentForm, SimpleSearchForm
from ..models import Article, Tag
from django.core.paginator import Paginator


class IndexView(ListView):
    context_object_name = 'articles'
    model = Article
    template_name = 'article/index.html'
    ordering = ['-created_at']
    paginate_by = 5
    paginate_orphans = 1

    def get(self, request, *args, **kwargs):
        self.form = self.get_search_form()
        self.search_query = self.get_search_query()
        self.tag_query = self.get_tag_query()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        if self.search_query:
            context['query'] = urlencode({'search': self.search_query})
        context['form'] = self.form
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.search_query:
            queryset = queryset.filter(
                Q(title__icontains=self.search_query)
                | Q(author__icontains=self.search_query)
                | Q(tags__name__iexact=self.search_query)
            )
        if self.tag_query:
            queryset = queryset.filter(
                Q(tags__name__iexact=Tag.objects.get(pk=self.tag_query))
            )
        return queryset

    def get_tag_query(self):
        if self.form.is_valid():
            return self.request.GET.get('tag')
        return None

    def get_search_form(self):
        return SimpleSearchForm(self.request.GET)

    def get_search_query(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search']
        return None


class ArticleView(DetailView):
    template_name = 'article/article.html'
    model = Article
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ArticleCommentForm()
        comments = context['article'].comments.order_by('-created_at')
        self.paginate_comments_to_context(comments, context)
        return context

    def paginate_comments_to_context(self, comments, context):
        paginator = Paginator(comments, 3, 0)
        page_number = self.request.GET.get('page', 1)
        page = paginator.get_page(page_number)
        context['paginator'] = paginator
        context['page_obj'] = page
        context['comments'] = page.object_list
        context['is_paginated'] = page.has_other_pages()


class ArticleCreateView(CreateView):
    model = Article
    template_name = 'article/create.html'
    form_class = ArticleForm

    def get_or_create_tag(self):
        tags = self.request.POST.get('tags')
        tags_list = tags.split(',')

        for tag in tags_list:
            tags, created = Tag.objects.get_or_create(name=tag.strip())
            self.object.tags.add(tags)

    def form_valid(self, form):
        self.object = form.save()
        self.get_or_create_tag()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('article_view', kwargs={'pk': self.object.pk})


class ArticleUpdateView(UpdateView):
    model = Article
    template_name = 'article/update.html'
    context_object_name = 'article'
    form_class = ArticleForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        tags = self.object.tags.all().values('name')
        tags_line = ''
        for tag in tags:
            tags_line += tag.get('name') + ','
        form.fields['tags'].initial = tags_line
        return form

    def get_or_create_tag(self):
        tags = self.request.POST.get('tags')
        tags_list = tags.split(',')
        self.object.tags.clear()

        for tag in tags_list:
            tags, created = Tag.objects.get_or_create(name=tag.strip())
            self.object.tags.add(tags)

    def form_valid(self, form):
        self.object = form.save()
        self.get_or_create_tag()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('article_view', kwargs={'pk': self.object.pk})


class ArticleDeleteView(DeleteView):
    model = Article
    template_name = 'article/delete.html'
    context_object_name = 'article'
    success_url = reverse_lazy('index')

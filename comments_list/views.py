from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.base import TemplateResponseMixin
from guestbook.models import Post

class ProductListView(ListView, TemplateResponseMixin):
    template_name = 'comments_list/my_template.html'
    model = Post
    context_object_name = 'products'
    paginate_by = 3
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Каталог коментов'
        return context
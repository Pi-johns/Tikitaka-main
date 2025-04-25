from django.contrib import sitemaps
from django.urls import reverse
from .models import Product

class ProductSitemap(sitemaps.Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.updated_at  # Use the last modified date of your model


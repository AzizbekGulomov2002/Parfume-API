from django.contrib import admin
from .models import Category, Product, ProductImages, Brand, Banner, Contact

# Register models
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImages)
admin.site.register(Brand)
admin.site.register(Banner)
admin.site.register(Contact)

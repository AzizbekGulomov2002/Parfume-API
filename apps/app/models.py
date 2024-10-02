from django.db import models
import uuid
# Category Model
class Category(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title_ru = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    icon = models.ImageField(upload_to='category_icons/')

    def __str__(self):
        return self.title_en

# Product Model
class Product(models.Model):
    title_ru = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description_ru = models.TextField()
    description_en = models.TextField()
    gender_choices = (('Male', 'Male'), ('Female', 'Female'))
    gender = models.CharField(max_length=6, choices=gender_choices)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_discounted = models.BooleanField(default=False)
    is_show_new_arrival = models.BooleanField(default=False)
    is_best_sellers = models.BooleanField(default=False)
    is_recommended = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    banner = models.ForeignKey('Banner', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.title_en

# Product Images Model
class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    images = models.ImageField(upload_to='product_images/')

# Brand Model
class Brand(models.Model):
    logo = models.ImageField(upload_to='brand_logos/')
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

# Banner Model
class Banner(models.Model):
    image_ru = models.ImageField(upload_to='banners/')
    image_en = models.ImageField(upload_to='banners/')
    link = models.URLField()

# Contact Model
class Contact(models.Model):
    info_ru = models.TextField()
    info_en = models.TextField()

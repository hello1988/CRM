from django.contrib import admin
from .models import Member, Product
# Register your models here.

class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price',)

admin.site.register(Member, MemberAdmin)
admin.site.register(Product, ProductAdmin)
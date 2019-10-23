from django.contrib import admin
from .models import Member, Product, Operator, Order, Cart
# Register your models here.

class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price',)

class OperatorAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'total_price', 'discount')

class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'product', 'quantity')


admin.site.register(Member, MemberAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Operator, OperatorAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Cart, CartAdmin)
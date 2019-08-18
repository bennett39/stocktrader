from django.contrib import admin

from .models import Profile, Stock, Transaction

# Register your models here.
admin.site.register(Profile)
admin.site.register(Stock)
admin.site.register(Transaction)

from models import SQLProfile
from django.contrib import admin

class SQLProfileAdmin(admin.ModelAdmin):
    list_display = ("url","id","millisecond")

admin.site.register(SQLProfile, SQLProfileAdmin)
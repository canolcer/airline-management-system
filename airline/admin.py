from django.contrib import admin
from .models import Airplane, Flight, Reservation

# Register your models here.

#admin.site.register(Airplane)
@admin.register(Airplane)
class ArticleAdmin(admin.ModelAdmin):
    
    list_display = ["tail_number", "model"]
    class Meta:
        model = Airplane
admin.site.register(Flight)

admin.site.register(Reservation)

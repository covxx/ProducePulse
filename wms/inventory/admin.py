from django.contrib import admin
from .models import InventoryItem, Category, Customer, Lot, Vendor, OrderCustomer, Product

admin.site.register(InventoryItem)
admin.site.register(Category)
admin.site.register(Customer)

@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = ('lot_number', 'product', 'vendor', 'quantity_in', 'quantity_used', 'date_received')
    list_filter = ('product', 'vendor', 'date_received')
    search_fields = ('lot_number', 'product__name', 'vendor__name')
    readonly_fields = ('lot_number', 'date_received')
    ordering = ('-date_received',)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('product', 'vendor')
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not obj.lot_number:
            obj.lot_number = Lot.generate_lot_number()
        super().save_model(request, obj, form, change)
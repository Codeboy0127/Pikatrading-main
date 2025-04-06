import csv
import datetime
from django.http import HttpResponse
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Order, OrderItem, ShippingRate
from django import forms
import io
from django.shortcuts import render
from django.urls import path
from django.utils.html import format_html

# ADD PDF Section in Admin Dashboard
def order_pdf(obj):
    url = reverse('admin_order_pdf', args=[obj.id])
    return mark_safe(f'<a href="{url}">PDF</a>')

order_pdf.short_description = 'Invoice'
 


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    content_disposition = f'attachment; filename={opts.verbose_name}.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = content_disposition
    writer = csv.writer(response)
    fields = [field for field in opts.get_fields() if not \
              field.many_to_many and not field.one_to_many]
    # Write a first row with header information
    writer.writerow([field.verbose_name for field in fields])
    # Write data rows
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)
    return response
export_to_csv.short_description = 'Export to CSV'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'created_at', 'total_amount' , 'status', 'payment_method','invoice_link', 'shipping_url']
    readonly_fields=('created_at',)
    list_filter = ['status',]
    inlines = [OrderItemInline]
    actions = [export_to_csv]

    def invoice_link(self, obj):
        if obj.invoice:
            return format_html('<a href="{}" target="_blank">Download Invoice</a>', obj.invoice.url)
        return "No Invoice"
    
    invoice_link.allow_tags = True
    invoice_link.short_description = "Invoice"

    def invoice_preview(self, obj):
        if obj.invoice:
            return format_html('<embed src="{}" width="300px" height="400px" />', obj.invoice.url)
        return "No Invoice Uploaded"
    
    invoice_preview.allow_tags = True
    invoice_preview.short_description = "Invoice Preview"

    def shipping_url(self, obj):
        if obj.shipping_url_printing:
            return format_html('<a href="{}" target="_blank">Print Shipping Label</a>', obj.shipping_url_printing)
        return "No Shipping Label"
    
    shipping_url.allow_tags = True
    shipping_url.short_description = "Shipping Label"

    #raw_id_fields = ['user']

#admin.site.register(Order)


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()

@admin.register(ShippingRate)
class ShippingRateAdmin(admin.ModelAdmin):
    list_display = ("combined_weight", "min_weight", "max_weight", "rate")
    change_list_template = "admin/shipping_rate_change_list.html"  # Custom template

    # Custom method to combine min_weight and max_weight in the admin list view
    def combined_weight(self, obj):
        return f"{obj.min_weight} - {obj.max_weight}"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("upload-csv/", self.admin_site.admin_view(self.upload_csv), name="shippingrate-upload-csv"),
        ]
        return custom_urls + urls
    
    def upload_csv(self, request):
        if request.method == "POST":
            form = CSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES["csv_file"]
                decoded_file = csv_file.read().decode("utf-8")
                reader = csv.reader(io.StringIO(decoded_file))
                next(reader, None)  # Skip the first row (header)
                
                for row in reader:
                    if len(row) < 3:
                        continue  # Skip rows with insufficient data
                    min_weight, max_weight, rate = row
                    ShippingRate.objects.create(
                        min_weight=float(min_weight),
                        max_weight=float(max_weight),
                        rate=float(rate),
                    )
                self.message_user(request, "CSV file imported successfully!")
                return render(request, "admin/upload_shipping_rate.html", {"form": form, "success": True})

        else:
            form = CSVUploadForm()
        return render(request, "admin/upload_shipping_rate.html", {"form": form})
    
    # Add custom button in admin panel
    def upload_csv_link(self):
        url = reverse("admin:shippingrate-upload-csv") 
        return format_html('<a href="{}" class="button">Upload Shipping Rate via CSV</a>', url)

    upload_csv_link.short_description = "Upload Shipping Rate File"

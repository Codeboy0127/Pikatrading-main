from django.urls import path

from .views import start_order,admin_order_pdf,order_detail

urlpatterns = [
    path('start_order/', start_order, name='start_order'),
    path('order_inv/<int:order_id>/pdf/', admin_order_pdf, name='admin_order_pdf'),
    path('order_detail/<int:order_id>/', order_detail, name='order_detail'),

]
from django.urls import path

from payment.views import creditcard_payment, payment_process, qrcode_payment,alipay_payment, payment_result_qr, payment_result_cd, payment_result_ali,payment_qr_notify, payment_cd_notify,payment_result_keroro

urlpatterns = [
    path('creditcard/', creditcard_payment, name='pay_creditcard'), 
    path('qrcode/', qrcode_payment, name='pay_qrcode'),
    path('alipay/', alipay_payment, name='pay_alipay'),
    path('process/', payment_process, name='payment_process'), 
    path('result_qr/', payment_result_qr, name='payment_result_qr'),
    path('result_cd/', payment_result_cd, name='payment_result_cd'),
    path('result_ali/', payment_result_ali, name='payment_result_ali'),
    path('qrcode_kbankxpika_notify/', payment_qr_notify, name='payment_qr_notify'),
    path('wechat_kbankxpika_notify/', payment_qr_notify, name='payment_wechat_notify'),# use the same method as qr notify
    path('card_kbankxpika_notify/', payment_cd_notify, name='payment_cd_notify'),
    path('ali_kbankxpika_notify/', payment_cd_notify, name='payment_ali_notify'),
    path('result_keroro/', payment_result_keroro, name='payment_result_keroro'), # Use power of captian to get through winning victory
]
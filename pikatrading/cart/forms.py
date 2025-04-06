from django import forms

class CheckoutForm(forms.Form):

    ## SHIPPING INFORMATION ##
    first_name = forms.CharField(max_length=100,required=True)
    last_name = forms.CharField(max_length=100 , required=True)
    address = forms.CharField(max_length=255, required=True)
    zipcode = forms.CharField(max_length=100 , required=True)
    place = forms.CharField(max_length=255, required=True)

    

    ## BILLING INFORMATION ##
    same_as_shipping = forms.CharField(max_length=100, required=False)
    first_name_billing = forms.CharField(max_length=100, required=False)
    last_name_billing = forms.CharField(max_length=100 , required=False)
    address_billing = forms.CharField(max_length=255, required=False)
    zipcode_billing = forms.CharField(max_length=100 , required=False)
    place_billing = forms.CharField(max_length=255, required=False)

    ## PERSONEL INFORMATION ##    
    email = forms.CharField(max_length=100, required=True)
    phone = forms.CharField(max_length=100, required=True)

    ## Payment Method ##
    payment_method = forms.CharField(max_length=255, required=True)

    def clean(self):
        cleaned_data = super().clean()  # Get the cleaned data for all fields
        same_as_shipping = cleaned_data.get("same_as_shipping")
        print('check ja:', same_as_shipping)
        ## CHECK BILLING INFORMATION ##
        
        if same_as_shipping != "yes":

            first_name_billing = cleaned_data.get("first_name_billing")
            last_name_billing = cleaned_data.get("last_name_billing")
            address_billing = cleaned_data.get("address_billing")
            zipcode_billing = cleaned_data.get("zipcode_billing")
            place_billing = cleaned_data.get("place_billing")

            # Check if 'name' is blank or contains only spaces
            if not first_name_billing or not first_name_billing.strip():
                self.add_error('first_name_billing', "First name cannot be blank.")
            # Check if 'last name' is blank or contains only spaces
            if not last_name_billing or not last_name_billing.strip():
                self.add_error('last_name_billing', "Last name cannot be blank.")
            # Check if 'address' is blank or contains only spaces
            if not address_billing or not address_billing.strip():
                self.add_error('address_billing', "Address cannot be blank.")
            # Check if 'zipcode' is blank or contains only spaces
            if not zipcode_billing or not zipcode_billing.strip():
                self.add_error('zipcode_billing', "Zip Code cannot be blank.")
            # Check if 'zipcode' is blank or contains only spaces
            if not place_billing or not place_billing.strip():
                self.add_error('place_billing', "City/Place cannot be blank.")
            
                        
        return cleaned_data
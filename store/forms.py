from django import forms
from .models import Enquiry

class EnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ["name", "email", "phone", "subject", "message", "preferred_date", "preferred_time"]
        widgets = {"message": forms.Textarea(attrs={"rows": 5}), "preferred_date": forms.DateInput(attrs={"type": "date"})}

class ContactForm(EnquiryForm):
    class Meta(EnquiryForm.Meta):
        fields = ["name", "email", "phone", "subject", "message"]

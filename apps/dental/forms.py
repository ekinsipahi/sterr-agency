from django import forms

from .models import DentalInquiry


class InquiryForm(forms.ModelForm):
    """Labels and option texts come from the page language (see `localize`)."""

    fax = forms.CharField(required=False, widget=forms.HiddenInput)  # honeypot
    consent = forms.BooleanField(required=True)

    class Meta:
        model = DentalInquiry
        fields = ["kind", "name", "email", "phone", "country", "company", "treatment", "message"]
        widgets = {
            "kind": forms.RadioSelect,
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel"}),
            "country": forms.TextInput(attrs={"autocomplete": "country-name"}),
            "company": forms.TextInput(attrs={"autocomplete": "organization"}),
            "message": forms.Textarea(attrs={"rows": 4}),
        }

    def localize(self, ui):
        self.ui = ui
        f = self.fields
        f["kind"].choices = [(k, ui["types"][k]) for k, _ in DentalInquiry.TYPES]
        f["treatment"].choices = [("", "—")] + [(k, ui["treatments"][k]) for k, _ in DentalInquiry.TREATMENTS]
        for name in ("kind", "name", "email", "phone", "country", "company", "treatment", "message"):
            f[name].label = ui[f"f_{name}"]
        f["message"].widget.attrs["placeholder"] = ui["f_message_ph"]
        f["consent"].label = ui["f_consent"]
        return self

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if sum(ch.isdigit() for ch in phone) < 7:
            raise forms.ValidationError(self.ui["err_phone"])
        return phone.strip()

    def is_spam(self):
        return bool(self.data.get("fax"))

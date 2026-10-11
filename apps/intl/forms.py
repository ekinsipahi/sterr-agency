from django import forms

from .models import IntlLead


class IntlLeadForm(forms.ModelForm):
    """Labels and option texts come from the page language (see `localize`)."""

    fax = forms.CharField(required=False, widget=forms.HiddenInput)  # honeypot
    consent = forms.BooleanField(required=True)

    class Meta:
        model = IntlLead
        fields = ["interest", "name", "email", "phone", "company", "website", "country", "message"]
        widgets = {
            "interest": forms.RadioSelect,
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel"}),
            "company": forms.TextInput(attrs={"autocomplete": "organization"}),
            "country": forms.TextInput(attrs={"autocomplete": "country-name"}),
            "message": forms.Textarea(attrs={"rows": 4}),
        }

    def localize(self, ui):
        self.ui = ui
        f = self.fields
        f["interest"].choices = [(k, ui["interests"][k]) for k, _ in IntlLead.INTERESTS]
        for name in self.Meta.fields:
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

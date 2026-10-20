import re

from django import forms

HANDLE_RE = re.compile(r"^[A-Za-z0-9._]{1,30}$")


def clean_handle(value):
    """'@brand', 'instagram.com/brand/', 'https://www.instagram.com/brand?igsh=..' -> 'brand'."""
    value = (value or "").strip()
    m = re.search(r"instagram\.com/([^/?#\s]+)", value)
    if m:
        value = m.group(1)
    return value.lstrip("@").strip().strip("/")


class GrowthForm(forms.Form):
    instagram = forms.CharField(max_length=80)
    location = forms.CharField(max_length=120)
    email = forms.EmailField(max_length=254)
    consent = forms.BooleanField()
    fax = forms.CharField(required=False)  # honeypot

    def __init__(self, *args, ui=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = ui or {}
        attrs = {
            "instagram": {"placeholder": self.ui.get("f_instagram_ph", ""), "autocomplete": "off", "autocapitalize": "none", "spellcheck": "false"},
            "location": {"placeholder": self.ui.get("f_location_ph", "")},
            "email": {"placeholder": self.ui.get("f_email_ph", ""), "autocomplete": "email"},
            "fax": {"tabindex": "-1", "autocomplete": "off"},
        }
        for name, extra in attrs.items():
            self.fields[name].widget.attrs.update(extra)
        self.fields["instagram"].label = self.ui.get("f_instagram")
        self.fields["location"].label = self.ui.get("f_location")
        self.fields["email"].label = self.ui.get("f_email")
        self.fields["consent"].label = self.ui.get("f_consent")

    def is_spam(self):
        return bool(self.data.get("fax"))

    def clean_instagram(self):
        handle = clean_handle(self.cleaned_data["instagram"])
        if not HANDLE_RE.match(handle):
            raise forms.ValidationError(self.ui.get("err_instagram", "Invalid username."))
        return handle.lower()

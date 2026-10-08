from django import forms

from .models import Lead


class LeadForm(forms.ModelForm):
    # Honeypot: real people never see or fill this.
    fax = forms.CharField(required=False, widget=forms.HiddenInput)
    kvkk = forms.BooleanField(
        required=True,
        error_messages={"required": "Devam etmek için aydınlatma metnini onaylamanız gerekir."},
    )

    class Meta:
        model = Lead
        fields = [
            "sector", "goal", "budget", "has_content", "timeline", "city",
            "name", "company", "phone", "email", "website", "message",
        ]
        widgets = {
            "sector": forms.RadioSelect,
            "goal": forms.RadioSelect,
            "budget": forms.RadioSelect,
            "has_content": forms.RadioSelect,
            "timeline": forms.RadioSelect,
            "message": forms.Textarea(attrs={"rows": 4, "placeholder": "İşletmenizden ve hedefinizden kısaca bahsedin."}),
            "name": forms.TextInput(attrs={"autocomplete": "name", "placeholder": "Adınız Soyadınız"}),
            "company": forms.TextInput(attrs={"autocomplete": "organization", "placeholder": "İşletme / marka adı"}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel", "placeholder": "05xx xxx xx xx"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "ornek@firma.com"}),
            "website": forms.TextInput(attrs={"placeholder": "firma.com veya @instagram"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Drop Django's "---------" blank option from radio groups.
        for name in ("sector", "goal", "budget", "has_content", "timeline"):
            self.fields[name].choices = [c for c in self.fields[name].choices if c[0]]
        self.fields["has_content"].required = True
        self.fields["timeline"].required = True
        self.fields["city"].choices = [("", "İl seçin")] + list(self.fields["city"].choices)[1:]

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        digits = "".join(ch for ch in phone if ch.isdigit())
        if len(digits) < 10:
            raise forms.ValidationError("Lütfen geçerli bir telefon numarası girin.")
        return phone.strip()

    def is_spam(self) -> bool:
        return bool(self.data.get("fax"))

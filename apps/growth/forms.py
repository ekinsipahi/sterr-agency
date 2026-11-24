import re

from django import forms

from .plan import CHOICES as PLAN_CHOICES, DEFAULT_PLAN

HANDLE_RE = re.compile(r"^[A-Za-z0-9._]{1,30}$")            # Instagram and TikTok usernames
YOUTUBE_HANDLE_RE = re.compile(r"^[A-Za-z0-9._-]{3,30}$")    # YouTube handles (@name): what Linksterr accepts
PHONE_RE = re.compile(r"^\+?\d{7,15}$")
PASSWORD_MIN = 8


def clean_handle(value):
    """'@brand', 'instagram.com/brand/', 'https://www.instagram.com/brand?igsh=..', 'tiktok.com/@brand',
    'https://www.youtube.com/@brand/videos' -> 'brand'. A YouTube link without an @name
    (/channel/UC…, /c/…) stays as it is and fails the handle check."""
    value = (value or "").strip()
    m = re.search(r"(?:instagram\.com/|tiktok\.com/@?|youtube\.com/@)([^/?#\s]+)", value, re.I)
    if m:
        value = m.group(1)
    return value.lstrip("@").strip().strip("/")


def valid_handle(handle, platform):
    return bool((YOUTUBE_HANDLE_RE if platform == "youtube" else HANDLE_RE).match(handle or ""))


YOUTUBE_VIDEO_RE = re.compile(
    r"^(?:https?://)?(?:www\.|m\.)?(?:youtube\.com/(?:watch\?(?:[^#\s]*&)?v=|(shorts)/|live/)|youtu\.be/)"
    r"([A-Za-z0-9_-]{11})(?:[?&#/].*)?$", re.I)


def clean_video_url(value):
    """A YouTube video link in any common form -> 'https://www.youtube.com/watch?v=<id>'
    (a Short: '/shorts/<id>'); '' when empty; None when it isn't a YouTube video link."""
    value = (value or "").strip()
    if not value:
        return ""
    m = YOUTUBE_VIDEO_RE.match(value)
    if not m:
        return None
    return f"https://www.youtube.com/shorts/{m.group(2)}" if m.group(1) else f"https://www.youtube.com/watch?v={m.group(2)}"


class _UIForm(forms.Form):
    """Labels, placeholders and errors come from the page language's UI strings."""

    labels = {}
    placeholders = {}

    def __init__(self, *args, ui=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = ui or {}
        for name, key in self.labels.items():
            if name in self.fields:
                self.fields[name].label = self.ui.get(key)
        for name, key in self.placeholders.items():
            if name in self.fields:
                self.fields[name].widget.attrs["placeholder"] = self.ui.get(key, "")
        for field in self.fields.values():
            field.error_messages["required"] = self.ui.get("err_required", field.error_messages["required"])
        if "email" in self.fields:
            self.fields["email"].widget.attrs["autocomplete"] = "email"
            self.fields["email"].error_messages["invalid"] = self.ui.get("err_email", "Enter a valid email.")

    def clean_email(self):
        return (self.cleaned_data["email"] or "").strip().lower()


class OrderForm(_UIForm):
    """Influencer package, account handle and target location; email + password unless signed in.
    `platform` decides the handle rule; on YouTube the form also takes an optional video link."""

    plan = forms.ChoiceField(choices=PLAN_CHOICES, initial=DEFAULT_PLAN, widget=forms.RadioSelect)
    handle = forms.CharField(max_length=120)
    video_url = forms.CharField(max_length=300, required=False)  # YouTube only
    location = forms.CharField(max_length=120)
    phone = forms.CharField(max_length=32)
    email = forms.EmailField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}), strip=False)
    consent = forms.BooleanField()
    fax = forms.CharField(required=False)  # honeypot

    labels = {"handle": "f_handle", "video_url": "f_video", "location": "f_location", "phone": "f_phone", "email": "f_email",
              "password": "f_password", "consent": "f_consent"}
    placeholders = {"handle": "f_handle_ph", "video_url": "f_video_ph", "location": "f_location_ph", "phone": "f_phone_ph",
                    "email": "f_email_ph"}

    def __init__(self, *args, user=None, account_fields=True, platform="instagram", **kwargs):
        super().__init__(*args, **kwargs)
        self.platform = platform
        if platform == "youtube":
            self.fields["video_url"].widget.input_type = "url"
            self.fields["video_url"].widget.attrs.update({"autocomplete": "off", "inputmode": "url", "spellcheck": "false"})
        else:
            del self.fields["video_url"]
        if user is not None and user.is_authenticated:
            # Signed in: the order goes to this account, no email or password asked.
            del self.fields["email"], self.fields["password"]
        elif not account_fields:
            # "Continue with Google": the account comes from Google, the fields stay on the page.
            self.fields["email"].required = self.fields["password"].required = False
        self.fields["handle"].widget.attrs.update({"autocomplete": "off", "autocapitalize": "none", "spellcheck": "false"})
        self.fields["phone"].widget.input_type = "tel"
        self.fields["phone"].widget.attrs.update({"autocomplete": "tel", "inputmode": "tel"})
        self.fields["fax"].widget.attrs.update({"tabindex": "-1", "autocomplete": "off"})
        self.fields["plan"].error_messages["invalid_choice"] = self.ui.get("err_plan", "Choose a package.")

    def is_spam(self):
        return bool(self.data.get("fax"))

    def clean_phone(self):
        """'+90 532 123 45 67', '(0532) 123-4567', '0090…' -> '+905321234567' / '05321234567'."""
        phone = re.sub(r"[\s().\-/]", "", self.cleaned_data["phone"] or "")
        if phone.startswith("00"):
            phone = "+" + phone[2:]
        if not PHONE_RE.match(phone):
            raise forms.ValidationError(self.ui.get("err_phone", "Enter a valid phone number."))
        return phone

    def clean_handle(self):
        handle = clean_handle(self.cleaned_data["handle"])
        if not valid_handle(handle, self.platform):
            raise forms.ValidationError(self.ui.get("err_handle", "Invalid username."))
        return handle.lower()

    def clean_video_url(self):
        video = clean_video_url(self.cleaned_data.get("video_url"))
        if video is None:
            raise forms.ValidationError(self.ui.get("err_video", "Paste a link to a YouTube video."))
        return video

    def clean_password(self):
        password = self.cleaned_data["password"]
        if not password and not self.fields["password"].required:
            return password
        if len(password) < PASSWORD_MIN:
            raise forms.ValidationError(self.ui.get("err_password", "Use at least 8 characters."))
        return password


class LoginForm(_UIForm):
    email = forms.EmailField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}), strip=False)
    labels = {"email": "f_email", "password": "f_password"}
    placeholders = {"email": "f_email_ph"}


class SignupForm(_UIForm):
    email = forms.EmailField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}), strip=False)
    consent = forms.BooleanField()
    labels = {"email": "f_email", "password": "f_password", "consent": "f_consent"}
    placeholders = {"email": "f_email_ph"}

    def clean_password(self):
        password = self.cleaned_data["password"]
        if len(password) < PASSWORD_MIN:
            raise forms.ValidationError(self.ui.get("err_password", "Use at least 8 characters."))
        return password


class ResetRequestForm(_UIForm):
    email = forms.EmailField(max_length=150)
    labels = {"email": "f_email"}
    placeholders = {"email": "f_email_ph"}


class NewPasswordForm(_UIForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}), strip=False)
    labels = {"password": "new_password"}

    def clean_password(self):
        password = self.cleaned_data["password"]
        if len(password) < PASSWORD_MIN:
            raise forms.ValidationError(self.ui.get("err_password", "Use at least 8 characters."))
        return password

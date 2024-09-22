from django import forms

from ticsys.fields import MultipleFileField

from .models import Share
from ticket.models import Comment


class ShareForm(forms.ModelForm):
    class Meta:
        model = Share
        fields = [
            "ticket",
        ]


class CommentShareForm(forms.ModelForm):
    files = MultipleFileField(
        required=False,
        help_text="Файлы",
        label="Прикрепить файлы",
    )

    user_fingerprint = forms.CharField(
        required=False, widget=forms.HiddenInput(), label="user_fingerprint"
    )

    class Meta:
        model = Comment
        fields = [
            "text",
        ]

        widgets = {
            "is_for_report": forms.HiddenInput(),
        }

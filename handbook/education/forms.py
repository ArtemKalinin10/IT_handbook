# forms.py
from django import forms

class SubmissionForm(forms.Form):
    code = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "code-area",
                "placeholder": "Введите решение здесь...",
                "spellcheck": "false",
                "rows": 1,
            }
        )
    )

    def clean_code(self):
        code = self.cleaned_data["code"].strip()
        if not code:
            raise forms.ValidationError("Код не может быть пустым")
        return code

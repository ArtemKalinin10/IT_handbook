from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.forms import CharField, EmailField, Form, ModelForm, PasswordInput, TextInput, ValidationError

User = get_user_model()

class RegistrationForm(UserCreationForm):

    email = EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "input"
            })

        self.fields["username"].widget.attrs["placeholder"] = "Имя"
        self.fields["email"].widget.attrs["placeholder"] = "Почта"
        self.fields["password1"].widget.attrs["placeholder"] = "Пароль"
        self.fields["password2"].widget.attrs["placeholder"] = "Повторите пароль"

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Пользователь с такой почтой уже существует")

        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        user.email = self.cleaned_data["email"].lower()

        if commit:
            user.save()
            student_group, _ = Group.objects.get_or_create(name="Student")
            user.groups.add(student_group)

        return user
        
class LoginForm(Form):
    username_email = CharField(
        widget=TextInput(attrs={
            "placeholder": "Логин или почта",
            "class": "input"
        })
    )
    password = CharField(
        widget=PasswordInput(attrs={
            "placeholder": "Пароль",
            "class": "input"
        })
    )

class ProfileSettingsForm(ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({
            "placeholder": "Логин",
            "class": "input"
        })
        self.fields["email"].widget.attrs.update({
            "placeholder": "Почта",
            "class": "input"
        })

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Пользователь с такой почтой уже существует")

        return email.lower()

class PasswordSettingsForm(PasswordChangeForm):
    old_password = CharField(
        widget=PasswordInput(attrs={
            "placeholder": "Введите текущий пароль",
            "class": "input"
        })
    )
    new_password1 = CharField(
        widget=PasswordInput(attrs={
            "placeholder": "Введите новый пароль",
            "class": "input"
        })
    )
    new_password2 = CharField(
        widget=PasswordInput(attrs={
            "placeholder": "Повторите новый пароль",
            "class": "input"
        })
    )

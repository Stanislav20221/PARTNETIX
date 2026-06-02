from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class AdminUserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'email',
            'phone',
            'company',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            'first_name': 'ФИО',
            'email': 'Email',            
            'phone': 'Телефон',
            'company': 'Компания',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }

        for field_name, field in self.fields.items():
            css_class = 'form-input'
            if field_name == 'avatar':
                field.widget.attrs.update({'class': css_class})
            else:
                field.widget.attrs.update({
                    'class': css_class,
                    'placeholder': placeholders.get(field_name, ''),
                })
    def save(self, commit=True):
            user = super().save(commit=False)
            user.username = self.cleaned_data['email']

            if commit:
                user.save()
            return user        


class AdminLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите логин',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите пароль',
        })
    )
class ProfileUpdateForm(forms.ModelForm):
    delete_avatar = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone',
            'company',
            'avatar',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
            'phone': 'Телефон',
            'company': 'Компания',
        }

        for field_name, field in self.fields.items():
            if field_name != 'avatar':
                field.widget.attrs.update({
                    'class': 'form-input',
                    'placeholder': placeholders.get(field_name, ''),
                })
            else:
                field.widget.attrs.update({
                    'class': 'form-input'
                })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
            'phone': 'Телефон',
            'company': 'Компания',
        }

        for field_name, field in self.fields.items():
            if field_name != 'avatar':
                field.widget.attrs.update({
                    'class': 'form-input',
                    'placeholder': placeholders.get(field_name, ''),
                })
            else:
                field.widget.attrs.update({
                    'class': 'form-input'
                })    
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class ClientRegistrationForm(forms.Form):
    full_name = forms.CharField(
        label='ФИО',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'ФИО',
        })
    )

    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email',
        })
    )

    phone = forms.CharField(
        label='Телефон',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Телефон',
        })
    )
    company = forms.CharField(
        label='Компания',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Компания',
        })
    )

    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Пароль',
        })
    )

    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Подтверждение пароля',
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')

        return email

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            self.add_error('password2', 'Пароли не совпадают.')

        return cleaned_data                
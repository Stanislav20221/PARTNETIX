from django import forms
from .models import Offer, PartnerRegistration
from django.contrib.auth import get_user_model

class OfferCreateForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = (
            'title',
            'description',
            'payout_type',
            'reward',
            'activity_start',
            'activity_end',
        
        )
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Название оффера',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Описание оффера',
                'rows': 4,
            }),
            'payout_type': forms.Select(attrs={
                'class': 'form-input',
            }),
            'reward': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Вознаграждение',
                'step': '0.01',
            }),
            'activity_start': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
            }),
            'activity_end': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
            }),
        }
class OfferUpdateForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = (
            'title',
            'description',
            'payout_type',
            'reward',
            'activity_start',
            'activity_end',
        
        )
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Название оффера',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Описание оффера',
                'rows': 4,
            }),
            'payout_type': forms.Select(attrs={
                'class': 'form-input',
            }),
            'reward': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Вознаграждение',
                'step': '0.01',
            }),
            'activity_start': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
            }),
            'activity_end': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
            }),
        
        }

    def clean(self):
        cleaned_data = super().clean()
        payout_type = cleaned_data.get('payout_type')

        if payout_type == 'partner_status':
            cleaned_data['reward'] = 0

        return cleaned_data        
class OfferUpdateForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = (
            'title',
            'description',
            'payout_type',
            'reward',
            'activity_start',
            'activity_end',
        )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Название оффера'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Описание оффера', 'rows': 4}),
            'payout_type': forms.Select(attrs={'class': 'form-input'}),
            'reward': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Вознаграждение', 'step': '0.01'}),
            'activity_start': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'activity_end': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('payout_type') == 'partner_status':
            cleaned_data['reward'] = 0
        return cleaned_data


User = get_user_model()


class OfferCreateForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = (
            'title',
            'description',
            'payout_type',
            'reward',
            'activity_start',
            'activity_end',
        )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Название оффера'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Описание оффера', 'rows': 4}),
            'payout_type': forms.Select(attrs={'class': 'form-input'}),
            'reward': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Вознаграждение', 'step': '0.01'}),
            'activity_start': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'activity_end': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('payout_type') == 'partner_status':
            cleaned_data['reward'] = 0
        return cleaned_data


class OfferUpdateForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = (
            'title',
            'description',
            'payout_type',
            'reward',
            'activity_start',
            'activity_end',
        )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Название оффера'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Описание оффера', 'rows': 4}),
            'payout_type': forms.Select(attrs={'class': 'form-input'}),
            'reward': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Вознаграждение', 'step': '0.01'}),
            'activity_start': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'activity_end': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('payout_type') == 'partner_status':
            cleaned_data['reward'] = 0
        return cleaned_data


class PartnerRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Пароль',
            'autocomplete': 'new-password'
        })
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Подтверждение пароля',
        })
    )
    status_display = forms.CharField(
        label='Статус',
        required=False,
        disabled=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Статус',
        })
    )
    inviter_name = forms.CharField(
        label='ФИО пригласившего',
        required=False,
        disabled=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'ФИО пригласившего',
        })
    )

    class Meta:
        model = PartnerRegistration
        fields = (
            'partner_type',
            'full_name',
            'email',
            'phone',
            'activity_type',
            'company_name',
            'company_full_name',
            'company_short_name',
            'postal_address',
            'legal_address',
            'inn',
            'kpp',
            'contact_person_name',
        )
        widgets = {
            'partner_type': forms.HiddenInput(),
            'full_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'ФИО',
                'autocomplete': 'off'   # ← ВОТ СЮДА
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Email',
                'autocomplete': 'off'
            }),

            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'id': 'phone-input',
                'placeholder': '+7 (999) 123-45-67',
            }),
            'activity_type': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Вид деятельности',
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Название компании',
            }),
            'company_full_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Полное название организации',
            }),
            'company_short_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Сокращенное название организации',
            }),
            'postal_address': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Почтовый адрес',
            }),
            'legal_address': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Юридический адрес',
            }),
            'inn': forms.TextInput(attrs={
                'class': 'form-input',
                'id': 'inn-input',
                'inputmode': 'numeric',
                'placeholder': 'ИНН',
                'maxlength': '12',
            }),

            'kpp': forms.TextInput(attrs={
                'class': 'form-input',
                'id': 'kpp-input',
                'inputmode': 'numeric',
                'placeholder': 'КПП (9 цифр)',
                'maxlength': '9',
            }),
            
            'contact_person_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'ФИО контактного лица',
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        partner_type = cleaned_data.get('partner_type')

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Пароли не совпадают.')

        if partner_type == 'individual':
            required_fields = ['full_name', 'email', 'phone', 'activity_type']
        elif partner_type == 'company':
            required_fields = [
                'email',
                'phone',
                'company_full_name',
                'company_short_name',
                'postal_address',
                'legal_address',
                'inn',
                'kpp',
                'contact_person_name',
            ]
        elif partner_type == 'self_employed':
            required_fields = ['full_name', 'email', 'phone', 'activity_type', 'company_name']
        else:
            required_fields = []

        for field_name in required_fields:
            if not cleaned_data.get(field_name):
                self.add_error(field_name, 'Это поле обязательно.')

        return cleaned_data
class PartnerCreateByUserForm(forms.ModelForm):
    offer = forms.ModelChoiceField(
        queryset=Offer.objects.none(),
        label='Оффер',
        empty_label="Выберите оффер",  
        widget=forms.Select(attrs={'class': 'form-input custom-select'})
    )

    class Meta:
        model = PartnerRegistration
        fields = (
            'partner_type',
            'full_name',
            'email',
            'phone',
            'activity_type',
            'company_name',
            'company_full_name',
            'company_short_name',
            'postal_address',
            'legal_address',
            'inn',
            'kpp',
            'contact_person_name',
            'offer',
        )
        widgets = {
            'partner_type': forms.Select(attrs={'class': 'form-input'}),
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ФИО'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'id': 'phone-input',
                'placeholder': '+7 (999) 123-45-67'
            }),

            'activity_type': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Вид деятельности'}),
            'company_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Название компании'}),
            'company_full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Полное название организации'}),
            'company_short_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Сокращенное название организации'}),
            'postal_address': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Почтовый адрес'}),
            'legal_address': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Юридический адрес'}),
            'inn': forms.TextInput(attrs={
                'class': 'form-input',
                'id': 'inn-input',
                'inputmode': 'numeric',
                'placeholder': 'ИНН',
                'maxlength': '12',
            }),
            'kpp': forms.TextInput(attrs={
            'class': 'form-input',
            'id': 'kpp-input',
            'inputmode': 'numeric',
            'placeholder': 'КПП (9 цифр)',
            'maxlength': '9',
        }),
            'contact_person_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ФИО контактного лица'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['offer'].queryset = Offer.objects.filter(
                current_user=user
            ).order_by('title')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email
    def clean_inn(self):
        inn = (self.cleaned_data.get('inn') or '').strip()
        partner_type = self.data.get('partner_type') or self.cleaned_data.get('partner_type')

        if not inn:
            return inn

        if not inn.isdigit():
            raise forms.ValidationError('ИНН должен содержать только цифры.')

        if partner_type == 'company':
            if len(inn) != 10:
                raise forms.ValidationError('Для юридического лица ИНН должен содержать 10 цифр.')
        elif partner_type in ['individual', 'self_employed']:
            if len(inn) != 12:
                raise forms.ValidationError('Для физического лица и самозанятого ИНН должен содержать 12 цифр.')

        return inn
    def clean(self):
        cleaned_data = super().clean()
        partner_type = cleaned_data.get('partner_type')

        if partner_type == 'individual':
            required_fields = ['full_name', 'email', 'phone', 'activity_type', 'offer']
        elif partner_type == 'company':
            required_fields = [
                'email',
                'phone',
                'activity_type',
                'company_full_name',
                'company_short_name',
                'postal_address',
                'legal_address',
                'inn',
                'kpp',
                'contact_person_name',
                'offer',
            ]
        elif partner_type == 'self_employed':
            required_fields = ['full_name', 'email', 'phone', 'activity_type', 'company_name', 'offer']
        else:
            required_fields = []

        for field_name in required_fields:
            if not cleaned_data.get(field_name):
                self.add_error(field_name, 'Это поле обязательно.')

        return cleaned_data
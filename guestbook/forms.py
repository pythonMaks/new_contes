from django import forms

class MyForm(forms.Form):
    user_name = forms.CharField(label='Имя пользователя')
    user_text = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label='Текст')
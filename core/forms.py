from django import forms
from .models import Submission, Task
from crispy_forms.layout import Submit, Layout, Fieldset
from crispy_forms.helper import FormHelper


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['code']
        widgets = {
            'code': forms.Textarea(attrs={'rows': 10}),
        }
        


class TaskForm(forms.ModelForm):
    name = forms.CharField(label='Название')
    LANGUAGES = (('python','Python'), ('kotlinc','Kotlin'), ('node','JavaScript'),('java', 'Java'))
    language = forms.ChoiceField(choices = LANGUAGES, label= 'Язык')
    description = forms.CharField(label='Описание',widget=forms.Textarea(attrs={'rows': 10}))
    input = forms.CharField(label='Тест№1. Ввод',)
    output = forms.CharField(label='Тест№1. Вывод',)
    input1 = forms.CharField(label='Тест№2. Ввод',)
    output1 = forms.CharField(label='Тест№2. Вывод',)
    input2 = forms.CharField(label='Тест№3. Ввод',)
    output2 = forms.CharField(label='Тест№3. Вывод')
    
    class Meta:
        model = Task
        fields = ['language', 'name', 'description', 'input', 'output', 'input1', 'output1', 'input2', 'output2']

    def __init__(self, *args, **kwargs):
        user_language = kwargs.pop('user_language', 'python')
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['language'].initial = user_language
        self.fields['language'].choices = self.LANGUAGES
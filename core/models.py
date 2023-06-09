from django.db import models
from pytils.translit import slugify
from django.urls import reverse

class Task(models.Model):
    language = models.CharField(("language"), max_length=150, blank=True)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    input = models.TextField()
    output = models.TextField()
    input1 = models.TextField(null=True)
    output1 = models.TextField(null=True)
    input2 = models.TextField(null=True)
    output2 = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    prepod = models.CharField(max_length=150, null=True) 
    
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('task_detail', kwargs={'slug': self.slug})
    
    def get_language(self):
        LANGUAGE_CHOICES = {
        'python': 'Python',
        'kotlinc': 'Kotlin',
        'node': 'JavaScript',
        'java': 'Java',
    }
        return LANGUAGE_CHOICES.get(self.language)
    
def slugify_task_name(sender, instance, **kwargs):
    instance.slug = slugify(instance.name)

models.signals.pre_save.connect(slugify_task_name, sender=Task)

class Submission(models.Model): 
    STATUS_CHOICES = (       
        ('AC', 'Успешно'),
        ('WA', 'Неправильный вывод'),        
        ('E', 'Ошибка'),
    )

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    code = models.TextField()
    status = models.CharField(max_length=3, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    student = models.CharField(null=True, max_length=150)
    prepod = models.CharField(null=True, max_length=150)

    def __str__(self):
        return f'{self.id} - {self.task.name} - {self.get_status_display()}'

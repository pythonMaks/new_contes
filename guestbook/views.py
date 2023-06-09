from django.shortcuts import render
from .models import Post
from .forms import MyForm

# Create your views here.
def home(request): 
    form = MyForm()   
    if request.method == 'POST':
        user = Post()
        user.name = request.POST['user_name']
        user.content = request.POST['user_text']               
        user.save()        
    context = {
    	'posts': reversed(Post.objects.all()),
        'form': form,
	}
    
    return render(request, 'guestbook/index.html', context)
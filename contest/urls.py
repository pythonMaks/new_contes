from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from interpreter import views as inpr_views
from guestbook import views as gb_views
from catalog import views as cat_views
from comments_list import views as prod_views


urlpatterns = [
    path('comments/', prod_views.ProductListView.as_view(), name='coments'),
    path('profile/', user_views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
	path('admin/', admin.site.urls),
	path('register/', user_views.register, name='register'),
    path('catalog/', cat_views.index, name='catalog'),
    path('submission_list/<str:student>', cat_views.submission_list, name='submission_list'),
    path('students_list/', cat_views.students_list, name='students_list'),
    path('showcookie/', cat_views.showcookie, name='showcookie'),   
    path('delete_cookie/', cat_views.delete_cookie, name='delcookie'),
    path('catalog/<int:pk>/', cat_views.MyDetailView.as_view(), name='mydetail'),
	path('', include('main.urls')),
    path('delete-task/<int:pk>/', user_views.delete_task, name='delete_task'),
    path('', include('core.urls')),
    path('interpreter/', inpr_views.index, name='interpreter'),
    path('guestbook/', gb_views.home, name='guestbook'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
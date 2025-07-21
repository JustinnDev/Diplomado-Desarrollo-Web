from django.urls import path 
from . import views

app_name = 'landing'

urlpatterns = [
    path('' , views.index , name='index'),
    path('material1/' , views.material1 , name='material1'),
    path('material2/' , views.material2 , name='material2'),    
]

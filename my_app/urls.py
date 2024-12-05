from django.urls import path

# from . import views

from .views import home ,purchase,checkout,handlerequest,tracker

urlpatterns = [
     path('',home,name='home' ),
     path('purchase/',purchase,name='purchase' ),
     path('checkout/',checkout,name='checkout' ),
     path('tracker/',tracker,name='trackstatus' ),
     path('handlerequest/',handlerequest,name='handlerequest' ),
  
]

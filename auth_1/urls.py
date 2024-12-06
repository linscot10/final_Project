
from django.urls import path
from auth_1 import views

urlpatterns = [
   path('signup/',views.signup ,name='signup'),
   path('login/',views.handlelogin ,name='handlelogin'),
   path('logout/',views.handlelogout ,name='handlelogout'),
   path('activate/<uidb64>/<token>',views.activateAccountView.as_view() ,name='activate'),
   path('request-reset-email/',views.ResetRequestEmailView.as_view() ,name='request-reset-email'),
   path('set-new-password/<uidb64>/<token>',views.SetNewPasswordView.as_view() ,name='set-new-password'),
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.edit_profile, name='profile_edit'),
    path('profile/delete/', views.delete_profile, name='profile_delete'),
]

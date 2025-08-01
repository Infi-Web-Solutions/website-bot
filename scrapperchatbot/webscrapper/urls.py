# In your app's urls.py file (e.g., webscrapper/urls.py)

from django.urls import path
from . import views

app_name = 'webscrapper'

urlpatterns = [
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home_view, name='home'), # The main dashboard
    path('add-bot/', views.add_bot_view, name='add_bot'), # URL for adding a bot
    path('bot/<int:bot_id>/upload-pdf/', views.upload_pdf_view, name='upload_pdf'), 
    path('bot/<int:bot_id>/chat/', views.bot_chat_view, name='bot_chat'), 
    path('bot/<int:bot_id>/add-url/', views.add_url_view, name='add_url'), 
]

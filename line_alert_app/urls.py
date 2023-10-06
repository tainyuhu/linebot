from django.urls import path
from . import views

urlpatterns = [
    path('open_line_oauth/', views.open_line_oauth, name='open_line_oauth'),
    path('callback/', views.callback, name='callback'),
    path('close/', views.close_page, name='close_page'),
    path('send_message/',views.send_message, name='send_message'),
    path('message_sent/', views.message_sent, name='message_sent'),
]
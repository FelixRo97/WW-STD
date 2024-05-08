from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('lobby', views.lobby, name='lobby'),
    path('removePlayer', views.removePlayer, name='removePlayer'),
    path('werwolfList', views.werwolfList, name='werwolfList'),
    path('game', views.game, name='game'),
]
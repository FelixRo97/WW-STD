from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('lobby', views.lobby, name='lobby'),
    path('removePlayer', views.removePlayer, name='removePlayer'),
    path('reopenLobby', views.reopenLobby, name='reopenLobby'),
    path('werwolfList', views.werwolfList, name='werwolfList'),
    path('addRoles', views.addRoles, name="addRoles"),
    path('gameWW', views.gameWW, name='gameWW'),
    path('gameSH', views.gameSH, name='gameSH'),
    path('requestRoleSH', views.requestRoleSH, name='requestRoleSH'),
]
# reservas/urls.py
from django.urls import path
from . import views

app_name = "reservas"

urlpatterns = [
    path('', views.home, name='home'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('elegir_fecha/', views.elegir_fecha, name='elegir_fecha'),
    path('turnos/<str:fecha>/', views.seleccionar_turno, name='seleccionar_turno'),
    path('confirmar/<str:fecha>/<int:cancha_id>/<str:hora_inicio>/<str:hora_fin>/', views.confirmar_turno, name='confirmar_turno'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
]

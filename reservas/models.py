# reservas/models.py - Versión incremental
from django.db import models
from django.contrib.auth.models import User

class Cancha(models.Model):
    nombre = models.CharField(max_length=100)
    activa = models.BooleanField(default=True)  # NUEVO: para poder desactivar canchas
    
    def __str__(self):
        return self.nombre

class HorarioBase(models.Model):
    """NUEVO: Horarios configurables por el admin en lugar de hardcodeados"""
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['orden', 'hora_inicio']
        unique_together = ['hora_inicio', 'hora_fin']
    
    def __str__(self):
        return f"{self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')}"

class Reserva(models.Model):
    # Campos existentes (sin cambios para no romper)
    cancha = models.ForeignKey(Cancha, on_delete=models.CASCADE)
    nombre_cliente = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)  # CAMBIADO: ahora opcional
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    # Campos nuevos opcionales
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # NUEVO
    email = models.EmailField(blank=True)  # NUEVO
    observaciones = models.TextField(blank=True)  # NUEVO
    creada_por_admin = models.BooleanField(default=False)  # NUEVO
    
    class Meta:
        unique_together = ['fecha', 'cancha', 'hora_inicio', 'hora_fin']
        ordering = ['fecha', 'hora_inicio']
    
    def __str__(self):
        return f"{self.cancha} | {self.fecha} {self.hora_inicio} - {self.hora_fin} | {self.nombre_cliente}"
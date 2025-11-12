# reservas/utils.py
from datetime import datetime, timedelta
from .models import HorarioBase, ConfiguracionDia, ConfiguracionSemana, Reserva, Cancha

def obtener_horarios_disponibles(fecha, cancha):
    """
    Obtiene los horarios disponibles para una fecha y cancha específica.
    Prioridad: ConfiguracionDia > ConfiguracionSemana > HorarioBase por defecto
    """
    # 1. Buscar configuración específica para ese día
    config_dia = ConfiguracionDia.objects.filter(fecha=fecha, cancha=cancha).first()
    
    if config_dia:
        if config_dia.cerrado:
            return []
        return config_dia.horarios_disponibles.filter(activo=True).order_by('orden', 'hora_inicio')
    
    # 2. Si no hay configuración específica, buscar configuración semanal
    dia_semana = fecha.weekday()
    config_semana = ConfiguracionSemana.objects.filter(dia_semana=dia_semana, cancha=cancha, activo=True).first()
    
    if config_semana:
        return config_semana.horarios_disponibles.filter(activo=True).order_by('orden', 'hora_inicio')
    
    # 3. Si no hay configuración semanal, usar todos los horarios activos por defecto
    return HorarioBase.objects.filter(activo=True).order_by('orden', 'hora_inicio')

def obtener_grilla_turnos(fecha):
    """Obtiene la grilla completa de turnos para todas las canchas en una fecha"""
    canchas = Cancha.objects.filter(activa=True)
    reservas = Reserva.objects.filter(fecha=fecha, estado='confirmada')
    grilla = []
    
    for cancha in canchas:
        horarios_disponibles = obtener_horarios_disponibles(fecha, cancha)
        turnos = []
        
        for horario in horarios_disponibles:
            ocupado = reservas.filter(
                cancha=cancha, 
                hora_inicio=horario.hora_inicio, 
                hora_fin=horario.hora_fin
            ).exists()
            
            turnos.append({
                'horario': horario,
                'inicio': horario.hora_inicio,
                'fin': horario})
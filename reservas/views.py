# reservas/views.py - Versión mejorada
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .forms import RegistroForm, FechaForm
from .models import Cancha, Reserva, HorarioBase
from datetime import datetime, timedelta, date
from django.conf import settings

# Página de inicio
def home(request):
    return render(request, 'reservas/home.html')

# Registro de usuario
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Especificar backend explícitamente
            from django.contrib.auth import login
            backend = settings.AUTHENTICATION_BACKENDS[0]
            login(request, user, backend=backend)
            return redirect('reservas:home')
    else:
        form = RegistroForm()
    return render(request, 'reservas/registro.html', {'form': form})

# Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('reservas:home')
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
    return render(request, 'reservas/login.html')

# Logout
def logout_view(request):
    logout(request)
    return redirect('reservas:home')

# Elegir fecha con calendario
@login_required
def elegir_fecha(request):
    if request.method == 'POST':
        form = FechaForm(request.POST)
        if form.is_valid():
            fecha = form.cleaned_data['fecha']
            return redirect('reservas:seleccionar_turno', fecha=fecha.strftime('%Y-%m-%d'))
    else:
        form = FechaForm()
    return render(request, 'reservas/elegir_fecha.html', {'form': form})

# Seleccionar turno para una fecha específica
@login_required
def seleccionar_turno(request, fecha):
    fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date()
    
    # Obtener horarios desde la base de datos en lugar de hardcodeados
    horarios_obj = HorarioBase.objects.filter(activo=True).order_by('orden', 'hora_inicio')
    horarios = [(h.hora_inicio.strftime('%H:%M'), h.hora_fin.strftime('%H:%M')) for h in horarios_obj]
    
    # Si no hay horarios en BD, usar los por defecto (compatibilidad)
    if not horarios:
        horarios = [
            ('12:00', '13:30'), ('13:30', '15:00'), ('15:00', '16:30'),
            ('16:30', '18:00'), ('18:00', '19:30'), ('19:30', '21:00'),
            ('21:00', '22:30'),
        ]
    
    canchas = Cancha.objects.filter(activa=True)
    reservas = Reserva.objects.filter(fecha=fecha_dt)
    grilla = []

    for cancha in canchas:
        turnos = []
        for inicio, fin in horarios:
            ocupado = reservas.filter(cancha=cancha, hora_inicio=inicio, hora_fin=fin).exists()
            turnos.append({
                'inicio': inicio,
                'fin': fin,
                'ocupado': ocupado
            })
        grilla.append({
            'cancha': cancha,
            'turnos': turnos
        })

    return render(request, 'reservas/seleccionar_turno.html', {
        'fecha': fecha,
        'grilla': grilla,
        'horarios': horarios
    })

# Confirmar turno seleccionado
@login_required
def confirmar_turno(request, fecha, cancha_id, hora_inicio, hora_fin):
    fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date()
    cancha = get_object_or_404(Cancha, id=cancha_id)

    # Verificar si el turno ya fue reservado
    if Reserva.objects.filter(fecha=fecha_dt, cancha=cancha, hora_inicio=hora_inicio).exists():
        messages.error(request, 'Este turno ya fue reservado.')
        return redirect('reservas:seleccionar_turno', fecha=fecha)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono', '')
        
        Reserva.objects.create(
            cancha=cancha,
            usuario=request.user,  # NUEVO: guardar el usuario
            nombre_cliente=nombre,
            telefono=telefono,
            fecha=fecha_dt,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            creada_por_admin=request.user.is_staff
        )
        messages.success(request, 'Turno reservado exitosamente!')
        return render(request, 'reservas/exito.html')

    return render(request, 'reservas/confirmar_turno.html', {
        'fecha': fecha,
        'cancha': cancha,
        'hora_inicio': hora_inicio,
        'hora_fin': hora_fin
    })

@login_required
def mis_reservas(request):
    reservas = Reserva.objects.filter(usuario=request.user).order_by('-fecha', '-hora_inicio')
    return render(request, 'reservas/mis_reservas.html', {
        'reservas': reservas,
        'today': date.today()
    })


# Dashboard para el admin
@staff_member_required
def dashboard(request):
    reservas = Reserva.objects.all().order_by('fecha', 'hora_inicio')
    return render(request, 'reservas/dashboard.html', {'reservas': reservas})

# NUEVAS VISTAS PARA ADMIN

@staff_member_required
def gestionar_horarios(request):
    """Nueva vista para que el admin gestione los horarios"""
    horarios = HorarioBase.objects.all().order_by('orden', 'hora_inicio')
    return render(request, 'reservas/gestionar_horarios.html', {'horarios': horarios})

@staff_member_required
def toggle_horario(request, horario_id):
    """Activar/desactivar un horario"""
    horario = get_object_or_404(HorarioBase, id=horario_id)
    horario.activo = not horario.activo
    horario.save()
    
    estado = "activado" if horario.activo else "desactivado"
    messages.success(request, f'Horario {horario} {estado}')
    return redirect('reservas:gestionar_horarios')

@staff_member_required
def gestionar_canchas(request):
    """Nueva vista para gestionar canchas"""
    canchas = Cancha.objects.all()
    return render(request, 'reservas/gestionar_canchas.html', {'canchas': canchas})

@staff_member_required
def toggle_cancha(request, cancha_id):
    """Activar/desactivar una cancha"""
    cancha = get_object_or_404(Cancha, id=cancha_id)
    cancha.activa = not cancha.activa
    cancha.save()
    
    estado = "activada" if cancha.activa else "desactivada"
    messages.success(request, f'Cancha {cancha.nombre} {estado}')
    return redirect('reservas:gestionar_canchas')
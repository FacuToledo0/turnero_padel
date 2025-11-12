# reservas/admin.py
from django.contrib import admin
from .models import Cancha, HorarioBase, Reserva

@admin.register(Cancha)
class CanchaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa')
    list_filter = ('activa',)
    list_editable = ('activa',)  # Permite editar desde la lista
    search_fields = ('nombre',)

@admin.register(HorarioBase)
class HorarioBaseAdmin(admin.ModelAdmin):
    list_display = ('hora_inicio', 'hora_fin', 'activo', 'orden')
    list_filter = ('activo',)
    list_editable = ('activo', 'orden')  # Permite editar desde la lista
    ordering = ('orden', 'hora_inicio')
    
    # Formulario personalizado
    fieldsets = (
        ('Horario', {
            'fields': ('hora_inicio', 'hora_fin')
        }),
        ('Configuración', {
            'fields': ('activo', 'orden'),
            'description': 'El orden determina cómo se muestran los horarios en la grilla'
        }),
    )

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'hora_inicio', 'hora_fin', 'cancha', 'nombre_cliente', 'usuario', 'creada_por_admin')
    list_filter = ('fecha', 'cancha', 'creada_por_admin')
    search_fields = ('nombre_cliente', 'usuario__username', 'telefono')
    date_hierarchy = 'fecha'
    ordering = ('-fecha', 'hora_inicio')
    
    # Campos de solo lectura para proteger datos importantes
    readonly_fields = ('usuario', 'creada_por_admin')
    
    fieldsets = (
        ('Información del Turno', {
            'fields': ('cancha', 'fecha', 'hora_inicio', 'hora_fin')
        }),
        ('Información del Cliente', {
            'fields': ('nombre_cliente', 'telefono', 'email', 'usuario')
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)  # Sección colapsable
        }),
        ('Información del Sistema', {
            'fields': ('creada_por_admin',),
            'classes': ('collapse',)
        }),
    )
    
    # Acciones personalizadas
    actions = ['marcar_como_admin']
    
    def marcar_como_admin(self, request, queryset):
        queryset.update(creada_por_admin=True)
        self.message_user(request, f"Se marcaron {queryset.count()} reservas como creadas por admin.")
    marcar_como_admin.short_description = "Marcar como creada por administrador"

# Configuración del admin site
admin.site.site_header = "Panel de Administración - Padel"
admin.site.site_title = "Admin Padel"
admin.site.index_title = "Gestión del Predio de Padel"
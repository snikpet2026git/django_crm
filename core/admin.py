from django.contrib import admin
from .models import (
    Position, Room, Employee, PrinterModel, Printer, PrinterMoveHistory,
    Cartridge, CartridgeRefillHistory, CartridgeMoveHistory
)


# =============================================================================
# АДМИНИСТРАЦИЯ ДЛЯ СПРАВОЧНИКОВ
# =============================================================================

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    """
    Админка для справочника должностей.
    Позволяет управлять списком должностей в организации.
    """
    list_display = ['name', 'description']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """
    Админка для справочника помещений.
    Позволяет управлять списком помещений, зданий и этажей.
    """
    list_display = ['name', 'building', 'floor', 'description']
    list_filter = ['building', 'floor']
    search_fields = ['name', 'building']
    ordering = ['building', 'name']


# =============================================================================
# АДМИНИСТРАЦИЯ ДЛЯ СОТРУДНИКОВ
# =============================================================================

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    Админка для сотрудников.
    Позволяет управлять списком сотрудников и назначать материально ответственных лиц.
    """
    list_display = ['full_name', 'position', 'phone', 'email', 'is_materially_responsible']
    list_filter = ['is_materially_responsible', 'position']
    search_fields = ['full_name', 'email', 'phone']
    ordering = ['full_name']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('full_name', 'position', 'user')
        }),
        ('Контактные данные', {
            'fields': ('phone', 'email')
        }),
        ('Статус ответственности', {
            'fields': ('is_materially_responsible',),
            'description': 'Отметьте, если сотрудник является материально ответственным лицом'
        }),
    )


# =============================================================================
# АДМИНИСТРАЦИЯ ДЛЯ МОДЕЛЕЙ ПРИНТЕРОВ
# =============================================================================

@admin.register(PrinterModel)
class PrinterModelAdmin(admin.ModelAdmin):
    """
    Админка для моделей принтеров.
    Содержит справочник производителей и моделей оборудования.
    """
    list_display = ['manufacturer', 'model_name', 'printer_type', 'cartridge_compatible']
    list_filter = ['manufacturer', 'printer_type']
    search_fields = ['manufacturer', 'model_name']
    ordering = ['manufacturer', 'model_name']


# =============================================================================
# АДМИНИСТРАЦИЯ ДЛЯ ПРИНТЕРОВ
# =============================================================================

class PrinterMoveHistoryInline(admin.TabularInline):
    """
    Встроенная админка для истории перемещений принтера.
    Отображается на странице конкретного принтера.
    """
    model = PrinterMoveHistory
    extra = 0
    readonly_fields = ['move_date', 'from_room', 'from_responsible', 'to_room', 'to_responsible', 'moved_by']
    can_delete = False
    verbose_name_plural = 'История перемещений'
    max_num = 10  # Показываем только последние 10 записей


@admin.register(Printer)
class PrinterAdmin(admin.ModelAdmin):
    """
    Основная админка для принтеров.
    Позволяет управлять всем парком печатающей техники:
    - Отслеживать местоположение
    - Назначать ответственных
    - Контролировать состояние
    - Просматривать историю перемещений
    """
    list_display = [
        'inventory_number', 
        'printer_model', 
        'status', 
        'current_room', 
        'responsible_employee',
        'updated_at'
    ]
    list_filter = ['status', 'printer_model__manufacturer', 'current_room__building']
    search_fields = ['inventory_number', 'serial_number', 'printer_model__model_name']
    ordering = ['inventory_number']
    inlines = [PrinterMoveHistoryInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('inventory_number', 'serial_number', 'printer_model')
        }),
        ('Состояние и расположение', {
            'fields': ('status', 'current_room', 'responsible_employee')
        }),
        ('Дополнительно', {
            'fields': ('purchase_date', 'warranty_end', 'notes'),
            'classes': ('collapse',)
        }),
    )


# =============================================================================
# АДМИНИСТРАЦИЯ ДЛЯ КАРТРИДЖЕЙ
# =============================================================================

class CartridgeRefillHistoryInline(admin.TabularInline):
    """
    Встроенная админка для истории заправок картриджа.
    """
    model = CartridgeRefillHistory
    extra = 0
    readonly_fields = ['refill_date', 'refill_count_after', 'performed_by']
    can_delete = False
    verbose_name_plural = 'История заправок'
    max_num = 15


class CartridgeMoveHistoryInline(admin.TabularInline):
    """
    Встроенная админка для истории перемещений картриджа.
    """
    model = CartridgeMoveHistory
    extra = 0
    readonly_fields = ['move_date', 'from_printer', 'from_storage', 'to_printer', 'to_storage', 'moved_by']
    can_delete = False
    verbose_name_plural = 'История перемещений'
    max_num = 10


@admin.register(Cartridge)
class CartridgeAdmin(admin.ModelAdmin):
    """
    Основная админка для картриджей.
    Позволяет управлять учетом картриджей:
    - Отслеживать состояние и количество заправок
    - Контролировать местоположение (в принтере или на складе)
    - Вести историю заправок и перемещений
    """
    list_display = [
        'inventory_number', 
        'model_name', 
        'color', 
        'status', 
        'refill_count',
        'current_printer',
        'storage_room',
        'last_refill_date'
    ]
    list_filter = ['status', 'color', 'current_printer', 'storage_room']
    search_fields = ['inventory_number', 'model_name']
    ordering = ['inventory_number']
    inlines = [CartridgeRefillHistoryInline, CartridgeMoveHistoryInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('inventory_number', 'model_name', 'color')
        }),
        ('Состояние', {
            'fields': ('status', 'refill_count', 'last_refill_date', 'first_use_date')
        }),
        ('Местоположение', {
            'fields': ('current_printer', 'storage_room'),
            'description': 'Укажите где находится картридж: в принтере или на складе'
        }),
        ('Примечания', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


# =============================================================================
# АДМИНИСТРАЦИЯ ДЛЯ ИСТОРИЙ (ОТДЕЛЬНЫЕ СТРАНИЦЫ)
# =============================================================================

@admin.register(PrinterMoveHistory)
class PrinterMoveHistoryAdmin(admin.ModelAdmin):
    """
    Админка для просмотра всей истории перемещений принтеров.
    """
    list_display = ['printer', 'move_date', 'from_room', 'to_room', 'from_responsible', 'to_responsible']
    list_filter = ['move_date', 'printer__printer_model__manufacturer']
    search_fields = ['printer__inventory_number']
    readonly_fields = ['printer', 'move_date', 'from_room', 'from_responsible', 'to_room', 'to_responsible', 'reason', 'moved_by']
    can_delete = False


@admin.register(CartridgeRefillHistory)
class CartridgeRefillHistoryAdmin(admin.ModelAdmin):
    """
    Админка для просмотра всей истории заправок картриджей.
    """
    list_display = ['cartridge', 'refill_date', 'refill_count_after', 'performed_by']
    list_filter = ['refill_date', 'cartridge__color']
    search_fields = ['cartridge__inventory_number']
    readonly_fields = ['cartridge', 'refill_date', 'refill_count_after', 'performed_by', 'notes']
    can_delete = False


@admin.register(CartridgeMoveHistory)
class CartridgeMoveHistoryAdmin(admin.ModelAdmin):
    """
    Админка для просмотра всей истории перемещений картриджей.
    """
    list_display = ['cartridge', 'move_date', 'from_printer', 'to_printer', 'from_storage', 'to_storage']
    list_filter = ['move_date', 'cartridge__color']
    search_fields = ['cartridge__inventory_number']
    readonly_fields = ['cartridge', 'move_date', 'from_printer', 'from_storage', 'to_printer', 'to_storage', 'reason', 'moved_by']
    can_delete = False


# =============================================================================
# КАСТОМИЗАЦИЯ ЗАГОЛОВКА АДМИНКИ
# =============================================================================

admin.site.site_header = "CRM система учета картриджей и принтеров"
admin.site.site_title = "CRM Картриджи"
admin.site.index_title = "Панель управления системой"

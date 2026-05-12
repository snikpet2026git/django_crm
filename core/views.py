from django.shortcuts import render
from .models import Printer, Cartridge, Employee, Room


def dashboard(request):
    """
    Главная панель управления системой.
    Отображает статистику и основные данные по всем сущностям.
    """
    # Получаем все принтеры
    printers = Printer.objects.select_related(
        'printer_model', 'current_room', 'responsible_employee'
    ).all()
    
    # Получаем все картриджи
    cartridges = Cartridge.objects.select_related(
        'current_printer', 'storage_room'
    ).all()
    
    # Получаем только материально ответственных сотрудников
    responsible_employees = Employee.objects.filter(
        is_materially_responsible=True
    ).select_related('position').prefetch_related('responsible_printers')
    
    # Получаем все помещения
    rooms = Room.objects.prefetch_related(
        'printers_current', 'stored_cartridges'
    ).all()
    
    context = {
        'printers': printers,
        'printers_count': printers.count(),
        'cartridges': cartridges,
        'cartridges_count': cartridges.count(),
        'employees_count': Employee.objects.count(),
        'responsible_employees': responsible_employees,
        'rooms': rooms,
        'rooms_count': rooms.count(),
    }
    
    return render(request, 'core/dashboard.html', context)

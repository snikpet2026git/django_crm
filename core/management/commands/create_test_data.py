from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Position, Room, Employee, PrinterModel, Printer, Cartridge, CartridgeRefillHistory

class Command(BaseCommand):
    help = "Заполняет базу данных 15 тестовыми записями для проверки работоспособности системы"

    def handle(self, *args, **options):
        self.stdout.write("Создание тестовых данных...")
        
        # Создаем суперпользователя для админки
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin123")
            self.stdout.write(self.style.SUCCESS("Создан суперпользователь: admin / admin123"))
        
        # Создаем должности (3 записи)
        positions_data = [
            {"name": "Системный администратор", "description": "Ответственный за IT инфраструктуру"},
            {"name": "Менеджер офиса", "description": "Управление офисным оборудованием"},
            {"name": "Бухгалтер", "description": "Финансовый учет"},
        ]
        positions = []
        for pos in positions_data:
            p, _ = Position.objects.get_or_create(name=pos["name"], defaults=pos)
            positions.append(p)
        
        # Создаем помещения (4 записи)
        rooms_data = [
            {"name": "Серверная", "building": "Корпус А", "floor": "1", "description": "Основная серверная комната"},
            {"name": "Офис менеджеров", "building": "Корпус А", "floor": "2", "description": "Отдел продаж"},
            {"name": "Бухгалтерия", "building": "Корпус Б", "floor": "1", "description": "Финансовый отдел"},
            {"name": "Склад оборудования", "building": "Корпус В", "floor": "1", "description": "Хранение принтеров и картриджей"},
        ]
        rooms = []
        for room in rooms_data:
            r, _ = Room.objects.get_or_create(name=room["name"], building=room["building"], defaults=room)
            rooms.append(r)
        
        # Создаем сотрудников (4 записи)
        employees_data = [
            {"full_name": "Иванов Иван Иванович", "position": positions[0], "phone": "+7-900-111-22-33", "email": "ivanov@company.ru", "is_materially_responsible": True},
            {"full_name": "Петрова Анна Сергеевна", "position": positions[1], "phone": "+7-900-222-33-44", "email": "petrova@company.ru", "is_materially_responsible": True},
            {"full_name": "Сидоров Петр Александрович", "position": positions[2], "phone": "+7-900-333-44-55", "email": "sidorov@company.ru", "is_materially_responsible": False},
            {"full_name": "Козлова Елена Дмитриевна", "position": positions[1], "phone": "+7-900-444-55-66", "email": "kozlova@company.ru", "is_materially_responsible": True},
        ]
        employees = []
        for emp in employees_data:
            e, _ = Employee.objects.get_or_create(full_name=emp["full_name"], defaults=emp)
            employees.append(e)
        
        # Создаем модели принтеров (3 записи)
        printer_models_data = [
            {"manufacturer": "HP", "model_name": "LaserJet Pro M404n", "printer_type": "laser", "cartridge_compatible": "HP 58A"},
            {"manufacturer": "Canon", "model_name": "i-SENSYS LBP623Cdw", "printer_type": "laser", "cartridge_compatible": "Canon 725"},
            {"manufacturer": "Kyocera", "model_name": "ECOSYS P2040dn", "printer_type": "laser", "cartridge_compatible": "TK-1170"},
        ]
        printer_models = []
        for model in printer_models_data:
            m, _ = PrinterModel.objects.get_or_create(manufacturer=model["manufacturer"], model_name=model["model_name"], defaults=model)
            printer_models.append(m)
        
        # Создаем принтеры (4 записи)
        printers_data = [
            {"inventory_number": "INV-001", "serial_number": "SN-HP-001", "printer_model": printer_models[0], "status": "active", "current_room": rooms[0], "responsible_employee": employees[0]},
            {"inventory_number": "INV-002", "serial_number": "SN-HP-002", "printer_model": printer_models[0], "status": "active", "current_room": rooms[1], "responsible_employee": employees[1]},
            {"inventory_number": "INV-003", "serial_number": "SN-CN-001", "printer_model": printer_models[1], "status": "active", "current_room": rooms[2], "responsible_employee": employees[2]},
            {"inventory_number": "INV-004", "serial_number": "SN-KY-001", "printer_model": printer_models[2], "status": "storage", "current_room": rooms[3], "responsible_employee": employees[3]},
        ]
        printers = []
        for printer in printers_data:
            p, _ = Printer.objects.get_or_create(inventory_number=printer["inventory_number"], defaults=printer)
            printers.append(p)
        
        # Создаем картриджи (4 записи)
        cartridges_data = [
            {"inventory_number": "CART-001", "model_name": "HP 58A", "color": "black", "status": "in_use", "refill_count": 2, "current_printer": printers[0]},
            {"inventory_number": "CART-002", "model_name": "HP 58A", "color": "black", "status": "ready", "refill_count": 1, "storage_room": rooms[3]},
            {"inventory_number": "CART-003", "model_name": "Canon 725", "color": "black", "status": "in_use", "refill_count": 3, "current_printer": printers[2]},
            {"inventory_number": "CART-004", "model_name": "TK-1170", "color": "black", "status": "empty", "refill_count": 0, "storage_room": rooms[3]},
        ]
        cartridges = []
        for cart in cartridges_data:
            c, _ = Cartridge.objects.get_or_create(inventory_number=cart["inventory_number"], defaults=cart)
            cartridges.append(c)
        
        total = len(positions) + len(rooms) + len(employees) + len(printer_models) + len(printers) + len(cartridges)
        
        self.stdout.write(self.style.SUCCESS(f"Успешно создано {total} тестовых записей:"))
        self.stdout.write(f"  - Должности: {len(positions)}")
        self.stdout.write(f"  - Помещения: {len(rooms)}")
        self.stdout.write(f"  - Сотрудники: {len(employees)}")
        self.stdout.write(f"  - Модели принтеров: {len(printer_models)}")
        self.stdout.write(f"  - Принтеры: {len(printers)}")
        self.stdout.write(f"  - Картриджи: {len(cartridges)}")
        self.stdout.write(self.style.WARNING("\nДля входа в админку используйте: admin / admin123"))

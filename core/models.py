from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


# =============================================================================
# СПРАВОЧНИКИ
# =============================================================================

class Position(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название должности")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название помещения")
    building = models.CharField(max_length=50, blank=True, null=True, verbose_name="Здание/Корпус")
    floor = models.CharField(max_length=10, blank=True, null=True, verbose_name="Этаж")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Помещение"
        verbose_name_plural = "Помещения"
        ordering = ["building", "name"]

    def __str__(self):
        location = f"{self.building} " if self.building else ""
        location += f"{self.name}"
        if self.floor:
            location += f" (эт.{self.floor})"
        return location


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь системы")
    full_name = models.CharField(max_length=200, verbose_name="ФИО полностью")
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Должность")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    is_materially_responsible = models.BooleanField(default=False, verbose_name="Материально ответственное лицо")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ["full_name"]

    def __str__(self):
        responsibility = " (МОЛ)" if self.is_materially_responsible else ""
        return f"{self.full_name}{responsibility}"


class PrinterModel(models.Model):
    manufacturer = models.CharField(max_length=100, verbose_name="Производитель")
    model_name = models.CharField(max_length=100, verbose_name="Модель")
    printer_type = models.CharField(max_length=50, choices=[("laser", "Лазерный"), ("inkjet", "Струйный"), ("matrix", "Матричный"), ("mfd", "МФУ")], default="laser", verbose_name="Тип принтера")
    cartridge_compatible = models.CharField(max_length=100, blank=True, null=True, verbose_name="Совместимый картридж")

    class Meta:
        verbose_name = "Модель принтера"
        verbose_name_plural = "Модели принтеров"
        ordering = ["manufacturer", "model_name"]
        unique_together = ["manufacturer", "model_name"]

    def __str__(self):
        return f"{self.manufacturer} {self.model_name}"


class Printer(models.Model):
    STATUS_CHOICES = [("active", "В эксплуатации"), ("repair", "В ремонте"), ("storage", "На складе"), ("writeoff", "Списан")]
    inventory_number = models.CharField(max_length=50, unique=True, verbose_name="Инвентарный номер")
    serial_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Серийный номер")
    printer_model = models.ForeignKey(PrinterModel, on_delete=models.PROTECT, verbose_name="Модель принтера")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active", verbose_name="Состояние")
    current_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Текущее помещение", related_name="printers_current")
    responsible_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ответственный сотрудник", related_name="responsible_printers")
    purchase_date = models.DateField(null=True, blank=True, verbose_name="Дата покупки")
    warranty_end = models.DateField(null=True, blank=True, verbose_name="Окончание гарантии")
    notes = models.TextField(blank=True, null=True, verbose_name="Примечания")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата внесения в базу")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")

    class Meta:
        verbose_name = "Принтер"
        verbose_name_plural = "Принтеры"
        ordering = ["inventory_number"]

    def __str__(self):
        return f"{self.printer_model} (инв. {self.inventory_number})"


class PrinterMoveHistory(models.Model):
    printer = models.ForeignKey(Printer, on_delete=models.CASCADE, verbose_name="Принтер", related_name="move_history")
    move_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата перемещения")
    from_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Из помещения", related_name="printer_moves_from")
    from_responsible = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="От ответственного", related_name="printer_moves_from_emp")
    to_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="В помещение", related_name="printer_moves_to")
    to_responsible = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="К ответственному", related_name="printer_moves_to_emp")
    reason = models.TextField(blank=True, null=True, verbose_name="Причина перемещения")
    moved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Кем выполнено перемещение")

    class Meta:
        verbose_name = "История перемещения принтера"
        verbose_name_plural = "Истории перемещений принтеров"
        ordering = ["-move_date"]

    def __str__(self):
        return f"Перемещение {self.printer.inventory_number} от {self.move_date.strftime('%d.%m.%Y')}"


class Cartridge(models.Model):
    STATUS_CHOICES = [("new", "Новый"), ("in_use", "В эксплуатации"), ("empty", "Пустой"), ("refilling", "На заправке"), ("ready", "Готов к установке"), ("repair", "В ремонте"), ("writeoff", "Списан")]
    inventory_number = models.CharField(max_length=50, unique=True, verbose_name="Инвентарный номер")
    model_name = models.CharField(max_length=100, verbose_name="Модель картриджа")
    color = models.CharField(max_length=20, choices=[("black", "Черный"), ("cyan", "Голубой"), ("magenta", "Пурпурный"), ("yellow", "Желтый"), ("other", "Другой")], default="black", verbose_name="Цвет")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new", verbose_name="Состояние")
    refill_count = models.IntegerField(default=0, verbose_name="Количество заправок")
    last_refill_date = models.DateField(null=True, blank=True, verbose_name="Дата последней заправки")
    first_use_date = models.DateField(null=True, blank=True, verbose_name="Дата первого использования")
    current_printer = models.ForeignKey(Printer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Установлен в принтер", related_name="installed_cartridges")
    storage_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Место хранения", related_name="stored_cartridges")
    notes = models.TextField(blank=True, null=True, verbose_name="Примечания")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата внесения в базу")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")

    class Meta:
        verbose_name = "Картридж"
        verbose_name_plural = "Картриджи"
        ordering = ["inventory_number"]

    def __str__(self):
        status_ru = dict(self.STATUS_CHOICES).get(self.status, self.status)
        return f"{self.model_name} ({self.inventory_number}) - {status_ru}"


class CartridgeRefillHistory(models.Model):
    cartridge = models.ForeignKey(Cartridge, on_delete=models.CASCADE, verbose_name="Картридж", related_name="refill_history")
    refill_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата заправки")
    refill_count_after = models.IntegerField(verbose_name="Количество заправок после этой")
    performed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Кто выполнял заправку", related_name="performed_refills")
    notes = models.TextField(blank=True, null=True, verbose_name="Примечания")

    class Meta:
        verbose_name = "История заправки картриджа"
        verbose_name_plural = "Истории заправок картриджей"
        ordering = ["-refill_date"]

    def __str__(self):
        return f"Заправка {self.cartridge.inventory_number} от {self.refill_date.strftime('%d.%m.%Y')} (#N{self.refill_count_after})"


class CartridgeMoveHistory(models.Model):
    cartridge = models.ForeignKey(Cartridge, on_delete=models.CASCADE, verbose_name="Картридж", related_name="move_history")
    move_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата перемещения")
    from_printer = models.ForeignKey(Printer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Из принтера", related_name="cartridge_moves_from")
    from_storage = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Со склада", related_name="cartridge_moves_from_room")
    to_printer = models.ForeignKey(Printer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="В принтер", related_name="cartridge_moves_to")
    to_storage = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="На склад", related_name="cartridge_moves_to_room")
    reason = models.TextField(blank=True, null=True, verbose_name="Причина перемещения")
    moved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Кем выполнено")

    class Meta:
        verbose_name = "История перемещения картриджа"
        verbose_name_plural = "Истории перемещений картриджей"
        ordering = ["-move_date"]

    def __str__(self):
        return f"Перемещение картриджа {self.cartridge.inventory_number} от {self.move_date.strftime('%d.%m.%Y')}"

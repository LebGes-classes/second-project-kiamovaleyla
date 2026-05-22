import datetime

class BaseEntity:
    _id_counter = 1

    def __init__(self, name):
        self._name = name
        self._id = BaseEntity._id_counter
        BaseEntity._id_counter += 1
        self._is_active = True

    @property
    def id(self): return self._id
    @property
    def name(self): return self._name

    @name.setter
    def name(self, value):
        if not value or not value.strip():
            print("⚠️ Имя не может быть пустым!")
        else:
            self._name = value.strip()

    def activate(self): self._is_active = True
    def deactivate(self): self._is_active = False

    def get_info(self):
        return f"[ID: {self.id}] {self._name} | Статус: {'Активен' if self._is_active else 'Неактивен'}"

    def to_dict(self):
        return {"id": self.id, "name": self.name, "is_active": self._is_active}


class Person(BaseEntity):
    def __init__(self, name, phone=""):
        super().__init__(name)
        self._phone = phone
    @property
    def phone(self): return self._phone


class Employee(Person):
    def __init__(self, name, phone, position, salary):
        super().__init__(name, phone)
        self._position = position
        self._salary = salary
        self._assigned_location_id = ""

    def get_info(self):
        base = super().get_info()
        return f"{base} | Должность: {self._position} | Зарплата: {self._salary}₽ | Локация: {self._assigned_location_id}"

    def to_dict(self):
        d = super().to_dict()
        d.update({"type": "employee", "phone": self.phone, "position": self._position,
                  "salary": self._salary, "assigned_location_id": self._assigned_location_id})
        return d


class Customer(Person):
    def __init__(self, name, phone=""):
        super().__init__(name, phone)
        self._total_spent = 0.0
        self._loyalty_points = 0.0

    def add_purchase(self, amount):
        self._total_spent += amount
        self._loyalty_points += amount * 0.01

    def get_discount(self):
        return min(10.0, self._loyalty_points)

    def get_info(self):
        base = super().get_info()
        return f"{base} | Потрачено: {self._total_spent}₽ | Баллы: {self._loyalty_points}"

    def to_dict(self):
        d = super().to_dict()
        d.update({"type": "customer", "phone": self.phone, "total_spent": self._total_spent,
                  "loyalty_points": self._loyalty_points})
        return d


class Location(BaseEntity):
    def __init__(self, name, address=""):
        super().__init__(name)
        self._address = address
        self._manager_id = ""

    def open_loc(self):
        self.activate()
        print(f" '{self.name}' открыт.")

    def close_loc(self):
        self.deactivate()
        print(f" '{self.name}' закрыт.")

    def get_info(self):
        base = super().get_info()
        return f"{base} | Адрес: {self._address} | Открыт: {'Да' if self._is_active else 'Нет'}"


class WarehouseCell(BaseEntity):
    def __init__(self, label, max_capacity, warehouse_id):
        super().__init__(label)
        self._max_capacity = max_capacity
        self._warehouse_id = warehouse_id
        self._contents = {}
        self._responsible_employee_id = ""

    def current_load(self): return sum(self._contents.values())

    def add_product(self, prod_id, qty):
        if qty <= 0: return False
        if self.current_load() + qty > self._max_capacity:
            print(" Ячейка переполнена!")
            return False
        self._contents[prod_id] = self._contents.get(prod_id, 0) + qty
        return True

    def remove_product(self, prod_id, qty):
        if qty <= 0: return False
        if self._contents.get(prod_id, 0) < qty:
            print(" Товара в ячейке недостаточно!")
            return False
        self._contents[prod_id] -= qty
        if self._contents[prod_id] == 0:
            del self._contents[prod_id]
        return True

    def change_responsible(self, emp_id):
        self._responsible_employee_id = emp_id
        print(" Ответственный ячейки изменён.")

    def get_info(self):
        return f" Ячейка: {self.name} | Загрузка: {self.current_load()}/{self._max_capacity} | Ответственный: {self._responsible_employee_id}"


class Warehouse(Location):
    def __init__(self, name, address=""):
        super().__init__(name, address)
        self._cells = []

    def add_cell(self, label, capacity):
        cell = WarehouseCell(label, capacity, self.id)
        self._cells.append(cell)
        print(f" Ячейка '{label}' создана. ID: {cell.id}")
        return cell

    def get_cell_by_id(self, cell_id):
        for c in self._cells:
            if str(c.id) == str(cell_id): return c
        return None

    def get_inventory(self):
        total = {}
        for c in self._cells:
            for pid, qty in c._contents.items():
                total[pid] = total.get(pid, 0) + qty
        return total

    def to_dict(self):
        d = super().to_dict()
        d.update({"type": "warehouse", "cells": [c.to_dict() for c in self._cells]})
        return d


class SalesPoint(Location):
    def __init__(self, name, address=""):
        super().__init__(name, address)
        self._inventory = {}
        self._total_revenue = 0.0

    def add_stock(self, prod_id, qty): self._inventory[prod_id] = self._inventory.get(prod_id, 0) + qty

    def remove_stock(self, prod_id, qty):
        if self._inventory.get(prod_id, 0) < qty:
            print(" Товара в пункте продаж нет!")
            return False
        self._inventory[prod_id] -= qty
        if self._inventory[prod_id] == 0: del self._inventory[prod_id]
        return True

    def record_revenue(self, amount): self._total_revenue += amount
    def get_inventory(self): return self._inventory.copy()

    def get_profit(self, products_dict):
        profit = 0.0
        for pid, qty in self._inventory.items():
            if pid in products_dict:
                p = products_dict[pid]
                profit += (p.sell_price - p.cost_price) * qty
        return profit

    def to_dict(self):
        d = super().to_dict()
        d.update({"type": "sales_point", "inventory": self._inventory, "total_revenue": self._total_revenue})
        return d


class Product(BaseEntity):
    def __init__(self, name, category, cost_price, sell_price):
        super().__init__(name)
        self._category = category
        self.cost_price = cost_price
        self.sell_price = sell_price

    def get_margin(self): return self.sell_price - self.cost_price

    def get_info(self):
        base = super().get_info()
        return f"{base} | Категория: {self._category} | Закупка: {self.cost_price}₽ | Продажа: {self.sell_price}₽"

    def to_dict(self):
        d = super().to_dict()
        d.update({"type": "product", "category": self._category, "cost_price": self.cost_price,
                  "sell_price": self.sell_price})
        return d


class Order:
    def __init__(self, customer_id, items, total):
        self.id = f"ORD_{datetime.datetime.now().strftime('%H%M%S')}"
        self.customer_id = customer_id
        self.items = items
        self.total = total
        self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.status = "Выполнен"

    def get_info(self):
        return f" Заказ {self.id} | Сумма: {self.total}₽ | Дата: {self.date}"
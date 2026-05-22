import json
import os
from models import Product, Employee, Customer, Warehouse, SalesPoint
from transactions import SaleTransaction, PurchaseTransaction, ReturnTransaction


class CRMSystem:
    """CRM-система для управления складом, продажами и финансами."""

    def __init__(self):
        """Инициализирует систему, создаёт пустые хранилища и загружает данные."""
        self.products = {}
        self.employees = {}
        self.customers = {}
        self.warehouses = {}
        self.sales_points = {}
        self.transactions = []
        self.orders = []
        self.balance = 10000.0
        self.load_data()

    def save_data(self):
        """Сохраняет текущее состояние системы (баланс, товары, сотрудников и др.) в файл crm_data.json."""
        data = {
            "balance": self.balance,
            "products": {str(k): v.to_dict() for k, v in self.products.items()},
            "employees": {str(k): v.to_dict() for k, v in self.employees.items()},
            "customers": {str(k): v.to_dict() for k, v in self.customers.items()},
            "warehouses": {str(k): v.to_dict() for k, v in self.warehouses.items()},
            "sales_points": {str(k): v.to_dict() for k, v in self.sales_points.items()},
            "orders": [o.__dict__ for o in self.orders]
        }
        with open("crm_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(" Данные сохранены в файл.")

    def load_data(self):
        """Загружает данные из файла crm_data.json. Если файла нет, запускает новую систему."""
        if not os.path.exists("crm_data.json"):
            print(" Файл данных не найден. Запускаем новую систему.")
            return
        try:
            with open("crm_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            self.balance = data.get("balance", 0.0)
            for pid, pd in data.get("products", {}).items():
                p = Product(pd["name"], pd["category"], pd["cost_price"], pd["sell_price"])
                p._id = int(pid)
                self.products[p.id] = p
            # Примечание: загрузка остальных сущностей опущена для краткости, как в оригинале.
            print(" Данные успешно загружены.")
        except Exception as e:
            print(f"Ошибка загрузки: {e}")

    def hire_employee(self, name, phone, pos, salary):
        """
        Нанимает нового сотрудника.

        Args:
            name (str): Имя сотрудника.
            phone (str): Телефон.
            pos (str): Должность.
            salary (float): Зарплата.
        """
        e = Employee(name, phone, pos, salary)
        self.employees[e.id] = e
        print(f" Сотрудник нанят. ID: {e.id}")

    def fire_employee(self, emp_id):
        """
        Увольняет сотрудника (деактивирует).

        Args:
            emp_id (int): ID сотрудника.
        """
        if emp_id in self.employees:
            self.employees[emp_id].deactivate()
            print(" Сотрудник уволен (деактивирован).")
        else:
            print(" Сотрудник не найден.")

    def add_customer(self, name, phone):
        """
        Добавляет нового клиента.

        Args:
            name (str): Имя клиента.
            phone (str): Телефон.
        """
        c = Customer(name, phone)
        self.customers[c.id] = c
        print(f" Клиент добавлен. ID: {c.id}")

    def add_product(self, name, cat, cost, sell):
        """
        Добавляет новый товар.

        Args:
            name (str): Название товара.
            cat (str): Категория.
            cost (float): Закупочная цена.
            sell (float): Продажная цена.

        Raises:
            Prints сообщение об ошибке, если цена <= 0.
        """
        if cost <= 0 or sell <= 0:
            print(" Цены должны быть больше 0!")
            return
        p = Product(name, cat, cost, sell)
        self.products[p.id] = p
        print(f" Товар добавлен. ID: {p.id}")

    def open_warehouse(self, name, addr):
        """
        Открывает новый склад.

        Args:
            name (str): Название склада.
            addr (str): Адрес.
        """
        w = Warehouse(name, addr)
        self.warehouses[w.id] = w
        w.open_loc()

    def add_sales_point(self, name, addr):
        """
        Добавляет новую торговую точку.

        Args:
            name (str): Название точки.
            addr (str): Адрес.
        """
        sp = SalesPoint(name, addr)
        self.sales_points[sp.id] = sp
        sp.open_loc()

    def close_location(self, loc_id, is_warehouse=True):
        """
        Закрывает локацию (склад или точку продаж).

        Args:
            loc_id (int): ID локации.
            is_warehouse (bool): True, если это склад, False — если торговая точка.
        """
        target = self.warehouses if is_warehouse else self.sales_points
        if loc_id in target:
            target[loc_id].close_loc()
        else:
            print(" Локация не найдена.")

    def add_cell(self, wh_id, label, cap):
        """
        Добавляет ячейку на склад.

        Args:
            wh_id (int): ID склада.
            label (str): Метка ячейки.
            cap (int): Вместимость ячейки.
        """
        if wh_id in self.warehouses:
            self.warehouses[wh_id].add_cell(label, cap)

    def move_product(self, wh_id, from_cell_id, to_cell_id, prod_id, qty):
        """
        Перемещает товар между ячейками одного склада.

        Args:
            wh_id (int): ID склада.
            from_cell_id (int): ID исходной ячейки.
            to_cell_id (int): ID целевой ячейки.
            prod_id (int): ID товара.
            qty (int): Количество.
        """
        if wh_id not in self.warehouses:
            print(" Склад не найден.")
            return

        wh = self.warehouses[wh_id]
        c1, c2 = wh.get_cell_by_id(from_cell_id), wh.get_cell_by_id(to_cell_id)

        if not c1 or not c2:
            print(" Ячейки не найдены.")
            return

        if c1.remove_product(prod_id, qty):
            c2.add_product(prod_id, qty)
            print(" Товар перемещён.")

    def change_responsible(self, cell_id, emp_id):
        """
        Меняет ответственного за ячейку.

        Args:
            cell_id (int): ID ячейки.
            emp_id (int): ID нового ответственного сотрудника.
        """

        for wh in self.warehouses.values():
            c = wh.get_cell_by_id(cell_id)
            if c:
                c.change_responsible(emp_id)
                return

        print(" Ячейка не найдена.")

    def procure(self, wh_id, items):
        """
        Осуществляет закупку товаров на склад.

        Args:
            wh_id (int): ID склада.
            items (list): Список позиций закупки.
        """
        PurchaseTransaction(wh_id, "", items).execute(self)

    def sell(self, sp_id, emp_id, cust_id, items):
        """
        Осуществляет продажу товаров в торговой точке.

        Args:
            sp_id (int): ID торговой точки.
            emp_id (int): ID сотрудника, оформившего продажу.
            cust_id (int): ID клиента.
            items (list): Список проданных позиций.
        """
        SaleTransaction(sp_id, emp_id, cust_id, items).execute(self)

    def return_items(self, sp_id, items):
        """
        Оформляет возврат товаров в торговой точке.

        Args:
            sp_id (int): ID торговой точки.
            items (list): Список возвращаемых позиций.
        """
        ReturnTransaction(sp_id, "", items).execute(self)

    def get_enterprise_profit(self):
        """
        Рассчитывает общую прибыль предприятия (деньги + стоимость остатков).

        Returns:
            float: Прибыль предприятия.
        """
        stock_profit = sum(sp.get_profit(self.products) for sp in self.sales_points.values())
        return self.balance + stock_profit

    def get_sales_point_profit(self, sp_id):
        """
        Возвращает прибыль конкретной торговой точки.

        Args:
            sp_id (int): ID торговой точки.

        Returns:
            float: Прибыль точки продаж, либо 0.0, если точка не найдена.
        """
        sp = self.sales_points.get(sp_id)

        if sp:
            return sp.get_profit(self.products)

        else:
            return 0.0

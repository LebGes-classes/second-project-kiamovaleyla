import datetime
from models import BaseEntity, Order


class Transaction(BaseEntity):
    """Базовый класс для всех транзакций в системе."""

    def __init__(self, t_type, location_id, employee_id, items):
        """
        Инициализирует базовую транзакцию.

        Args:
            t_type (str): Тип транзакции (sale, purchase, return).
            location_id (int): ID локации (склада или точки продаж).
            employee_id (int): ID сотрудника, выполнившего транзакцию.
            items (list): Список товаров в транзакции.
        """
        super().__init__(t_type)
        self.location_id = location_id
        self.employee_id = employee_id
        self.items = items
        self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.status = "pending"

    def execute(self, manager):
        """
        Выполняет транзакцию. Должен быть переопределён в дочерних классах.

        Args:
            manager: Менеджер CRM-системы.
        """
        pass


class SaleTransaction(Transaction):
    """Транзакция продажи товаров в торговой точке."""

    def __init__(self, location_id, emp_id, cust_id, items):
        """
        Инициализирует транзакцию продажи.

        Args:
            location_id (int): ID торговой точки.
            emp_id (int): ID сотрудника.
            cust_id (int): ID клиента.
            items (list): Список продаваемых товаров.
        """
        super().__init__("sale", location_id, emp_id, items)
        self.customer_id = cust_id

    def execute(self, manager):
        """
        Выполняет продажу: списывает товары со склада, начисляет выручку и обновляет баланс.

        Args:
            manager: Менеджер CRM-системы.
        """
        sp = manager.sales_points.get(int(self.location_id))
        if not sp or not sp._is_active:
            print(" Пункт продаж не найден или закрыт!")
            return

        total = 0
        for it in self.items:
            if not sp.remove_stock(it["prod_id"], it["qty"]):
                return
            total += it["qty"] * it["price"]

        sp.record_revenue(total)
        manager.balance += total

        if self.customer_id in manager.customers:
            manager.customers[self.customer_id].add_purchase(total)

        self.status = "completed"
        manager.transactions.append(self)

        order = Order(self.customer_id, self.items, total)
        manager.orders.append(order)

        print(f" Продажа выполнена. Сумма: {total}₽. Заказ: {order.id}")


class PurchaseTransaction(Transaction):
    """Транзакция закупки товаров на склад."""

    def execute(self, manager):
        """
        Выполняет закупку: добавляет товары на склад и списывает средства с баланса.

        Args:
            manager: Менеджер CRM-системы.
        """
        wh = manager.warehouses.get(int(self.location_id))
        if not wh or not wh._is_active:
            print(" Склад не найден или закрыт!")
            return

        if not wh._cells:
            print(" На складе нет ячеек!")
            return

        target_cell = wh._cells[0]
        cost = 0

        for it in self.items:
            if not target_cell.add_product(it["prod_id"], it["qty"]):
                return
            cost += it["qty"] * it["cost_price"]

        manager.balance -= cost
        self.status = "completed"
        manager.transactions.append(self)

        print(f" Закупка выполнена. Затрачено: {cost}₽")


class ReturnTransaction(Transaction):
    """Транзакция возврата товаров от клиента."""

    def execute(self, manager):
        """
        Выполняет возврат: добавляет товары обратно на склад и возвращает деньги клиенту.

        Args:
            manager: Менеджер CRM-системы.
        """
        sp = manager.sales_points.get(int(self.location_id))
        if not sp or not sp._is_active:
            print(" Пункт продаж не найден или закрыт!")
            return

        refund = 0

        for it in self.items:
            sp.add_stock(it["prod_id"], it["qty"])
            refund += it["qty"] * it["price"]

        manager.balance -= refund
        sp.record_revenue(-refund)
        self.status = "completed"
        manager.transactions.append(self)

        print(f" Возврат выполнен. Возвращено: {refund}₽")
from crm import CRMSystem


def run_ui():
    """
    Запускает интерактивный пользовательский интерфейс CRM-системы.

    Функция создаёт экземпляр CRM-системы и предоставляет консольное меню
    для управления всеми аспектами системы: персонал, клиенты, склады,
    точки продаж, товары, закупки и отчёты.
    """
    crm = CRMSystem()

    while True:
        print("\n" + "=" * 40)
        print(" CRM СИСТЕМА ПРЕДПРИЯТИЯ")
        print(f" Баланс: {crm.balance}₽")
        print("1. Персонал (Найм/Увольнение/Инфо)")
        print("2. Клиенты (Добавить/Инфо)")
        print("3. Склады (Открыть/Закрыть/Ячейки/Перемещение)")
        print("4. Точки продаж (Открыть/Закрыть/Продажа/Возврат/Инфо)")
        print("5. Товары и Закупки")
        print("6. Отчёты (Доходность)")
        print("7. Сохранить и Выйти")

        try:
            choice = int(input("Введите номер: "))
        except ValueError:
            print(" Нужно число!")
            continue

        if choice == 1:
            print("\n1. Найм  2. Увольнение  3. Список")
            c = input("Действие: ")

            if c == "1":
                name = input("Имя: ")
                phone = input("Телефон: ")
                position = input("Должность: ")
                salary = float(input("Зарплата: "))
                crm.hire_employee(name, phone, position, salary)

            elif c == "2":
                emp_id = int(input("ID сотрудника: "))
                crm.fire_employee(emp_id)

            elif c == "3":
                for e in crm.employees.values():
                    print(e.get_info())

        elif choice == 2:
            name = input("Имя клиента: ")
            phone = input("Телефон: ")
            crm.add_customer(name, phone)

        elif choice == 3:
            print("\n1. Открыть склад  2. Закрыть  3. Добавить ячейку  4. Переместить товар")
            c = input("Действие: ")

            if c == "1":
                name = input("Название: ")
                address = input("Адрес: ")
                crm.open_warehouse(name, address)

            elif c == "2":
                loc_id = int(input("ID склада: "))
                crm.close_location(loc_id, is_warehouse=True)

            elif c == "3":
                wh_id = int(input("ID склада: "))
                label = input("Метка: ")
                capacity = int(input("Вместимость: "))
                crm.add_cell(wh_id, label, capacity)

            elif c == "4":
                wh_id = int(input("ID склада: "))
                from_cell = input("Из ячейки ID: ")
                to_cell = input("В ячейку ID: ")
                prod_id = int(input("ID товара: "))
                quantity = int(input("Кол-во: "))
                crm.move_product(wh_id, from_cell, to_cell, prod_id, quantity)

        elif choice == 4:
            print("\n1. Открыть точку  2. Закрыть  3. Продать  4. Вернуть  5. Инфо")
            c = input("Действие: ")

            if c == "1":
                name = input("Название: ")
                address = input("Адрес: ")
                crm.add_sales_point(name, address)

            elif c == "2":
                loc_id = int(input("ID точки: "))
                crm.close_location(loc_id, is_warehouse=False)

            elif c == "3":
                sp_id = int(input("ID точки: "))
                cust_id = int(input("ID клиента: "))
                emp_id = input("ID сотрудника: ")

                items = []
                print("Вводите товары (ID Кол-во Цена), пустая строка для завершения:")

                while True:
                    line = input("> ").strip()
                    if not line:
                        break

                    parts = line.split()
                    if len(parts) != 3:
                        print(" Ошибка: нужно ввести 3 значения (ID Кол-во Цена)")
                        continue

                    pid, qty, price = parts
                    items.append({
                        "prod_id": int(pid),
                        "qty": int(qty),
                        "price": float(price)
                    })

                crm.sell(sp_id, emp_id, cust_id, items)

            elif c == "4":
                sp_id = int(input("ID точки: "))

                items = []
                print("Возврат товаров (ID Кол-во Цена), пустая строка для выхода:")

                while True:
                    line = input("> ").strip()
                    if not line:
                        break

                    parts = line.split()
                    if len(parts) != 3:
                        print(" Ошибка: нужно ввести 3 значения (ID Кол-во Цена)")
                        continue

                    pid, qty, price = parts
                    items.append({
                        "prod_id": int(pid),
                        "qty": int(qty),
                        "price": float(price)
                    })

                crm.return_items(sp_id, items)

            elif c == "5":
                sp_id = int(input("ID точки: "))
                sp = crm.sales_points.get(sp_id)

                if sp:
                    print(sp.get_info())
                    print("\nОстатки:", sp.get_inventory())

        elif choice == 5:
            print("\n1. Добавить товар  2. Закупка")
            c = input("Действие: ")

            if c == "1":
                name = input("Название: ")
                category = input("Категория: ")
                cost_price = float(input("Закупка: "))
                sell_price = float(input("Продажа: "))
                crm.add_product(name, category, cost_price, sell_price)

            elif c == "2":
                wh_id = int(input("ID склада: "))

                items = []
                print("Товары на закупку (ID Кол-во ЗакупЦена), пустая строка для выхода:")

                while True:
                    line = input("> ").strip()
                    if not line:
                        break

                    parts = line.split()
                    if len(parts) != 3:
                        print(" Ошибка: нужно ввести 3 значения (ID Кол-во ЗакупЦена)")
                        continue

                    pid, qty, price = parts
                    items.append({
                        "prod_id": int(pid),
                        "qty": int(qty),
                        "cost_price": float(price)
                    })

                crm.procure(wh_id, items)

        elif choice == 6:
            print("\n1. Доходность всего предприятия")
            print("2. Доходность точки продаж")
            c = input("Действие: ")

            if c == "1":
                profit = crm.get_enterprise_profit()
                print(f" Общая доходность: {profit}₽")

            elif c == "2":
                sp_id = int(input("ID точки: "))
                profit = crm.get_sales_point_profit(sp_id)
                print(f" Доходность точки: {profit}₽")

        elif choice == 7:
            crm.save_data()
            print(" Пока!")
            break


if __name__ == "__main__":
    """Точка входа в программу."""
    run_ui()
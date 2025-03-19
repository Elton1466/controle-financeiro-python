class FinanceManager:
    def __init__(self):
        self.transactions = []

    def add_transaction(self, description, amount, transaction_type):
        if transaction_type not in ["receita", "despesa"]:
            print("Tipo de transação inválido. Use 'receita' ou 'despesa'.")
            return

        self.transactions.append({
            "description": description,
            "amount": amount,
            "type": transaction_type
        })
        print("Transação adicionada com sucesso!")

    def view_transactions(self):
        if not self.transactions:
            print("Nenhuma transação registrada.")
            return

        print("\nTransações:")
        for transaction in self.transactions:
            print(f"{transaction['description']}: {transaction['amount']} ({transaction['type']})")

    def calculate_balance(self):
        total_income = sum(t["amount"] for t in self.transactions if t["type"] == "receita")
        total_expenses = sum(t["amount"] for t in self.transactions if t["type"] == "despesa")
        balance = total_income - total_expenses
        print(f"\nSaldo atual: {balance}")

    def view_transactions_by_category(self, category):
        filtered_transactions = [t for t in self.transactions if t["category"] == category]
        if not filtered_transactions:
            print(f"Nenhuma transação na categoria '{category}'.")
            return

        print(f"\nTransações na categoria '{category}':")
        for transaction in filtered_transactions:
            print(f"{transaction['date']}: {transaction['description']}: {transaction['amount']} ({transaction['type']})")

    def view_transactions_by_date_range(self, start_date, end_date):
        filtered_transactions = [t for t in self.transactions if start_date <= t["date"] <= end_date]
        if not filtered_transactions:
            print(f"Nenhuma transação no período de {start_date} a {end_date}.")
            return

        print(f"\nTransações de {start_date} a {end_date}:")
        for transaction in filtered_transactions:
            print(f"{transaction['date']}: {transaction['description']}: {transaction['amount']} ({transaction['type']})")

    def monthly_report(self, year, month):
        filtered_transactions = [t for t in self.transactions if t["date"].year == year and t["date"].month == month]
        if not filtered_transactions:
            print(f"Nenhuma transação em {month}/{year}.")
            return

        total_income = sum(t["amount"] for t in filtered_transactions if t["type"] == "receita")
        total_expenses = sum(t["amount"] for t in filtered_transactions if t["type"] == "despesa")
        balance = total_income - total_expenses

        print(f"\nRelatório Mensal - {month}/{year}:")
        print(f"Receita Total: {total_income}")
        print(f"Despesa Total: {total_expenses}")
        print(f"Saldo: {balance}")

    def edit_transaction(self, index, description=None, amount=None, transaction_type=None):
        if index < 0 or index >= len(self.transactions):
            print("Índice de transação inválido.")
            return

        transaction = self.transactions[index]
        if description:
            transaction["description"] = description
        if amount:
            transaction["amount"] = amount
        if transaction_type:
            if transaction_type not in ["receita", "despesa"]:
                print("Tipo de transação inválido. Use 'receita' ou 'despesa'.")
                return
            transaction["type"] = transaction_type

        print("Transação editada com sucesso!")

    def remove_transaction(self, index):
        if index < 0 or index >= len(self.transactions):
            print("Índice de transação inválido.")
            return

        self.transactions.pop(index)
        print("Transação removida com sucesso!")

    def export_to_csv(self, filename):
        import csv
        with open(filename, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["description", "amount", "type", "category", "date"])
            writer.writeheader()
            writer.writerows(self.transactions)
        print(f"Transações exportadas para {filename} com sucesso!")

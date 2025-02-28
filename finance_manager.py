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

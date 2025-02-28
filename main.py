from src.finance_manager import FinanceManager

def main():
    print("Bem-vindo ao Controle Financeiro Pessoal!")
    manager = FinanceManager()

    while True:
        print("\nOpções:")
        print("1. Adicionar transação")
        print("2. Visualizar transações")
        print("3. Calcular saldo")
        print("4. Sair")

        choice = input("Escolha uma opção: ")

        if choice == "1":
            description = input("Descrição: ")
            amount = float(input("Valor: "))
            transaction_type = input("Tipo (receita/despesa): ").lower()
            manager.add_transaction(description, amount, transaction_type)
        elif choice == "2":
            manager.view_transactions()
        elif choice == "3":
            manager.calculate_balance()
        elif choice == "4":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()

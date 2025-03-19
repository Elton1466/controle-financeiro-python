from src.finance_manager import FinanceManager

def main():
    print("Bem-vindo ao Controle Financeiro Pessoal!")
    manager = FinanceManager()

    while True:
        print("\nOpções:")
        print("1. Adicionar transação")
        print("2. Visualizar transações")
        print("3. Calcular saldo")
        print("4. Filtrar transações por categoria")
        print("5. Filtrar transações por data")
        print("6. Gerar relatório mensal")
        print("7. Editar transação")
        print("8. Remover transação")
        print("9. Exportar transações para CSV")
        print("10. Sair")

        choice = input("Escolha uma opção: ")

        if choice == "1":
            description = input("Descrição: ")
            amount = float(input("Valor: "))
            transaction_type = input("Tipo (receita/despesa): ").lower()
            category = input("Categoria: ")
            date = input("Data (YYYY-MM-DD): ")
            manager.add_transaction(description, amount, transaction_type, category, date)
        elif choice == "2":
            manager.view_transactions()
        elif choice == "3":
            manager.calculate_balance()
        elif choice == "4":
            category = input("Digite a categoria para filtrar: ")
            manager.view_transactions_by_category(category)
        elif choice == "5":
            start_date = input("Data inicial (YYYY-MM-DD): ")
            end_date = input("Data final (YYYY-MM-DD): ")
            manager.view_transactions_by_date_range(start_date, end_date)
        elif choice == "6":
            year = int(input("Ano (YYYY): "))
            month = int(input("Mês (MM): "))
            manager.monthly_report(year, month)
        elif choice == "7":
            index = int(input("Índice da transação a editar: "))
            description = input("Nova descrição (deixe em branco para manter): ")
            amount = input("Novo valor (deixe em branco para manter): ")
            amount = float(amount) if amount else None
            transaction_type = input("Novo tipo (receita/despesa, deixe em branco para manter): ").lower()
            manager.edit_transaction(index, description, amount, transaction_type)
        elif choice == "8":
            index = int(input("Índice da transação a remover: "))
            manager.remove_transaction(index)
        elif choice == "9":
            filename = input("Nome do arquivo CSV (ex: transacoes.csv): ")
            manager.export_to_csv(filename)
        elif choice == "10":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()

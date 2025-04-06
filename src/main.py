from finance_manager import FinanceManager
from utils import Utils
from datetime import datetime
import os
import sys
from colorama import Fore, Style, init
from typing import Dict, Any
from pathlib import Path

# Garante que o src está no PATH
sys.path.insert(0, str(Path(__file__).parent))

# Inicializa colorama para cores no terminal
init(autoreset=True)

# Constantes
DATA_FILE = 'financas.dat'
BACKUP_FILE = 'financas.bak'
DATE_FORMAT = "%d-%m-%Y"

class FinancialApp:
    def __init__(self):
        self.manager = self.initialize_manager()
        self.running = True

    def initialize_manager(self) -> FinanceManager:
        """Inicializa o gerenciador financeiro com dados do arquivo"""
        try:
            # Tenta fazer backup antes de carregar
            if os.path.exists(DATA_FILE):
                if os.path.exists(BACKUP_FILE):
                    os.remove(BACKUP_FILE)
                os.rename(DATA_FILE, BACKUP_FILE)

            manager = FinanceManager.load_from_file(DATA_FILE)
            print_success("Dados financeiros carregados com sucesso!")
            return manager
        except FileNotFoundError:
            print_success("Novo arquivo de finanças criado.")
            return FinanceManager()
        except Exception as e:
            print_error(f"Erro ao carregar dados: {str(e)}")
            # Tenta restaurar do backup
            if os.path.exists(BACKUP_FILE):
                os.rename(BACKUP_FILE, DATA_FILE)
                return self.initialize_manager()
            return FinanceManager()

    def run(self):
        """Loop principal da aplicação"""
        while self.running:
            try:
                self.show_main_menu()
                choice = input("\nEscolha uma opção: ").strip()
                self.handle_choice(choice)
            except KeyboardInterrupt:
                self.exit_app()
            except Exception as e:
                print_error(f"Erro inesperado: {str(e)}")
                if not Utils.confirm_action("Continuar executando?"):
                    self.exit_app()

    def show_main_menu(self):
        """Exibe o menu principal"""
        clear_screen()
        print_header("CONTROLE FINANCEIRO PESSOAL")
        
        menu_options = [
            ("1", "Adicionar transação"),
            ("2", "Visualizar transações"),
            ("3", "Calcular saldo"),
            ("4", "Filtrar transações por categoria"),
            ("5", "Filtrar transações por data"),
            ("6", "Gerar relatório mensal"),
            ("7", "Editar transação"),
            ("8", "Remover transação"),
            ("9", "Exportar para CSV"),
            ("10", "Definir orçamento"),
            ("11", "Visualizar orçamentos"),
            ("12", "Fazer backup dos dados"),
            ("13", "Restaurar backup"),
            ("0", "Sair")
        ]
        
        for key, option in menu_options:
            color = Fore.RED if key == "0" else Fore.WHITE
            print(f"{color}{key}. {option}")

    def handle_choice(self, choice: str):
        """Processa a escolha do usuário"""
        actions = {
            '1': self.add_transaction,
            '2': self.view_transactions,
            '3': self.show_balance,
            '4': self.filter_by_category,
            '5': self.filter_by_date,
            '6': self.generate_monthly_report,
            '7': self.edit_transaction,
            '8': self.remove_transaction,
            '9': self.export_to_csv,
            '10': self.set_budget,
            '11': self.view_budgets,
            '12': self.backup_data,
            '13': self.restore_backup,
            '0': self.exit_app
        }
        
        action = actions.get(choice)
        if action:
            action()
        else:
            print_error("Opção inválida. Tente novamente.")
            input("\nPressione Enter para continuar...")

    def add_transaction(self):
        """Adiciona uma nova transação"""
        clear_screen()
        print_header("ADICIONAR TRANSAÇÃO")
        
        transaction_data = self.get_transaction_input()
        if transaction_data:
            success = self.manager.add_transaction(
                description=transaction_data['description'],
                amount=transaction_data['amount'],
                transaction_type=transaction_data['type'],
                category=transaction_data['category'],
                date=transaction_data['date']
            )
            
            if success and self.save_data():
                print_success("Transação adicionada com sucesso!")
            input("\nPressione Enter para continuar...")

    def get_transaction_input(self) -> Dict[str, Any]:
        """Obtém dados de transação do usuário"""
        date = Utils.input_with_validation(
            "Data (DD-MM-YYYY): ",
            Utils.validate_date,
            date_format=DATE_FORMAT
        )
        
        description = input("Descrição: ").strip()
        while not description:
            print_error("Descrição não pode ser vazia!")
            description = input("Descrição: ").strip()
            
        amount = Utils.input_with_validation(
            "Valor: ",
            Utils.validate_amount,
            allow_negative=False
        )
        
        transaction_type = Utils.input_with_validation(
            "Tipo (receita/despesa): ",
            lambda x: (True, x.lower()) if x.lower() in ["receita", "despesa"] else 
                     (False, "Tipo inválido! Use 'receita' ou 'despesa'.")
        )
        
        category = input("Categoria: ").strip()
        while not category:
            print_error("Categoria não pode ser vazia!")
            category = input("Categoria: ").strip()
            
        return {
            'date': date,
            'description': description,
            'amount': float(amount),
            'type': transaction_type,
            'category': category
        }

    def view_transactions(self):
        """Exibe todas as transações"""
        clear_screen()
        print_header("VISUALIZAR TRANSAÇÕES")
        self.manager.view_transactions()
        input("\nPressione Enter para continuar...")

    def show_balance(self):
        """Exibe o saldo atual"""
        clear_screen()
        print_header("SALDO ATUAL")
        self.manager.calculate_balance()
        input("\nPressione Enter para continuar...")

    def filter_by_category(self):
        """Filtra transações por categoria"""
        clear_screen()
        print_header("FILTRAR POR CATEGORIA")
        
        if not self.manager.transactions:
            print_error("Nenhuma transação cadastrada.")
            input("\nPressione Enter para continuar...")
            return
            
        categories = sorted({t['category'] for t in self.manager.transactions})
        print("\nCategorias disponíveis:")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat}")
            
        category_input = input("\nDigite o nome da categoria ou número: ").strip()
        try:
            if category_input.isdigit():
                category = categories[int(category_input)-1]
            else:
                category = category_input
                
            self.manager.view_transactions_by_category(category)
        except (ValueError, IndexError):
            print_error("Seleção de categoria inválida!")
            
        input("\nPressione Enter para continuar...")

    def filter_by_date(self):
        """Filtra transações por intervalo de datas"""
        clear_screen()
        print_header("FILTRAR POR DATA")
        
        print("\nInforme o intervalo de datas:")
        start_date = Utils.input_with_validation(
            "Data inicial (DD-MM-YYYY): ",
            Utils.validate_date,
            date_format=DATE_FORMAT
        )
        
        end_date = Utils.input_with_validation(
            "Data final (DD-MM-YYYY): ",
            Utils.validate_date,
            date_format=DATE_FORMAT
        )
        
        if start_date > end_date:
            print_error("Data inicial não pode ser maior que data final!")
            input("\nPressione Enter para continuar...")
            return
            
        self.manager.view_transactions_by_date_range(
            start_date.strftime(DATE_FORMAT),
            end_date.strftime(DATE_FORMAT)
        )
        input("\nPressione Enter para continuar...")

    def generate_monthly_report(self):
        """Gera relatório mensal"""
        clear_screen()
        print_header("RELATÓRIO MENSAL")
        
        year = Utils.input_with_validation(
            "Ano (YYYY): ",
            lambda x: (True, int(x)) if x.isdigit() and len(x) == 4 else
                     (False, "Ano inválido! Use o formato YYYY.")
        )
        
        month = Utils.input_with_validation(
            "Mês (MM): ",
            lambda x: (True, int(x)) if x.isdigit() and 1 <= int(x) <= 12 else
                     (False, "Mês inválido! Use valores entre 01 e 12.")
        )
        
        self.manager.monthly_report(year, month)
        input("\nPressione Enter para continuar...")

    def edit_transaction(self):
        """Edita uma transação existente"""
        clear_screen()
        print_header("EDITAR TRANSAÇÃO")
        
        if not self.manager.transactions:
            print_error("Nenhuma transação cadastrada.")
            input("\nPressione Enter para continuar...")
            return
            
        self.manager.view_transactions()
        
        try:
            index = int(input("\nÍndice da transação a editar: "))
            if index < 0 or index >= len(self.manager.transactions):
                print_error("Índice inválido!")
                return
                
            print("\nDeixe em branco para manter o valor atual.")
            transaction = self.manager.transactions[index]
            
            new_description = input(f"Nova descrição [{transaction['description']}]: ").strip()
            new_description = new_description if new_description else None
            
            new_amount = input(f"Novo valor [{transaction['amount']}]: ").strip()
            new_amount = float(new_amount) if new_amount else None
            
            new_type = input(f"Novo tipo (receita/despesa) [{transaction['type']}]: ").lower().strip()
            if new_type and new_type not in ["receita", "despesa"]:
                print_error("Tipo inválido! Use 'receita' ou 'despesa'.")
                return
            new_type = new_type if new_type else None
            
            if self.manager.edit_transaction(index, new_description, new_amount, new_type):
                if self.save_data():
                    print_success("Transação editada com sucesso!")
        except ValueError:
            print_error("Índice deve ser um número!")
            
        input("\nPressione Enter para continuar...")

    def remove_transaction(self):
        """Remove uma transação"""
        clear_screen()
        print_header("REMOVER TRANSAÇÃO")
        
        if not self.manager.transactions:
            print_error("Nenhuma transação cadastrada.")
            input("\nPressione Enter para continuar...")
            return
            
        self.manager.view_transactions()
        
        try:
            index = int(input("\nÍndice da transação a remover: "))
            if Utils.confirm_action("Tem certeza que deseja remover esta transação?"):
                if self.manager.remove_transaction(index):
                    if self.save_data():
                        print_success("Transação removida com sucesso!")
        except ValueError:
            print_error("Índice deve ser um número!")
            
        input("\nPressione Enter para continuar...")

    def export_to_csv(self):
        """Exporta transações para CSV"""
        clear_screen()
        print_header("EXPORTAR PARA CSV")
        
        default_filename = f"transacoes_{datetime.now().strftime('%Y%m%d')}.csv"
        filename = input(f"Nome do arquivo ({default_filename}): ").strip()
        filename = filename if filename else default_filename
        
        if not filename.endswith('.csv'):
            filename += '.csv'
            
        if os.path.exists(filename):
            if not Utils.confirm_action(f"Arquivo {filename} já existe. Sobrescrever?"):
                return
                
        if self.manager.export_to_csv(filename):
            print_success(f"Transações exportadas para {filename}")
        input("\nPressione Enter para continuar...")

    def set_budget(self):
        """Define um orçamento para categoria"""
        clear_screen()
        print_header("DEFINIR ORÇAMENTO")
        
        category = input("Categoria: ").strip()
        while not category:
            print_error("Categoria não pode ser vazia!")
            category = input("Categoria: ").strip()
            
        amount = Utils.input_with_validation(
            "Valor do orçamento: ",
            Utils.validate_amount,
            allow_negative=False
        )
        
        if self.manager.set_budget(category, float(amount)) and self.save_data():
            print_success(f"Orçamento definido para {category}")
        input("\nPressione Enter para continuar...")

    def view_budgets(self):
        """Exibe todos os orçamentos"""
        clear_screen()
        print_header("VISUALIZAR ORÇAMENTOS")
        self.manager.view_budgets()
        input("\nPressione Enter para continuar...")

    def backup_data(self):
        """Cria um backup dos dados"""
        clear_screen()
        print_header("BACKUP DOS DADOS")
        
        backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dat"
        try:
            with open(backup_file, 'wb') as f:
                pickle.dump({
                    'transactions': self.manager.transactions,
                    'budgets': self.manager.budgets
                }, f)
            print_success(f"Backup criado com sucesso: {backup_file}")
        except Exception as e:
            print_error(f"Falha ao criar backup: {str(e)}")
            
        input("\nPressione Enter para continuar...")

    def restore_backup(self):
        """Restaura dados de um backup"""
        clear_screen()
        print_header("RESTAURAR BACKUP")
        
        if not os.path.exists(BACKUP_FILE):
            print_error("Nenhum backup encontrado!")
            input("\nPressione Enter para continuar...")
            return
            
        if Utils.confirm_action("Tem certeza que deseja restaurar o último backup?"):
            try:
                os.rename(DATA_FILE, DATA_FILE + ".tmp")
                os.rename(BACKUP_FILE, DATA_FILE)
                self.manager = FinanceManager.load_from_file(DATA_FILE)
                print_success("Backup restaurado com sucesso!")
            except Exception as e:
                print_error(f"Falha ao restaurar backup: {str(e)}")
                # Tentar reverter
                if os.path.exists(DATA_FILE + ".tmp"):
                    os.rename(DATA_FILE + ".tmp", DATA_FILE)
                    
        input("\nPressione Enter para continuar...")

    def save_data(self) -> bool:
        """Salva os dados no arquivo"""
        try:
            if self.manager.save_to_file(DATA_FILE):
                return True
            print_error("Falha ao salvar dados.")
            return False
        except Exception as e:
            print_error(f"Erro ao salvar dados: {str(e)}")
            return False

    def exit_app(self):
        """Encerra a aplicação"""
        if Utils.confirm_action("\nTem certeza que deseja sair?"):
            if self.save_data():
                print(Fore.GREEN + "\nDados salvos com sucesso. Até logo!")
            else:
                print(Fore.RED + "\nAtenção: Os dados podem não ter sido salvos corretamente!")
            self.running = False

# Funções auxiliares de UI
def clear_screen():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Imprime um cabeçalho formatado"""
    print(Fore.CYAN + "\n" + "=" * 70)
    print(Fore.CYAN + f"\t{title.center(60)}")
    print(Fore.CYAN + "=" * 70 + Style.RESET_ALL)

def print_success(message):
    """Imprime mensagem de sucesso"""
    print(Fore.GREEN + f"\n✓ {message}" + Style.RESET_ALL)

def print_error(message):
    """Imprime mensagem de erro"""
    print(Fore.RED + f"\n✗ {message}" + Style.RESET_ALL)

if __name__ == "__main__":
    try:
        app = FinancialApp()
        app.run()
    except Exception as e:
        print_error(f"Erro fatal: {str(e)}")
        sys.exit(1)
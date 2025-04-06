from datetime import datetime
from typing import List, Dict, Optional, Tuple, Union
import csv
import pickle
import os
from colorama import Fore, Style
import hashlib

class FinanceManager:
    def __init__(self):
        self.transactions: List[Dict] = []
        self.budgets: Dict[str, float] = {}
        self.goals: Dict[str, Dict] = {}

    def add_transaction(self, description: str, amount: float, 
                   transaction_type: str, category: str, 
                   date: Union[datetime, str]) -> bool:
        """
        Adiciona uma nova transação ao gerenciador com validação robusta.
        
        Args:
            description: Descrição da transação
            amount: Valor da transação (positivo)
            transaction_type: 'receita' ou 'despesa'
            category: Categoria da transação
            date: Data como datetime ou string no formato DD-MM-YYYY
            
        Returns:
            bool: True se a transação foi adicionada com sucesso
        """
        # Validação do tipo de transação
        if transaction_type.lower() not in ["receita", "despesa"]:
            print(Fore.RED + "Tipo de transação inválido. Use 'receita' ou 'despesa'.")
            return False

        # Validação do valor
        if not isinstance(amount, (int, float)) or amount <= 0:
            print(Fore.RED + "O valor deve ser um número positivo.")
            return False

        # Conversão e validação da data
        if isinstance(date, str):
            try:
                date = datetime.strptime(date, "%d-%m-%Y")
            except ValueError:
                print(Fore.RED + "Formato de data inválido. Use DD-MM-YYYY.")
                return False
        elif not isinstance(date, datetime):
            print(Fore.RED + "Tipo de data inválido. Use datetime ou string no formato DD-MM-YYYY.")
            return False

        # Validação de descrição e categoria
        if not description.strip():
            print(Fore.RED + "A descrição não pode ser vazia.")
            return False
            
        if not category.strip():
            print(Fore.RED + "A categoria não pode ser vazia.")
            return False

        self.transactions.append({
            "description": description.strip(),
            "amount": float(amount),
            "type": transaction_type.lower(),
            "category": category.strip(),
            "date": date
        })
        
        # Ordena transações por data
        self.transactions.sort(key=lambda x: x['date'])
        return True

    def view_transactions(self, transactions=None):
        """Exibe transações em formato tabular melhorado"""
        transactions_to_show = transactions if transactions is not None else self.transactions
        
        if not transactions_to_show:
            print(f"{Fore.YELLOW}Nenhuma transação registrada.{Style.RESET_ALL}")
            return
        
        # Formata as colunas
        print(f"{'Índice':<7} | {'Data':<10} | {'Descrição':<25} | {'Valor':<12} | {'Tipo':<8} | {'Categoria':<15}")
        print("-" * 70)
        
        for idx, transaction in enumerate(transactions_to_show):
            # Formata valor com cores
            amount = transaction['amount']
            amount_color = Fore.GREEN if transaction['type'] == 'receita' else Fore.RED
            amount_str = f"{amount_color}R$ {amount:,.2f}{Style.RESET_ALL}"
            
            # Formata data
            date_str = transaction['date'].strftime('%d/%m/%Y')
            
            # Limita o tamanho da descrição
            description = (transaction['description'][:22] + '...') if len(transaction['description']) > 25 else transaction['description']
            
            print(f"{idx:<7} | {date_str:<10} | {description:<25} | {amount_str:<12} | "
                f"{transaction['type']:<8} | {transaction['category']:<15}")
        
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
# transactions_sorted = sorted(transactions_to_show, key=lambda x: x['date']) **** adicionar futuramente

    def calculate_balance(self) -> Dict[str, float]:
        """
        Calcula o saldo atual e retorna um dicionário com:
        - receita_total
        - despesa_total
        - saldo
        - categorias_com_problema (orçamento excedido)
        """
        total_income = sum(t["amount"] for t in self.transactions if t["type"] == "receita")
        total_expenses = sum(t["amount"] for t in self.transactions if t["type"] == "despesa")
        balance = total_income - total_expenses
        
        result = {
            'receita_total': total_income,
            'despesa_total': total_expenses,
            'saldo': balance,
            'categorias_com_problema': self._check_budget_exceeded()
        }
        
        return result

    def _check_budget_exceeded(self) -> Dict[str, Dict[str, float]]:
        """
        Verifica orçamentos excedidos por categoria.
        
        Returns:
            Dicionário com categorias que excederam o orçamento
            Formato: {categoria: {'gasto': X, 'orçamento': Y}}
        """
        exceeded = {}
        for category, budget in self.budgets.items():
            spent = sum(t['amount'] for t in self.transactions 
                       if t['category'] == category and t['type'] == 'despesa')
            if spent > budget:
                exceeded[category] = {
                    'gasto': spent,
                    'orçamento': budget,
                    'excedido': spent - budget
                }
        return exceeded

    def filter_transactions(self, category: Optional[str] = None,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None,
                           transaction_type: Optional[str] = None) -> List[Dict]:
        """
        Filtra transações com base em múltiplos critérios.
        
        Args:
            category: Filtrar por categoria
            start_date: Data inicial do intervalo
            end_date: Data final do intervalo
            transaction_type: 'receita' ou 'despesa'
            
        Returns:
            Lista de transações filtradas
        """
        filtered = self.transactions.copy()
        
        if category:
            filtered = [t for t in filtered if t["category"].lower() == category.lower()]
            
        if start_date and end_date:
            filtered = [t for t in filtered if start_date <= t["date"] <= end_date]
            
        if transaction_type:
            filtered = [t for t in filtered if t["type"] == transaction_type.lower()]
            
        return filtered

    def view_transactions_by_category(self, category: str) -> None:
        """Exibe transações de uma categoria específica."""
        filtered = self.filter_transactions(category=category)
        if not filtered:
            print(Fore.YELLOW + f"Nenhuma transação na categoria '{category}'.")
            return
            
        total = sum(t['amount'] for t in filtered)
        print(Fore.CYAN + f"\nTRANSAÇÕES NA CATEGORIA '{category.upper()}':")
        print(f"Total: {total:.2f}")
        self.view_transactions(filtered)

    def view_transactions_by_date_range(self, start_date: str, end_date: str) -> None:
        """Exibe transações em um intervalo de datas."""
        try:
            start = datetime.strptime(start_date, "%d-%m-%Y")
            end = datetime.strptime(end_date, "%d-%m-%Y")
            
            if start > end:
                print(Fore.RED + "Data inicial não pode ser maior que data final!")
                return
                
            filtered = self.filter_transactions(start_date=start, end_date=end)
            
            if not filtered:
                print(Fore.YELLOW + f"Nenhuma transação entre {start_date} e {end_date}.")
                return
                
            total_income = sum(t['amount'] for t in filtered if t['type'] == 'receita')
            total_expenses = sum(t['amount'] for t in filtered if t['type'] == 'despesa')
            
            print(Fore.CYAN + f"\nTRANSAÇÕES DE {start_date} A {end_date}:")
            print(Fore.GREEN + f"Receita Total: {total_income:.2f}")
            print(Fore.RED + f"Despesa Total: {total_expenses:.2f}")
            print(Fore.BLUE + f"Saldo: {total_income - total_expenses:.2f}")
            
            self.view_transactions(filtered)
        except ValueError:
            print(Fore.RED + "Formato de data inválido. Use DD-MM-YYYY.")

    def monthly_report(self, year: int, month: int) -> Dict:
        """
        Gera um relatório mensal detalhado.
        
        Returns:
            Dicionário com o resumo do relatório
        """
        filtered = [
            t for t in self.transactions 
            if t["date"].year == year and t["date"].month == month
        ]
        
        if not filtered:
            print(Fore.YELLOW + f"Nenhuma transação em {month:02d}/{year}.")
            return {}
            
        total_income = sum(t["amount"] for t in filtered if t["type"] == "receita")
        total_expenses = sum(t["amount"] for t in filtered if t["type"] == "despesa")
        balance = total_income - total_expenses
        budget_status = self._check_budget_exceeded()

        print(Fore.CYAN + f"\nRELATÓRIO MENSAL - {month:02d}/{year}:")
        print(Fore.WHITE + "-" * 40)
        print(Fore.GREEN + f"Receita Total: {total_income:.2f}")
        print(Fore.RED + f"Despesa Total: {total_expenses:.2f}")
        print(Fore.BLUE + f"Saldo: {balance:.2f}")
        print(Fore.WHITE + "-" * 40)
        
        # Detalhamento por categoria
        categories = {t['category'] for t in filtered}
        print("\nDETALHAMENTO POR CATEGORIA:")
        for category in sorted(categories):
            cat_income = sum(t['amount'] for t in filtered 
                         if t['category'] == category and t['type'] == 'receita')
            cat_expenses = sum(t['amount'] for t in filtered 
                             if t['category'] == category and t['type'] == 'despesa')
            
            print(f"\n{Fore.CYAN}{category.upper()}{Style.RESET_ALL}")
            if cat_income > 0:
                print(f"  Receitas: {Fore.GREEN}{cat_income:.2f}{Style.RESET_ALL}")
            if cat_expenses > 0:
                print(f"  Despesas: {Fore.RED}{cat_expenses:.2f}{Style.RESET_ALL}")
                
            # Verifica orçamento se existir para esta categoria
            if category in self.budgets:
                budget = self.budgets[category]
                if cat_expenses > budget:
                    print(Fore.RED + f"  ATENÇÃO: Orçamento excedido em {cat_expenses - budget:.2f}")
                else:
                    print(Fore.GREEN + f"  Orçamento restante: {budget - cat_expenses:.2f}")

        return {
            'year': year,
            'month': month,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'balance': balance,
            'budget_status': budget_status
        }

    def edit_transaction(self, index: int, 
                        description: Optional[str] = None, 
                        amount: Optional[float] = None, 
                        transaction_type: Optional[str] = None) -> bool:
        """
        Edita uma transação existente.
        
        Args:
            index: Índice da transação a editar
            description: Nova descrição (opcional)
            amount: Novo valor (opcional)
            transaction_type: Novo tipo (opcional)
            
        Returns:
            bool: True se a edição foi bem-sucedida
        """
        if index < 0 or index >= len(self.transactions):
            print(Fore.RED + "Índice de transação inválido.")
            return False

        transaction = self.transactions[index]
        
        if description is not None:
            if not description.strip():
                print(Fore.RED + "Descrição não pode ser vazia.")
                return False
            transaction["description"] = description.strip()
            
        if amount is not None:
            if not isinstance(amount, (int, float)) or amount <= 0:
                print(Fore.RED + "Valor deve ser um número positivo.")
                return False
            transaction["amount"] = float(amount)
            
        if transaction_type is not None:
            if transaction_type.lower() not in ["receita", "despesa"]:
                print(Fore.RED + "Tipo de transação inválido. Use 'receita' ou 'despesa'.")
                return False
            transaction["type"] = transaction_type.lower()

        return True

    def remove_transaction(self, index: int) -> bool:
        """
        Remove uma transação.
        
        Args:
            index: Índice da transação a remover
            
        Returns:
            bool: True se a remoção foi bem-sucedida
        """
        if index < 0 or index >= len(self.transactions):
            print(Fore.RED + "Índice de transação inválido.")
            return False
            
        self.transactions.pop(index)
        return True

    def export_to_csv(self, filename: str) -> bool:
        """
        Exporta transações para arquivo CSV.
        
        Args:
            filename: Nome do arquivo de saída
            
        Returns:
            bool: True se a exportação foi bem-sucedida
        """
        try:
            with open(filename, "w", newline="", encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=[
                    "date", "description", "amount", "type", "category"
                ])
                writer.writeheader()
                for transaction in self.transactions:
                    row = transaction.copy()
                    row["date"] = row["date"].strftime("%d-%m-%Y")
                    writer.writerow(row)
            return True
        except Exception as e:
            print(Fore.RED + f"Erro ao exportar transações: {e}")
            return False

    def save_to_file(self, filename: str) -> bool:
        """
        Salva os dados no arquivo com verificação de integridade.
        
        Args:
            filename: Nome do arquivo para salvar
            
        Returns:
            bool: True se o salvamento foi bem-sucedido
        """
        try:
            # Cria um checksum para verificação de integridade
            checksum = hashlib.md5(
                pickle.dumps({
                    'transactions': self.transactions,
                    'budgets': self.budgets
                })
            ).hexdigest()
            
            data = {
                'transactions': self.transactions,
                'budgets': self.budgets,
                'goals': getattr(self, 'goals', {}),
                'checksum': checksum,
                'version': '1.0'
            }
            
            # Cria backup antes de salvar
            if os.path.exists(filename):
                backup_name = filename + '.bak'
                if os.path.exists(backup_name):
                    os.remove(backup_name)
                os.rename(filename, backup_name)
            
            with open(filename, 'wb') as file:
                pickle.dump(data, file)
            return True
        except Exception as e:
            print(Fore.RED + f"Erro ao salvar dados: {e}")
            return False

    @classmethod
    def load_from_file(cls, filename: str) -> 'FinanceManager':
        """
        Carrega os dados do arquivo com verificação de integridade.
        
        Args:
            filename: Nome do arquivo para carregar
            
        Returns:
            FinanceManager: Instância carregada ou nova instância em caso de erro
        """
        try:
            if not os.path.exists(filename):
                return cls()
                
            with open(filename, 'rb') as file:
                data = pickle.load(file)
                
                # Verificação básica de integridade
                if not isinstance(data, dict):
                    raise ValueError("Formato de arquivo inválido")
                    
                # Verifica checksum se existir
                if 'checksum' in data:
                    current_data = {k: v for k, v in data.items() if k != 'checksum'}
                    current_checksum = hashlib.md5(pickle.dumps(current_data)).hexdigest()
                    if current_checksum != data['checksum']:
                        raise ValueError("Checksum inválido - dados corrompidos")
                
                manager = cls()
                manager.transactions = data.get('transactions', [])
                manager.budgets = data.get('budgets', {})
                manager.goals = data.get('goals', {})
                
                # Converte strings de data para objetos datetime
                for transaction in manager.transactions:
                    if isinstance(transaction['date'], str):
                        transaction['date'] = datetime.strptime(transaction['date'], "%d-%m-%Y")
                
                return manager
        except Exception as e:
            print(Fore.RED + f"Erro ao carregar dados: {e}")
            return cls()

    def set_budget(self, category: str, amount: float) -> bool:
        """
        Define um orçamento para uma categoria.
        
        Args:
            category: Nome da categoria
            amount: Valor do orçamento
            
        Returns:
            bool: True se o orçamento foi definido com sucesso
        """
        if amount <= 0:
            print(Fore.RED + "O valor do orçamento deve ser positivo.")
            return False
            
        self.budgets[category] = float(amount)
        return True

    def view_budgets(self) -> None:
        """Exibe todos os orçamentos e status."""
        if not self.budgets:
            print(Fore.YELLOW + "Nenhum orçamento definido.")
            return
            
        headers = ["Categoria", "Orçamento", "Gasto", "Saldo", "Status"]
        rows = []
        
        for category, budget in sorted(self.budgets.items()):
            spent = sum(t['amount'] for t in self.transactions 
                       if t['category'] == category and t['type'] == 'despesa')
            balance = budget - spent
            status = (Fore.GREEN + "Dentro") if spent <= budget else (Fore.RED + "Excedido")
            
            rows.append([
                category,
                f"{budget:.2f}",
                f"{spent:.2f}",
                f"{balance:.2f}",
                status
            ])
        
        from utils import Utils
        Utils.print_table(headers, rows)

    # Novos métodos para metas financeiras
    def set_financial_goal(self, goal_name: str, target_amount: float, 
                          target_date: str) -> bool:
        """
        Define uma meta financeira.
        
        Args:
            goal_name: Nome da meta
            target_amount: Valor alvo
            target_date: Data alvo (DD-MM-YYYY)
            
        Returns:
            bool: True se a meta foi definida com sucesso
        """
        try:
            target_date = datetime.strptime(target_date, "%d-%m-%Y")
            if target_date < datetime.now():
                print(Fore.RED + "A data da meta não pode ser no passado.")
                return False
                
            self.goals[goal_name] = {
                'target_amount': float(target_amount),
                'target_date': target_date,
                'saved_amount': 0.0,
                'created_at': datetime.now()
            }
            return True
        except ValueError:
            print(Fore.RED + "Formato de data inválido. Use DD-MM-YYYY.")
            return False

    def add_to_goal(self, goal_name: str, amount: float) -> bool:
        """
        Adiciona valor a uma meta financeira.
        
        Args:
            goal_name: Nome da meta
            amount: Valor a adicionar
            
        Returns:
            bool: True se o valor foi adicionado com sucesso
        """
        if goal_name not in self.goals:
            print(Fore.RED + f"Meta '{goal_name}' não encontrada.")
            return False
            
        if amount <= 0:
            print(Fore.RED + "O valor deve ser positivo.")
            return False
            
        self.goals[goal_name]['saved_amount'] += float(amount)
        return True

    def view_goals(self) -> None:
        """Exibe o progresso de todas as metas."""
        if not self.goals:
            print(Fore.YELLOW + "Nenhuma meta definida.")
            return
            
        for name, goal in self.goals.items():
            progress = (goal['saved_amount'] / goal['target_amount']) * 100
            remaining = goal['target_amount'] - goal['saved_amount']
            days_remaining = (goal['target_date'] - datetime.now()).days
            
            print(Fore.CYAN + f"\nMeta: {name}")
            print(f"Progresso: [{'#' * int(progress//5)}{' ' * (20 - int(progress//5))}] {progress:.1f}%")
            print(f"Arrecadado: {goal['saved_amount']:.2f} de {goal['target_amount']:.2f}")
            print(f"Restante: {remaining:.2f}")
            print(f"Prazo: {goal['target_date'].strftime('%d/%m/%Y')} ({days_remaining} dias restantes)")
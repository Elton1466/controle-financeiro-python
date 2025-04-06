import re
from datetime import datetime
from typing import Tuple, Union, List, Optional, Callable, Any
from colorama import Fore, Style

class Utils:
    # Constantes para validação
    DATE_FORMAT = "%d-%m-%Y"
    CURRENCY_SYMBOLS = {'R$', '$', '€', '£', '¥'}
    
    @staticmethod
    def validate_amount(
        amount: Union[str, float, int],
        allow_negative: bool = False,
        max_value: Optional[float] = None,
        min_value: Optional[float] = None,
        allow_zero: bool = True
    ) -> Tuple[bool, Union[float, str]]:
        """
        Valida um valor monetário com diversos critérios.
        
        Args:
            amount: Valor a ser validado (pode ser string, float ou int)
            allow_negative: Permite valores negativos
            max_value: Valor máximo permitido
            min_value: Valor mínimo permitido
            allow_zero: Permite valor zero
            
        Returns:
            tuple[bool, Union[float, str]]: 
                (True, valor_convertido) se válido, 
                (False, mensagem_erro) caso contrário
        """
        # Converte para string se for numérico
        if isinstance(amount, (float, int)):
            amount_str = str(amount)
        else:
            amount_str = amount.strip()

        # Remove símbolos de moeda e espaços
        amount_cleaned = re.sub(r'[^\d,-]', '', amount_str)
        
        # Verifica formatos inválidos
        if amount_cleaned.count('.') > 1 or amount_cleaned.count(',') > 1:
            return False, f"{Fore.RED}Formato numérico inválido. Use apenas um separador decimal.{Style.RESET_ALL}"
        
        # Uniformiza o separador decimal
        if ',' in amount_cleaned and '.' in amount_cleaned:
            # Caso como "1.234,56" - remove pontos de milhar
            amount_cleaned = amount_cleaned.replace('.', '').replace(',', '.')
        elif ',' in amount_cleaned:
            # Caso como "1234,56"
            amount_cleaned = amount_cleaned.replace(',', '.')
        
        try:
            value = float(amount_cleaned)
            
            # Validações adicionais
            if not allow_negative and value < 0:
                return False, f"{Fore.RED}Valores negativos não são permitidos.{Style.RESET_ALL}"
                
            if not allow_zero and value == 0:
                return False, f"{Fore.RED}Valor zero não é permitido.{Style.RESET_ALL}"
                
            if max_value is not None and value > max_value:
                return False, f"{Fore.RED}O valor não pode ser maior que {max_value:.2f}.{Style.RESET_ALL}"
                
            if min_value is not None and value < min_value:
                return False, f"{Fore.RED}O valor não pode ser menor que {min_value:.2f}.{Style.RESET_ALL}"
                
            return True, value
        except ValueError:
            return False, f"{Fore.RED}Valor inválido. Digite um número válido.{Style.RESET_ALL}"

    @staticmethod
    def validate_date(
        date_str: str, 
        date_format: str = DATE_FORMAT,
        allow_future: bool = False
    ) -> Tuple[bool, Union[datetime, str]]:
        """
        Valida uma string de data com múltiplos critérios.
        
        Args:
            date_str: String contendo a data
            date_format: Formato esperado (default: DD-MM-YYYY)
            allow_future: Permite datas futuras
            
        Returns:
            tuple[bool, Union[datetime, str]]: 
                (True, datetime) se válido, 
                (False, mensagem_erro) caso contrário
        """
        try:
            date_obj = datetime.strptime(date_str.strip(), date_format)
            
            if not allow_future and date_obj > datetime.now():
                return False, f"{Fore.RED}Data não pode ser futura.{Style.RESET_ALL}"
                
            return True, date_obj
        except ValueError:
            return False, f"{Fore.RED}Formato de data inválido. Use {date_format}.{Style.RESET_ALL}"

    @staticmethod
    def validate_date_range(
        start_date: str,
        end_date: str,
        date_format: str = DATE_FORMAT
    ) -> Tuple[bool, Union[Tuple[datetime, datetime], str]]:
        """
        Valida um intervalo de datas.
        
        Args:
            start_date: Data inicial
            end_date: Data final
            date_format: Formato das datas
            
        Returns:
            tuple[bool, Union[tuple[datetime, datetime], str]]: 
                (True, (start, end)) se válido, 
                (False, mensagem_erro) caso contrário
        """
        # Valida data inicial
        valid_start, start = Utils.validate_date(start_date, date_format)
        if not valid_start:
            return False, start
            
        # Valida data final
        valid_end, end = Utils.validate_date(end_date, date_format)
        if not valid_end:
            return False, end
            
        # Verifica intervalo válido
        if start > end:
            return False, f"{Fore.RED}Data inicial não pode ser maior que data final.{Style.RESET_ALL}"
            
        return True, (start, end)

    @staticmethod
    def format_currency(
        value: float,
        symbol: str = 'R$',
        decimal_places: int = 2,
        thousands_sep: str = '.',
        decimal_sep: str = ','
    ) -> str:
        """
        Formata um valor float como moeda.
        
        Args:
            value: Valor a formatar
            symbol: Símbolo monetário (default: 'R$')
            decimal_places: Casas decimais
            thousands_sep: Separador de milhar
            decimal_sep: Separador decimal
            
        Returns:
            str: Valor formatado como moeda
        """
        # Parte inteira com separadores de milhar
        int_part = "{:,.0f}".format(abs(value)).replace(",", "X").replace(".", ",").replace("X", ".")
        
        # Parte decimal
        decimal_part = ("{:.%df}" % decimal_places).format(abs(value) % 1)[2:]
        
        # Sinal
        sign = '-' if value < 0 else ''
        
        # Monta a string final
        return f"{sign}{symbol} {int_part}{decimal_sep}{decimal_part}"

    @staticmethod
    def currency_to_float(currency_str: str) -> float:
        """
        Converte uma string de moeda para float.
        
        Args:
            currency_str: String no formato monetário (ex: "R$ 1.234,56")
            
        Returns:
            float: Valor convertido
            
        Raises:
            ValueError: Se a string não puder ser convertida
        """
        try:
            # Remove símbolos e espaços
            cleaned = re.sub(r'[^\d,-]', '', currency_str.strip())
            
            # Verifica se tem separador decimal
            if ',' in cleaned:
                # Caso brasileiro: 1.234,56 → 1234.56
                cleaned = cleaned.replace('.', '').replace(',', '.')
            elif '.' in cleaned and cleaned.count('.') == 1:
                # Caso internacional: 1,234.56 → 1234.56
                cleaned = cleaned.replace(',', '')
                
            return float(cleaned)
        except ValueError:
            raise ValueError(f"{Fore.RED}Formato monetário inválido. Exemplos válidos: 'R$ 1.234,56' ou '1,234.56'{Style.RESET_ALL}")

    @staticmethod
    def input_with_validation(
        prompt: str,
        validation_func: Callable,
        *validation_args,
        **validation_kwargs
    ) -> Any:
        """
        Solicita entrada do usuário com validação.
        
        Args:
            prompt: Mensagem para exibir
            validation_func: Função de validação
            *validation_args: Argumentos posicionais para a validação
            **validation_kwargs: Argumentos nomeados para a validação
            
        Returns:
            Any: Valor validado conforme retornado pela validation_func
        """
        while True:
            user_input = input(prompt).strip()
            is_valid, result = validation_func(user_input, *validation_args, **validation_kwargs)
            
            if is_valid:
                return result
                
            print(result)

    @staticmethod
    def print_table(
        headers: List[str],
        rows: List[List[Any]],
        col_widths: Optional[List[int]] = None,
        max_width: int = 80,
        align: str = 'left',
        header_color: str = Fore.CYAN,
        row_colors: Optional[List[str]] = None
    ) -> None:
        """
        Imprime dados em formato de tabela com formatação avançada.
        
        Args:
            headers: Lista de cabeçalhos
            rows: Lista de listas contendo os dados
            col_widths: Larguras opcionais para cada coluna
            max_width: Largura máxima total da tabela
            align: Alinhamento ('left', 'right', 'center')
            header_color: Cor dos cabeçalhos
            row_colors: Lista de cores para as linhas (cíclica)
        """
        if not rows:
            print(f"{Fore.YELLOW}Nenhum dado para exibir.{Style.RESET_ALL}")
            return
            
        # Determina alinhamento
        align_map = {'left': '<', 'right': '>', 'center': '^'}
        align_char = align_map.get(align.lower(), '<')
        
        # Calcula larguras das colunas se não fornecidas
        if not col_widths:
            col_widths = []
            for col in zip(headers, *rows):
                max_content_len = max(len(str(item)) for item in col)
                col_widths.append(min(max_content_len, max_width // len(headers)))
        
        # Ajusta larguras para não exceder max_width
        total_width = sum(col_widths) + (3 * (len(headers) - 1))  # 3 para separadores
        if total_width > max_width:
            ratio = max_width / total_width
            col_widths = [int(w * ratio) for w in col_widths]
        
        # Imprime cabeçalho
        header_parts = []
        for h, w in zip(headers, col_widths):
            header_parts.append(f"{header_color}{str(h):{align_char}{w}}{Style.RESET_ALL}")
        print(" | ".join(header_parts))
        
        # Linha separadora
        print("-" * (sum(col_widths) + (3 * (len(headers) - 1))))
        
        # Imprime linhas com cores alternadas
        row_colors = row_colors or [Fore.WHITE, Fore.LIGHTWHITE_EX]
        for i, row in enumerate(rows):
            color = row_colors[i % len(row_colors)]
            row_parts = []
            for item, w in zip(row, col_widths):
                text = str(item)
                if len(text) > w:
                    text = text[:w-3] + "..."
                row_parts.append(f"{color}{text:{align_char}{w}}{Style.RESET_ALL}")
            print(" | ".join(row_parts))

    @staticmethod
    def confirm_action(prompt: str = "Confirmar ação? (S/N): ") -> bool:
        """
        Solicita confirmação do usuário para uma ação.
        
        Args:
            prompt: Mensagem de confirmação
            
        Returns:
            bool: True se confirmado, False caso contrário
        """
        while True:
            response = input(prompt).strip().upper()
            if response in {'S', 'SIM', 'Y', 'YES'}:
                return True
            if response in {'N', 'NÃO', 'NAO', 'NO'}:
                return False
            print(f"{Fore.RED}Opção inválida. Responda com S(Sim) ou N(Não).{Style.RESET_ALL}")

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Valida o formato de um endereço de email.
        
        Args:
            email: Endereço de email a validar
            
        Returns:
            tuple[bool, str]: (True, "OK") se válido, (False, mensagem) caso contrário
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email.strip()):
            return True, f"{Fore.GREEN}Email válido.{Style.RESET_ALL}"
        return False, f"{Fore.RED}Email inválido. Use o formato nome@dominio.com.{Style.RESET_ALL}"

    @staticmethod
    def validate_password(password: str, min_length: int = 8) -> Tuple[bool, str]:
        """
        Valida a força de uma senha.
        
        Args:
            password: Senha a validar
            min_length: Comprimento mínimo requerido
            
        Returns:
            tuple[bool, str]: (True, "OK") se válido, (False, mensagem) caso contrário
        """
        if len(password) < min_length:
            return False, f"{Fore.RED}A senha deve ter pelo menos {min_length} caracteres.{Style.RESET_ALL}"
        if not re.search(r'[A-Z]', password):
            return False, f"{Fore.RED}A senha deve conter pelo menos uma letra maiúscula.{Style.RESET_ALL}"
        if not re.search(r'[a-z]', password):
            return False, f"{Fore.RED}A senha deve conter pelo menos uma letra minúscula.{Style.RESET_ALL}"
        if not re.search(r'[0-9]', password):
            return False, f"{Fore.RED}A senha deve conter pelo menos um número.{Style.RESET_ALL}"
        if not re.search(r'[^A-Za-z0-9]', password):
            return False, f"{Fore.RED}A senha deve conter pelo menos um caractere especial.{Style.RESET_ALL}"
        return True, f"{Fore.GREEN}Senha válida.{Style.RESET_ALL}"

    @staticmethod
    def mask_sensitive_data(data: str, visible_chars: int = 4, mask_char: str = '*') -> str:
        """
        Mascara dados sensíveis como cartões de crédito ou CPF.
        
        Args:
            data: Dado a mascarar
            visible_chars: Número de caracteres visíveis no final
            mask_char: Caractere usado para mascarar
            
        Returns:
            str: Dado mascarado
        """
        if len(data) <= visible_chars:
            return data
        return mask_char * (len(data) - visible_chars) + data[-visible_chars:]

    @staticmethod
    def validate_cpf(cpf: str) -> Tuple[bool, str]:
        """
        Valida um número de CPF brasileiro.
        
        Args:
            cpf: Número de CPF a validar
            
        Returns:
            tuple[bool, str]: (True, "OK") se válido, (False, mensagem) caso contrário
        """
        # Remove caracteres não numéricos
        cpf = re.sub(r'[^\d]', '', cpf)
        
        # Verifica tamanho e dígitos repetidos
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False, f"{Fore.RED}CPF inválido (formato incorreto).{Style.RESET_ALL}"
        
        # Cálculo do primeiro dígito verificador
        sum_ = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digit1 = (sum_ * 10) % 11
        digit1 = 0 if digit1 == 10 else digit1
        
        # Cálculo do segundo dígito verificador
        sum_ = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digit2 = (sum_ * 10) % 11
        digit2 = 0 if digit2 == 10 else digit2
        
        # Verifica dígitos calculados
        if int(cpf[9]) == digit1 and int(cpf[10]) == digit2:
            return True, f"{Fore.GREEN}CPF válido.{Style.RESET_ALL}"
        return False, f"{Fore.RED}CPF inválido (dígitos verificadores incorretos).{Style.RESET_ALL}"

    @staticmethod
    def progress_bar(
        iteration: int,
        total: int,
        prefix: str = '',
        suffix: str = '',
        length: int = 50,
        fill: str = '█',
        print_end: str = "\r"
    ) -> None:
        """
        Exibe uma barra de progresso no console.
        
        Args:
            iteration: Iteração atual
            total: Total de iterações
            prefix: Texto prefixo
            suffix: Texto sufixo
            length: Comprimento da barra
            fill: Caractere de preenchimento
            print_end: Caractere no final (default: \\r)
        """
        percent = f"{100 * (iteration / float(total)):.1f}"
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
        if iteration == total: 
            print()

    @staticmethod
    def format_long_date(date_obj: datetime) -> str:
        """
        Formata data no formato extenso (ex: "25 de Dezembro de 2023").
        
        Args:
            date_obj: Objeto datetime a formatar
            
        Returns:
            str: Data formatada
        """
        months = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        return f"{date_obj.day} de {months[date_obj.month - 1]} de {date_obj.year}"

    @staticmethod
    def calculate_age(birth_date: datetime, reference_date: datetime = None) -> int:
        """
        Calcula idade a partir da data de nascimento.
        
        Args:
            birth_date: Data de nascimento
            reference_date: Data de referência (default: hoje)
            
        Returns:
            int: Idade calculada
        """
        ref = reference_date or datetime.now()
        age = ref.year - birth_date.year
        if (ref.month, ref.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age
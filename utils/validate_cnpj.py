import re
from django.core.exceptions import ValidationError

def validate_cnpj(cnpj: str) -> None:
    """
    Valida um CNPJ.
    Levanta ValidationError se o CNPJ for inválido.
    """
    # Verifica se o CNPJ contém exatamente 14 dígitos numéricos
    if not re.match(r'^\d{14}$', cnpj):
        raise ValidationError('O CNPJ deve conter exatamente 14 números.')

    if not is_valid_cnpj(cnpj):
        raise ValidationError('O CNPJ informado é inválido.')

def is_valid_cnpj(cnpj: str) -> bool:
    """
    Implementa a validação do dígito verificador do CNPJ.
    Retorna True se o CNPJ for válido, False caso contrário.
    """
    # Verifica se todos os dígitos são iguais (CNPJs como 00000000000000 são inválidos)
    if cnpj == cnpj[0] * 14:
        return False

    def calculate_digit(cnpj_partial):
        weights = [6,5,4,3,2,9,8,7,6,5,4,3,2]
        sum_ = 0
        # Ajusta o alinhamento dos pesos para o tamanho parcial do CNPJ
        offset = len(weights) - len(cnpj_partial)
        for i, num in enumerate(cnpj_partial):
            sum_ += int(num) * weights[i + offset]
        remainder = sum_ % 11
        return '0' if remainder < 2 else str(11 - remainder)

    # Calcula o primeiro dígito verificador
    first12 = cnpj[:12]
    first_digit = calculate_digit(first12)
    if cnpj[12] != first_digit:
        return False

    # Calcula o segundo dígito verificador
    first13 = cnpj[:13]
    second_digit = calculate_digit(first13)
    if cnpj[13] != second_digit:
        return False

    return True
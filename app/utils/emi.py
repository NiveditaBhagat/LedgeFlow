from decimal import Decimal, ROUND_HALF_UP


def calculate_emi(
    principal: Decimal,
    annual_rate: float,
    tenure_months: int
) -> Decimal:
   

    # 🔒 Validations
    if principal <= 0:
        raise ValueError("Principal must be greater than 0")

    if tenure_months <= 0:
        raise ValueError("Tenure must be greater than 0")

    #  Zero interest case
    if annual_rate == 0:
        return (principal / Decimal(tenure_months)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    P = principal
    r = Decimal(str(annual_rate)) / Decimal("1200")
    n = Decimal(tenure_months)

    one_plus_r_pow_n = (Decimal("1") + r) ** n

    emi = (P * r * one_plus_r_pow_n) / (one_plus_r_pow_n - Decimal("1"))

    return emi.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
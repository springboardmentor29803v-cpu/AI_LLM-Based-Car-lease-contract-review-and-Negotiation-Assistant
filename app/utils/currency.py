import re

USD_TO_INR = 83.0


def extract_number(value):
    """
    Extract numeric part from string or number
    """
    if value is None:
        return 0

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value)

    num = re.sub(r"[^\d.]", "", value)

    try:
        return float(num)
    except:
        return 0


def to_inr(value):
    """
    Convert any amount to INR

    Rules:
    ₹ present → INR
    $ present → USD → INR
    plain number → assume USD → INR
    """

    if value is None:
        return 0

    value_str = str(value).lower()
    amount = extract_number(value_str)

    # INR symbol
    if "₹" in value_str or "inr" in value_str:
        return int(amount)

    # USD symbol
    if "$" in value_str or "usd" in value_str:
        return int(amount * USD_TO_INR)

    # ❗ Plain number → assume USD
    return int(amount * USD_TO_INR)
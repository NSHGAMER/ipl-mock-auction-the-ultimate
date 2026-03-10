def format_currency(value):
    crores = value / 1e7
    if crores.is_integer():
        return f"{int(crores)}cr"
    else:
        return f"{crores:.1f}cr"


def parse_price(txt):
    txt = txt.strip().lower()
    if txt.endswith('cr'):
        try:
            num = float(txt[:-2])
            return int(num * 1e7)
        except ValueError:
            return 0
    else:
        try:
            return int(float(txt))
        except ValueError:
            return 0

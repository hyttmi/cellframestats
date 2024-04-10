import re
import database_utils as du

def validate_input(input):
    total_supply = 30300000
    input_strip = input.strip()

    if len(input_strip) == 104 and input_strip.isalnum(): # This is probably a wallet address
        pattern = re.match(r"^R.{103}$", input_strip)
        if pattern:
            cell = du.check_cell_amount_by_wallet_addr(input_strip)
            if cell is not None:
                cell_float = float(cell) / (10 ** 18) if cell is not None else 0.0
                percentage = (cell_float / total_supply) * 100
                return {"status": "success", "message": "You have {:.5f}% of the total supply".format(percentage)}
            else:
                return {"status": "error", "message": f"Can't fetch token amount of wallet {input_strip}."}

        else:
            return {"status": "error", "message": "Invalid wallet address."}

    elif input_strip.isnumeric():
        percentage = (int(input_strip) / total_supply) * 100
        msg = "You have {:.8f}% of the total supply.".format(percentage)
        return {"status": "success", "message": msg}

    else:
        return {"status": "error", "message": "Unknown wallet or amount!"}
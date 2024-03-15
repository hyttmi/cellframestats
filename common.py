import re

def validate_input(input):
    input_strip = input.strip()
    if len(input_strip) == 104 and input_strip.isalnum(): # This is probably an wallet...
        pattern = re.match(r"^R.{103}$", input)
        if pattern:
            return {"status": "success", "message": f"NOTIMPLEMENTED"}
    elif input_strip.isnumeric():
        return {"status": "success", "message": f"NOTIMPLEMENTED"}
    else:
        return {"status": "error", "message": f"Unknown wallet or amount!"}
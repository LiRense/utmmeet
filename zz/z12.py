import z11

def gen_long_barcode():
    return str(z11.gen_number_code(3)) + str(z11.gen_number_code(3)) + str(z11.gen_number_code(8)) + str(
        z11.gen_number_code(7)) + str(z11.gen_vers(129))

print(gen_long_barcode())
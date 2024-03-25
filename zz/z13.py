import z11

class Barcode():
    def barcode_old(self):
        gen = z11.Generator()
        ves = gen.gen_vers(3)
        allcode = '00008AEKBH65N6G1'
        djob = gen.gen_djob_code()
        mark = gen.gen_number_code(6)
        kript_code = gen.gen_vers(31)
        barcode = '22N'+allcode+djob+mark+kript_code
        return barcode

    def barcode_new(self):
        gen = z11.Generator()
        return str(gen.gen_number_code(3)) + str(gen.gen_number_code(3)) + str(gen.gen_number_code(8)) + str(gen.gen_number_code(7)) + str(gen.gen_vers(129))

    def getold(self,n):
        old_barcode_list = list()
        for i in range(n):
            old_barcode_list.append(self.barcode_old())
        return old_barcode_list

    def getnew(self,n):
        new_barcode_list = list()
        for i in range(n):
            new_barcode_list.append(self.barcode_new())
        return new_barcode_list

br = Barcode()
print(br.getold(1))
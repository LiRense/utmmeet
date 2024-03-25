import inspect


class AllBarcodes():
    @staticmethod
    def old_alc_barcode():
        pass

    @staticmethod
    def new_alc_barcode(**kwargs):
        for arg in kwargs.items():
            if arg in ['types','serial','number','month','year','version','kript'] and kwargs[arg]:

        # args = inspect.getfullargspec(AllBarcodes.new_alc_barcode())
        print(kwargs)

kwargs = {'types':1,
          'serial':1,
          'number':1,
          'month':1,
          'year':1,
          'version':1,
          'kript':'1'}

AllBarcodes.new_alc_barcode(**kwargs)
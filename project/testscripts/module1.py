import json


class Product:
    def __init__(self, product_code, product_desc):
        self.product_code = product_code
        self.product_desc = product_desc
        



my_list = []

for i in range(10):
    my_list.append(Product('prod' + str(i), 'desc' + str(i)))





b = json.dumps([one.__dict__ for one in my_list])

print(b)
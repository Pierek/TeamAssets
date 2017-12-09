# project/api/model.py


class Product:

    '''Setup connection metadata in constructor'''
    def __init__(self, product_code, product_description, promo, ean, integral_code, series, category, brand, range
                 , product_description_en, category_en, box_capacity, dimension_h, dimension_w, dimension_l
                 , pallete_capacity, box_dimension_h, box_dimension_w, box_dimension_l, rep_state, rep_state_www, kgo):

        self.product_code = product_code
        self.product_description = product_description
        self.promo = promo
        self.ean = ean
        self.integral_code = integral_code
        self.series = series
        self.category = category
        self.brand = brand
        self.range = range
        self.product_description_en = product_description_en
        self.category_en = category_en
        self.box_capacity = box_capacity
        self.dimension_h = dimension_h
        self.dimension_w = dimension_w
        self.dimension_l = dimension_l
        self.pallete_capacity = pallete_capacity
        self.box_dimension_h = box_dimension_h
        self.box_dimension_w = box_dimension_w
        self.box_dimension_l = box_dimension_l
        self.rep_state = rep_state
        self.rep_state_www = rep_state_www
        self.kgo = kgo

    def print_product(self):
        return self.product_description
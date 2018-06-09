"""Parse and upload images"""
import glob
import os
import re
import sys
from math import floor
import cv2
import imutils
import numpy as np
#import PIL.ExifTags
import piexif
import pyodbc
import requests
from PIL import Image
from resizeimage import resizeimage
import json
from shutil import copy2

VERSION = 0.15
DEFAULT_DPI = 96 #72
MIN_DPI = 72
STR_SEPARATOR = "; "
LIST_SEPARATOR = "|"
CSV_SEPARATOR = ","
ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png']
FILE_UPLOAD_URL = 'https://teampolska.eu/api/product/attachment/{0}' #'http://teampolska.eu/fileupload'
EXIF_TAG_SEPARATOR = "|"
PARENT_FOLDER = r'C:\OEC\CodeBase\_teamservices.jakubas.eu\ZDJECIA INTERNET\KALORIK'
IMAGE_FOLDER = os.path.join(PARENT_FOLDER, 'unprocessed')
IMAGE_PROCESSED_FOLDER = os.path.join(PARENT_FOLDER, 'processed')
IMAGE_ERRORS_FOLDER = os.path.join(PARENT_FOLDER, 'errors')
IMAGE_THUMBNAIL_FOLDER = os.path.join(PARENT_FOLDER, 'thumbnails')

PROCESS_ERRORS = []
CREATE_THUMBNAILS = True
PROCESS_TEMPLATES = False
TEMPLATES = ['template_kalorik_h95_vertical.jpg', 'template_kalorik_w95_horizontal.jpg',
             'template_efbe_h95_vertical.jpg', 'template_efbe_w95_horizontal.jpg',
             'template_kitchen_h165_vertical.jpg', 'template_kitchen_w165_horizontal.jpg']
VISUALIZE = False
CORRELATION_TRESHOLD = 0.330 #no logo recognized below this level
#SQL_CONNECTION = pyodbc.connect('DSN=Team;Uid=team_reader;Pwd=team_reader;')
UPLOAD_FILES = True
FILENAME_FILTER = 'BL1000_offer'
THUMBNAIL_HEIGHT = 96 #72, 96, 128, 150
THUMBNAIL_FORMAT = 'PNG' #'JPEG',
PROCESS_DB_DATA = True
SQL_CONNECTION = None
SQL_CURSOR = None
TOKEN = "eyJleHAiOjE1Mjc0Nzg1ODYsImFsZyI6IkhTMjU2IiwiaWF0IjoxNTI3NDc0OTg2fQ.eyJjb25maXJtIjoyfQ.O98Lsp1VlunsZuJIhj2ODE9sfyywZY8U0EvnjGK1JOs"

def rreplace(given_string, old, new, occurrence):
    split_list = given_string.rsplit(old, occurrence)
    return new.join(split_list)

def list_to_str(lst):
    '''Creates string from string list separated using default separator'''
    list_as_string = ''
    if isinstance(lst, str) is False:
        for iterator in range(0, len(lst)):
            if iterator == 0:
                list_as_string = str(lst[iterator])
            else:
                list_as_string = list_as_string + LIST_SEPARATOR + str(lst[iterator])
    return list_as_string

class TeamImage:
    """Class to hold all Team Image data"""
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_size = os.path.getsize(self.file_path)
        self.image_folder, self.file_name = os.path.split(self.file_path)
        self.file_name_no_extension = os.path.splitext(self.file_name)[0].lower()
        self.file_extension = os.path.splitext(self.file_name)[-1].lower()
        self.temp_file_name_no_extension = ""
        self.product_code_from_file_name = ""
        self.possible_product_codes = []
        self.warnings = []
        self.errors = []
        self.products_from_db = []
        self.filename_image_sequence = -1
        self.filename_image_type = ''
        self.filename_logo_removed = False
        self.filename_is_offer = False
        self.filename_is_boxoffer = False
        self.filename_is_label = False
        self.filename_arranged = False
        self.filename_dpi = -1
        self.filename_attributes = []
        self.logo_removed = False
        self.product_code_from_db = ""
        self.exif_dpi = 0
        self.exif_image_description = ''
        self.exif_image_title = ''
        self.exif_image_subject = ''
        self.exif_image_comment = ''
        self.exif_image_keywords = ''
        self.exif_image_author = ''
        self.new_filename = ''
        self.processed_filepath = ''
        self.new_thumbnail_filename = ''
        self.thumbnail_filepath = ''

        self.get_metadata_from_image_file(self.file_path)
        self.parse_file_name()

        if len(self.metadata_image_format) > 0 and len(self.filename_image_type) > 0 and\
                self.metadata_image_format != self.filename_image_type:
            self.errors.append('FIL: File extension "{0}" and file type "{1}" do not match'\
                .format(self.filename_image_type, self.metadata_image_format))

        if PROCESS_DB_DATA is True:
            products_count = self.find_product_code_in_db(self.possible_product_codes, 1)
            if products_count == 1:
                if self.product_code_from_file_name.lower() != self.product_code_from_db.lower():
                    self.warnings.append('PCE: Product code from file does not match database product code')
                if self.product_code_from_db.find(' ') > -1:
                    self.warnings.append('PCE: Product code contain space character')
            #elif products_count > 1:
            #    if len(self.product_code_from_db) > 0:
            #        if self.product_code_from_file_name.lower() != self.product_code_from_db.lower():
            #            self.errors.append('PCE: Product code from file does not match database product code')
                #if self.find_product_code_in_db(self.possible_product_codes, 2) == 0:
                #    if self.find_product_code_in_db(self.possible_product_codes, 3) == 0:
                #        self.find_product_code_in_db(self.possible_product_codes, 4)
            elif products_count == 0: #len(self.product_code_from_db) == 0:
                self.errors.append('PCE: Product code "{0}" was not found in database'\
                    .format(self.product_code_from_file_name))

        if PROCESS_TEMPLATES:
            for template in TEMPLATES:
                correlation = 0.0
                correlation = self.image_has_template(self.file_path, template)
                #print('Correlation: {0} for template: {1}'.format(correlation, template))
                if correlation >= CORRELATION_TRESHOLD:
                    #print('Correlation: {0} for template: {1}'.format(correlation, template))
                    self.logo_removed = False
                    break
                else:
                    self.logo_removed = True
            if self.filename_logo_removed != self.logo_removed:
                self.warnings.append('LOG: Filename logo information does not match recorded image logo value')

        if self.filename_dpi > -1 and self.metadata_image_dpi != self.filename_dpi:
            self.errors.append('DPI: Image DPI: {0} does not match filename DPI: {1}'.format(self.metadata_image_dpi, self.filename_dpi))

        if self.filename_is_offer is True and self.filename_is_boxoffer is True:
            self.errors.append('FIL: There are "offer" and "boxoffer" attributes in filename which is not allowed')
        elif self.filename_is_offer is True and self.filename_arranged is True:
            self.errors.append('FIL: There are "offer" and "arr" attributes in filename which is not allowed')
        elif self.filename_is_boxoffer is True\
                and self.filename_arranged is True:
            self.errors.append('FIL: There are "boxoffer" and "arr" attributes in filename which is not allowed')

        self.new_filename = self.create_filename()[0]
        self.new_thumbnail_filename = self.create_filename()[1]
        self.processed_filepath = os.path.join(IMAGE_PROCESSED_FOLDER, self.new_filename)
        self.thumbnail_filepath = os.path.join(IMAGE_THUMBNAIL_FOLDER, self.new_thumbnail_filename)
        #os.rename(self.file_path, self.processed_filepath)
        copy2(self.file_path,self.processed_filepath)

        if CREATE_THUMBNAILS is True:
            self.create_thumbnail(self.processed_filepath, self.thumbnail_filepath)

    def create_filename(self):
        """Create file name from attributes"""
        new_filename = ''
        new_thumbnail_filename = ''
        if len(self.product_code_from_db) > 0:
            new_filename += self.product_code_from_db.upper().replace('/', '-')
        else:
            new_filename += self.product_code_from_file_name.upper()
        if self.filename_is_offer or self.filename_is_boxoffer or self.filename_arranged:
            if self.filename_is_offer:
                new_filename += '_offer'
            if self.filename_is_boxoffer:
                new_filename += '_boxoffer'
            if self.filename_arranged:
                new_filename += '_arranged'
        if PROCESS_TEMPLATES:
            if self.logo_removed:
                new_filename += '_L'
        else:
            if self.filename_logo_removed:
                new_filename += '_L'
        if self.filename_is_label:
            new_filename += '_label'
        if self.filename_dpi > 0:
            new_filename += '_DPI' + str(self.metadata_image_dpi)
        if self.filename_image_sequence > -1:
            if self.filename_image_sequence == 0:
                self.filename_image_sequence += 1
            new_filename += '_v' + str(self.filename_image_sequence).zfill(2)
        new_thumbnail_filename = new_filename
        new_thumbnail_filename += '_Th' + str(THUMBNAIL_HEIGHT)

        if self.filename_attributes:
            attributes = ''
            for iterator in range(0, len(self.filename_attributes)):
                if self.filename_attributes[iterator] is not None and len(self.filename_attributes[iterator]) > 0:
                    if iterator == 0:
                        attributes += self.filename_attributes[iterator]
                    else:
                        attributes += '-' + self.filename_attributes[iterator]
            if len(attributes) > 0:
                new_filename += '_' + attributes
                new_thumbnail_filename += '_' + attributes

        if self.filename_image_type == 'JPEG':
            new_filename += '.jpg'
        elif self.filename_image_type == 'PNG':
            new_filename += '.png'
        else:
            new_filename += self.file_extension
        
        if THUMBNAIL_FORMAT == 'JPEG':
            new_thumbnail_filename += '.jpg'
        elif THUMBNAIL_FORMAT == 'PNG':
            new_thumbnail_filename += '.png'

        return (new_filename, new_thumbnail_filename)

    def __str__(self):
        return self.file_name + STR_SEPARATOR\
            + str(self.file_size) + STR_SEPARATOR\
            + self.metadata_image_format + STR_SEPARATOR\
            + str(self.metadata_image_width)  + STR_SEPARATOR\
            + str(self.metadata_image_height) + STR_SEPARATOR\
            + str(self.metadata_image_dpi) + STR_SEPARATOR\
            + self.product_code_from_file_name + STR_SEPARATOR\
            + list_to_str(self.possible_product_codes) + STR_SEPARATOR\
            + str(self.filename_logo_removed) + STR_SEPARATOR\
            + str(self.filename_is_boxoffer) + STR_SEPARATOR\
            + str(self.filename_is_offer) + STR_SEPARATOR\
            + str(self.filename_is_label) + STR_SEPARATOR\
            + str(self.filename_arranged) + STR_SEPARATOR\
            + str(self.filename_dpi) + STR_SEPARATOR\
            + str(self.logo_removed) + STR_SEPARATOR\
            + str(self.filename_image_sequence) + STR_SEPARATOR\
            + self.product_code_from_db + STR_SEPARATOR\
            + self.new_filename + STR_SEPARATOR\
            + list_to_str(self.products_from_db) + STR_SEPARATOR\
            + list_to_str(self.warnings) + STR_SEPARATOR\
            + list_to_str(self.errors)

    def get_metadata_from_image_file(self, image_path):
        """Populate Image metadata from file"""
        try:
            image_file = Image.open(image_path)
            self.metadata_image_format = image_file.format
            self.metadata_image_width, self.metadata_image_height = image_file.size
            self.metadata_image_dpi = DEFAULT_DPI
            if image_file.info.get('dpi'):
                x_dpi, y_dpi = image_file.info['dpi']
                if x_dpi == y_dpi and x_dpi >= MIN_DPI:
                    self.metadata_image_dpi = x_dpi
                elif x_dpi == y_dpi and x_dpi > 0 and x_dpi < MIN_DPI:
                    self.errors.append('DPI: Image DPI is set too low: {0}'.format(x_dpi))
                else:
                    self.warnings.append('DPI: Metadata DPI information is not consistent [x_dpi=' + str(x_dpi)
                                         + ', y_dpi = ' + str(y_dpi) + ']. Default value will be used.')
                    if x_dpi > y_dpi and x_dpi >= DEFAULT_DPI:
                        image_file.save(image_path, dpi=(x_dpi, x_dpi))
                    elif y_dpi > x_dpi and y_dpi >= DEFAULT_DPI:
                        image_file.save(image_path, dpi=(y_dpi, y_dpi))
                    else:
                        image_file.save(image_path, dpi=(DEFAULT_DPI, DEFAULT_DPI))
            else:
                self.warnings.append('DPI: Metadata does not contain DPI information. Default value will be used.')
                image_file.save(image_path, dpi=(DEFAULT_DPI, DEFAULT_DPI))
        except Exception as ex:
            exc_type = ex.__class__.__name__
            self.errors.append("IMG: Unable to process image [" + self.file_name + "] Exception Type: " + str(exc_type) + " Error: " + str(ex))
        finally:
            if image_file is not None:
                image_file.close()

    def create_thumbnail(self, image_path, thumbnail_path):
        """Create thumbnail(s) for provided image"""
        try:
            image_file = Image.open(image_path)
            #for tile_height in THUMBNAIL_HEIGHT:
            #    for tile_format in THUMBNAIL_FORMAT:
            thumbnail = resizeimage.resize_height(image_file, THUMBNAIL_HEIGHT)
            thumbnail.save(thumbnail_path)
        except Exception as ex:
            exc_type = ex.__class__.__name__
            self.errors.append("IMG: Unable to create thumbnail image [" + self.file_name
                               + "] Exception Type: " + str(exc_type) + " Error: " + str(ex))
        finally:
            if image_file is not None:
                image_file.close()

    def parse_file_name(self):
        """Get image attrubutes from file name"""
        self.temp_file_name_no_extension = self.file_name_no_extension
        if self.temp_file_name_no_extension.find('box_back_offer') > -1:
            self.temp_file_name_no_extension = \
                self.temp_file_name_no_extension.replace('box_back_offer', '_boxoffer_') #_boxbackoffer_
        elif self.temp_file_name_no_extension.find('box_front_offer') > -1:
            self.temp_file_name_no_extension = self.temp_file_name_no_extension.replace('box_front_offer', '_boxoffer_')#_boxfrontoffer_
        elif self.temp_file_name_no_extension.find('box_offer') > -1:
            self.temp_file_name_no_extension = self.temp_file_name_no_extension.replace('box_offer', '_boxoffer_')
        elif self.temp_file_name_no_extension.find('box') > -1:
            self.errors.append('FIL: File attribute "box" is not allowed.')
            #self.temp_file_name_no_extension = self.temp_file_name_no_extension.replace('box', '_boxoffer_')

        if self.file_extension == '.png':
            self.filename_image_type = 'PNG'
        elif self.file_extension == '.jpg' or self.file_extension == '.jpeg':
            self.filename_image_type = 'JPEG'
        #elif self.file_extension == '.gif':
        #    self.filename_image_type = 'GIF'
        else:
            self.errors.append('EXT: File extension "{0}" is not suported.'.format(self.file_extension))

        image_name_splitted = self.temp_file_name_no_extension.split('_')
        self.product_code_from_file_name = image_name_splitted[0].upper()

        #self.possible_product_codes.append(self.product_code_from_file_name)
        #if(self.product_code_from_file_name.find('-') > -1):
        #    self.possible_product_codes.append(rreplace(self.product_code_from_file_name, '-', '/', 1))
        self.possible_product_codes = self.get_all_possible_product_codes(self.product_code_from_file_name)

        image_name_splitted.remove(image_name_splitted[0])
        for part in image_name_splitted:
            part = part.strip()
            part = part.replace('copy', '')
            part = part.replace('app', '')
            #part = part.replace('arr', '')
            part = part.replace('ar', 'arr')
            part = part.replace('kopia', '')
            part = part.replace(' - ', '')
            part = part.replace('(1)', '')
            part = part.replace('(2)', '')
            part = part.replace('(3)', '')
            part = part.replace('old', '01')
            #part = part.replace('etap', '')
            part = part.strip()
            if len(part) > 0:
                processed_attribute = False
                if part == 'l' or part == 'll':
                    self.filename_logo_removed = True
                    processed_attribute = True
                elif part == 'boxoffer':  #get info about box offer
                    self.filename_is_boxoffer = True
                    processed_attribute = True
                elif part == 'offer':
                    self.filename_is_offer = True
                    processed_attribute = True
                elif part == 'offerl':
                    self.filename_is_offer = True
                    self.filename_logo_removed = True
                    processed_attribute = True
                elif part == 'label':
                    self.filename_is_label = True
                    processed_attribute = True
                elif part == 'arr':
                    self.filename_arranged = True
                    processed_attribute = True
                elif (len(part) == 1 and re.match(r'[0-9]', part)) \
                    or (len(part) == 2 and re.match(r'[0-9][0-9]', part)): #integer
                    self.filename_image_sequence = int(part)
                    processed_attribute = True
                elif (len(part) == 2 and re.match(r'[0-9]l', part)) \
                    or (len(part) == 3 and re.match(r'[0-9][0-9]l', part)) \
                    or (len(part) == 3 and re.match(r'[0-9]-l', part)) \
                    or (len(part) == 4 and re.match(r'[0-9][0-9]-l', part)):
                    self.filename_logo_removed = True
                    self.filename_image_sequence = int(part.replace('l', '').replace('-', ''))
                    processed_attribute = True
                elif part.find('dpi') > -1:
                    dpi = part.replace('dpi', '')
                    if (len(dpi) == 2 and re.match(r'[0-9][0-9]', dpi)) \
                        or (len(dpi) == 3 and re.match(r'[0-9][0-9][0-9]', dpi)) \
                        or (len(dpi) == 4 and re.match(r'[0-9][0-9][0-9][0-9]', dpi)):
                        self.filename_dpi = int(dpi)
                        processed_attribute = True
                elif (len(part) == 2 and re.match(r'[0-9]a', part)) \
                    or (len(part) == 3 and re.match(r'[0-9][0-9]a', part)):
                    self.filename_image_sequence = int(part.replace('a', ''))
                    processed_attribute = True
                elif len(part) == 3 and re.match(r'v[0-9][0-9]', part):
                    self.filename_image_sequence = int(part.replace('v', ''))
                    processed_attribute = True

                if not processed_attribute:
                    self.filename_attributes.append(part)
                    #self.warnings.append('ATR: Attribute ' + part + ' was not processed')
        return

    def get_all_possible_product_codes(self, product_code):
        """Tries to guess similar product codes"""
        split_char = '-'
        possible_product_codes = list()
        possible_product_codes.append(product_code)
        if product_code.find('-') > -1:
            possible_product_codes.append(rreplace(product_code, '-', '/', 1))

        product_code_splitted = product_code.split(split_char)
        code_chunks = len(product_code_splitted)
        if code_chunks > 0:
            last_chunk = product_code_splitted[code_chunks - 1]
            if (len(last_chunk) == 1 and re.match(r'[0-9]', last_chunk)) \
                or (len(last_chunk) == 2 and re.match(r'[0-9][0-9]', last_chunk)):
                new_code = ''
                new_code_short = ''
                for x in range(0, code_chunks):
                    if len(product_code_splitted[x].strip()) > 0:
                        if x == 0:
                            new_code = product_code_splitted[x]
                        elif x > 0 and x < code_chunks - 1:
                            new_code = new_code + '-' + product_code_splitted[x]
                        else:
                            new_code_short = new_code
                            new_code = new_code + '/' + product_code_splitted[x]
                possible_product_codes.append(new_code)
                if len(new_code_short) > 0:
                    possible_product_codes.append(new_code_short)

        #KALORIK
        possible_product_codes_2 = list()
        for code in possible_product_codes:
            if code.find('-KALORIK') > -1:
                possible_product_codes_2.append(code.replace('-KALORIK', ''))
            else:
                possible_product_codes_2.append(code + '-KALORIK')

        for code_2 in possible_product_codes_2:
            possible_product_codes.append(code_2)

        product_code_splitted_space = product_code.split(' ')
        if len(product_code_splitted_space) > 1 and len(product_code_splitted_space[0]) >= 4:
            possible_product_codes.append(product_code_splitted_space[0])
            if product_code_splitted_space[0].find('-KALORIK') > -1:
                possible_product_codes.append(code.replace('-KALORIK', ''))
            else:
                possible_product_codes.append(code + '-KALORIK')

        #SCHOTT
        possible_product_schott1 = list()
        for code_schott1 in possible_product_codes:
            if code_schott1.find('-SCHOTT') > -1:
                possible_product_schott1.append(code_schott1.replace('-SCHOTT', ''))
            else:
                possible_product_schott1.append(code_schott1 + '-SCHOTT')

        for code_schott in possible_product_schott1:
            possible_product_codes.append(code_schott)

        product_code_splitted_space_shott = product_code.split(' ')
        if len(product_code_splitted_space_shott) > 1 and len(product_code_splitted_space_shott[0]) >= 4:
            possible_product_codes.append(product_code_splitted_space_shott[0])
            if product_code_splitted_space_shott[0].find('-SCHOTT') > -1:
                possible_product_codes.append(code.replace('-SCHOTT', ''))
            else:
                possible_product_codes.append(code + '-SCHOTT')

        #add all codes
        possible_product_codes = list(set(possible_product_codes))
        possible_product_codes.sort(key=len, reverse=True)
        return possible_product_codes

    def find_product_code_in_db(self, product_codes, strict_level):
        rowcount = 0
        for product_code in product_codes:
            product_code_for_like = product_code.replace("'", "''").replace("%", "[%]").replace("_", "[_]")
            sql = "SELECT [ID],[Guid],[Kod],[Nazwa],[NumerKatalogowy] FROM [TEAM].[dbo].[Towary] WHERE Kod LIKE '" + product_code_for_like + "%'"
            if strict_level == 1:
                sql = "SELECT [ID],[Guid],[Kod],[Nazwa],[NumerKatalogowy] FROM [TEAM].[dbo].[Towary] WHERE Kod = '" + product_code.replace("'", "''") + "'"
            elif strict_level == 2:
                sql = "SELECT [ID],[Guid],[Kod],[Nazwa],[NumerKatalogowy] FROM [TEAM].[dbo].[Towary] WHERE Kod LIKE '" + product_code_for_like + "%'"
            elif strict_level == 3:
                sql = "SELECT [ID],[Guid],[Kod],[Nazwa],[NumerKatalogowy] FROM [TEAM].[dbo].[Towary] WHERE Kod LIKE '%" + product_code_for_like + "%'"
            elif strict_level == 4:
                sql = "SELECT [ID],[Guid],[Kod],[Nazwa],[NumerKatalogowy] FROM [TEAM].[dbo].[Towary] WHERE REPLACE(Kod,'/','-') LIKE '%" + product_code_for_like + "%'"

            SQL_CURSOR.execute(sql)
            row = SQL_CURSOR.fetchone()
            while row:
                rowcount = rowcount + 1
                if rowcount == 1:
                    self.product_code_from_db = row[2].lower().encode('utf-8', 'ignore').decode(sys.stdout.encoding)
                try:
                    self.products_from_db.append(
                        str(row[0])+'~"' + row[1]+'"~"'
                        + row[2].lower().encode('utf-8', 'ignore').decode(sys.stdout.encoding).replace('"', '""')+'"~"'\
                        + row[3].lower().encode('utf-8', 'ignore').decode(sys.stdout.encoding).replace('"', '""')+'"~"'\
                        + row[4].lower().encode('utf-8', 'ignore').decode(sys.stdout.encoding).replace('"', '""')+'"')
                except UnicodeDecodeError as ex:
                    exc_type = ex.__class__.__name__
                    print('ID: ' + str(row[0]) + ' Exception Type: ' + exc_type)
                #title.encode('utf-8', 'ignore').decode(sys.stdout.encoding)
                #title = title.encode('utf8').decode('utf8')
                #break
                row = SQL_CURSOR.fetchone()
            if rowcount > 1:
                self.errors.append('SQL: More than one [' + str(rowcount) + '] product returned for the code: [' + product_code + ']')
            '''
            if rowcount >= 4:
                self.product_code_from_db = ''
                self.products_from_db.clear()
                self.errors.append('SQL: Too many records [' + str(rowcount) + '] returned for the code: [' + product_code + ']')
            '''
        return rowcount

    def image_has_template(self, image_path, template_path):
        has_template = False

        # load the image image, convert it to grayscale, and detect edges
        template = cv2.imread(template_path)
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        template = cv2.Canny(template, 50, 200)
        (tH, tW) = template.shape[:2]
        #cv2.imshow("Template", template)

        # load the image, convert it to grayscale, and initialize the
        # bookkeeping variable to keep track of the matched region
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        found = (0, (0, 0), 0)

        # loop over the scales of the image
        for scale in np.linspace(0.01, 1.0, 200)[::-1]:
            # resize the image according to the scale, and keep track
            # of the ratio of the resizing
            resized = imutils.resize(gray, width=int(gray.shape[1] * scale))
            r = gray.shape[1] / float(resized.shape[1])

            # if the resized image is smaller than the template, then break
            # from the loop
            if resized.shape[0] < tH or resized.shape[1] < tW:
                break

            # detect edges in the resized, grayscale image and apply template
            # matching to find the template in the image
            edged = cv2.Canny(resized, 50, 200)
            result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF_NORMED)
            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

            # check to see if the iteration should be visualized
            if VISUALIZE:
                # draw a bounding box around the detected region
                clone = np.dstack([edged, edged, edged])
                cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
                              (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
                cv2.imshow("Visualize", clone)
                cv2.waitKey(0)

            # if we have found a new maximum correlation value, then ipdate
            # the bookkeeping variable
            if found is None or maxVal > found[0]:
                found = (maxVal, maxLoc, r)
            #print(found[0], maxVal)
        # unpack the bookkeeping varaible and compute the (x, y) coordinates
        # of the bounding box based on the resized ratio
        if found is not None:
            (_, maxLoc, r) = found
            (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
            (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

            # draw a bounding box around the detected result and display the image
            #cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
            #cv2.imshow("Image", image)
            if found[0] >= CORRELATION_TRESHOLD:
                has_template = True
                #print(found[0])
        #else:
        #    print(found = [0])
        #return has_template
        return found[0]
#End of TeamImage class

def get_column_descriptions():
    return 'file_name' + STR_SEPARATOR\
        + 'file_size' + STR_SEPARATOR\
        + 'metadata_image_format' + STR_SEPARATOR\
        + 'metadata_image_width'  + STR_SEPARATOR\
        + 'metadata_image_height' + STR_SEPARATOR\
        + 'metadata_image_dpi' + STR_SEPARATOR\
        + 'product_code_from_file_name' + STR_SEPARATOR\
        + 'possible_product_codes' + STR_SEPARATOR\
        + 'filename_logo_removed' + STR_SEPARATOR\
        + 'filename_is_box_offer' + STR_SEPARATOR\
        + 'filename_is_offer' + STR_SEPARATOR\
        + 'filename_is_label' + STR_SEPARATOR\
        + 'filename_arranged' + STR_SEPARATOR\
        + 'filename_dpi' + STR_SEPARATOR\
        + 'logo_removed' + STR_SEPARATOR\
        + 'filename_image_sequence' + STR_SEPARATOR\
        + 'product_code_from_db' + STR_SEPARATOR\
        + 'new_filename' + STR_SEPARATOR\
        + 'products' + STR_SEPARATOR\
        + 'warnings' + STR_SEPARATOR\
        + 'errors'

def exif_str_2_tuple(input_string):
    converted_list = list()
    for char in input_string:
        char2int = ord(char)
        if char2int < 256:
            converted_list.append(char2int)
            converted_list.append(0)
        else:
            converted_list.append(char2int%256)
            converted_list.append(floor(char2int/256))
    converted_list.append(0)
    converted_list.append(0)
    return tuple(converted_list)

def exif_tuple_2_str(input_tuple):
    output_string = ''
    for ix in range(0, len(input_tuple)):
        if ix % 2 == 0:
            lo_byte = input_tuple[ix]
            hi_byte = input_tuple[ix + 1]#this is risky in case tuple has not even number of values
            if lo_byte > 0 or hi_byte > 0:
                output_string = output_string + chr(hi_byte * 256 + lo_byte)
                #ix = ix + 1
    return output_string

def find_product_in_db(product_id):
    SQL = "SELECT [ID],[Guid],[Kod],[Nazwa],[NumerKatalogowy] FROM [TEAM].[dbo].[Towary] WHERE Kod LIKE '" + product_id + "%'"
    product_db_id = ''
    cursor.execute(SQL)
    row = cursor.fetchone()
    if row:
        print(row)
    return product_db_id

def process_exif(image_path):
    image_file = Image.open(image_path)
    #exif_data = image_file._getexif()
    #print(exif_data)
    #print(ord(u'ą'))
    '''
    exif_dict = piexif.load(image_path)
    for ifd in ("0th", "Exif", "GPS", "1st"):
        for tag in exif_dict[ifd]:
            print(ifd, piexif.TAGS[ifd][tag]["name"], exif_dict[ifd][tag])
    '''
    '''
    exif = {
        PIL.ExifTags.TAGS[k]: v
        for k, v in image_file._getexif().items()
        if k in PIL.ExifTags.TAGS
        }
    '''
    if image_file.info.get('exif'):
        exif_dict = piexif.load(image_file.info["exif"])
        if exif_dict.get('0th'):
            if exif_dict["0th"].get(piexif.ImageIFD.XResolution):
                x_dpi, flag = exif_dict["0th"][piexif.ImageIFD.XResolution]
                #print('EXIF_XResolution: ' + str(x_dpi))
            if exif_dict["0th"].get(piexif.ImageIFD.YResolution):
                y_dpi, flag = exif_dict["0th"][piexif.ImageIFD.YResolution]
                #print('EXIF_YResolution: ' + str(y_dpi))
            #ImageDescription and XPTitle are the same when saved on Windows explorer
            if exif_dict["0th"].get(piexif.ImageIFD.ImageDescription):
                img_desc = exif_dict["0th"][piexif.ImageIFD.ImageDescription]
                #print('ImageDescription: ' + img_desc.decode('UTF-8'))
            if exif_dict["0th"].get(piexif.ImageIFD.XPTitle):
                XPTitle = exif_dict["0th"][piexif.ImageIFD.XPTitle]
                #print('XPTitle: ' + exif_tuple_2_str(XPTitle))
            if exif_dict["0th"].get(piexif.ImageIFD.XPSubject):
                XPSubject = exif_dict["0th"][piexif.ImageIFD.XPSubject]
                #print('XPSubject: ' + exif_tuple_2_str(XPSubject))
            if exif_dict["0th"].get(piexif.ImageIFD.XPComment):
                XPComment = exif_dict["0th"][piexif.ImageIFD.XPComment]
                #print('XPComment: ' + exif_tuple_2_str(XPComment))
            if exif_dict["0th"].get(piexif.ImageIFD.XPKeywords):
                XPKeywords = exif_dict["0th"][piexif.ImageIFD.XPKeywords]
                #print('XPKeywords: ' + exif_tuple_2_str(XPKeywords))
            if exif_dict["0th"].get(piexif.ImageIFD.XPAuthor):
                XPAuthor = exif_dict["0th"][piexif.ImageIFD.XPAuthor]
                #print('XPAuthor: ' + exif_tuple_2_str(XPAuthor))

    # process im and exif_dict...
    #exif_dict["0th"][piexif.ImageIFD.XResolution] = (width, 1)
    #exif_dict["0th"][piexif.ImageIFD.YResolution] = (height, 1)
    '''
    exif_dict["0th"][piexif.ImageIFD.XResolution] = 
    exif_dict["0th"][piexif.ImageIFD.YResolution] = 
    exif_dict["0th"][piexif.ImageIFD.ImageDescription] = 'test-title-ąćń'.encode('UTF-8')
    exif_dict["0th"][piexif.ImageIFD.XPSubject] = exif_str_2_tuple(u'xpsubject-ąćń-שלום עולם')
    exif_dict["0th"][piexif.ImageIFD.XPComment] = exif_str_2_tuple(u'xpcomment')
    exif_dict["0th"][piexif.ImageIFD.XPKeywords] = exif_str_2_tuple(u'xpkeywords')
    exif_dict["0th"][piexif.ImageIFD.XPAuthor] = exif_str_2_tuple(u'https://services.teampolska.eu/')
    exif_dict["0th"][piexif.ImageIFD.XPTitle] = exif_str_2_tuple(u'xptitle')
    exif_bytes = piexif.dump(exif_dict)
    image_file.save(os.path.join(folder_name, '1-SP2-KALORIK-test.jpg'), "jpeg", exif=exif_bytes)
    '''
    #print(PIL.ExifTags.TAGS)
    #print(image_file._getexif().items())
    #image_file.save()
    image_file.close()

def is_image_path_valid():
    if not os.path.isdir(PARENT_FOLDER):
        PROCESS_ERRORS.append('DIR: Parent folder: "{0}" does not exists'.format(PARENT_FOLDER))
    if not os.path.isdir(IMAGE_FOLDER):
        PROCESS_ERRORS.append('DIR: Unprocessed images folder: "{0}" does not exists'.format(IMAGE_FOLDER))
    if not os.path.isdir(IMAGE_PROCESSED_FOLDER):
        PROCESS_ERRORS.append('DIR: Processed images folder: "{0}" does not exists'.format(IMAGE_PROCESSED_FOLDER))
    if not os.path.isdir(IMAGE_ERRORS_FOLDER):
        PROCESS_ERRORS.append('DIR: Error images folder: "{0}" does not exists'.format(IMAGE_ERRORS_FOLDER))
    if len(os.listdir(PARENT_FOLDER)) != 3:
        PROCESS_ERRORS.append('DIR: Parent folder: "{0}" contains other files or folders'.format(PARENT_FOLDER))
    if PROCESS_ERRORS:
        return False
    else:
        return True

#==========SCRIPT========
#check paths are ok
#is_image_path_valid()

if PROCESS_DB_DATA is True:
    try:
        SQL_CONNECTION = pyodbc.connect('Driver={SQL Server Native Client 11.0};'
                                        + 'Server=localhost;Database=TEAM;Uid=team_reader;Pwd=team_reader;')
    except Exception as ex:
        PROCESS_ERRORS.append('SQL: Unable to connect to database server. Error: {0}'.format(repr(ex)))

if PROCESS_ERRORS:
    for error in PROCESS_ERRORS:
        print(error)
    exit(1)

#print('All good. We are ready to rumble')
#exit(0)

if SQL_CONNECTION is not None:
    SQL_CURSOR = SQL_CONNECTION.cursor()
print(get_column_descriptions())
#onlyfiles = [f for f in listdir(IMAGE_FOLDER) if isfile(join(IMAGE_FOLDER, f))]
onlyfiles = os.listdir(IMAGE_FOLDER)
for filename in onlyfiles:
    if os.path.isfile(os.path.join(IMAGE_FOLDER, filename)):
        if os.path.splitext(filename)[-1].lower() in ALLOWED_EXTENSIONS\
            and (filename.find(FILENAME_FILTER) >= 0\
            or len(FILENAME_FILTER.strip()) == 0):#startswith<->find >= 0
            team_image = None
            try:
                #print(filename, end=';')
                team_image = TeamImage(os.path.join(IMAGE_FOLDER, filename))
                print(team_image)
                #process_exif(os.path.join(IMAGE_FOLDER, filename))
            except UnicodeEncodeError as ex:
                exc_type = ex.__class__.__name__
                print('FILE: ' + filename + ' Exception Type: ' + exc_type)
            except Exception as ex1:
                exc_type = ex1.__class__.__name__
                print('FILE: ' + filename + ' Exception Type: '\
                        + exc_type + ' Message: ' + repr(ex1))

            #process_image(IMAGE_FOLDER, filename)
            
            if UPLOAD_FILES:
                url = "https://teampolska.eu/api/product/attachment/{0}".format(team_image.new_filename)
                #url = "https://teampolska.eu/api/product/attachment/BL1000-KALORIK_boxoffer.jpg"
                fin = open(team_image.processed_filepath, 'rb')
                files = {'product_image': fin}
                token='eyJleHAiOjE1Mjc2MzAwOTMsImFsZyI6IkhTMjU2IiwiaWF0IjoxNTI3NjI2NDkzfQ.eyJjb25maXJtIjoyfQ.QQmU0ol5kpgJZyxWG1-bI0Pjb9Ad1AcowwCkv7VZVZw'
                try:
                    r = requests.put(url, headers={'Token' : token}, files=files)
                    print(r.text)
                except Exception as ex:
                    print('Message: ' + repr(ex))
                finally:
                    fin.close()
                '''
                img_file = {'product_image': open(team_image.processed_filepath, 'rb')}
                r = requests.put(URL + team_image.new_filename, headers={'Token' : TOKEN}, files=img_file)
                print(r.text)
                '''
                tile_file = {'product_image': open(team_image.thumbnail_filepath, 'rb')}
                r = requests.put(FILE_UPLOAD_URL.format(team_image.new_thumbnail_filename), headers={'Token' : token}, files=tile_file)
                print(r.status_code)
                
    if os.path.isdir(os.path.join(IMAGE_FOLDER, filename)):
        pass#print(IMAGE_FOLDER + filename + '\\')

if SQL_CONNECTION is not None:
    SQL_CURSOR.close()
    SQL_CONNECTION.close()

'''
import requests
fin = open(filepath, 'rb')
files = {'product_image': fin}
try:
    r = requests.put(url, headers={'Token' : token}, files=files)
    print(r.text)
finally:
 fin.close()
 '''

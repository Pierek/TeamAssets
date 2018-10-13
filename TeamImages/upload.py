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
from datetime import datetime
import json
import logging
import argparse
from shutil import copy2, move
sys.path.append(r'..\project\api')
from request import token_refresh

'''
TO DO:
-Do not move files to processed folder before image upload (in case of failure)
-Add more command line arguments
-Add config file
-More advanced SQL search - including manufacture check
-Keep templates in separate folder
-Web requests in dedicated method
-Merge TeamImages with TeamAssets
-Add try/catch to SQL calls
-Refactoring
-Reuse token and refresh only after unsuccesull call
'''

VERSION = 0.24
DEFAULT_DPI = 96
MIN_DPI = 72
STR_SEPARATOR = "; "
LIST_SEPARATOR = "|"
CSV_SEPARATOR = ","
EXIF_TAG_SEPARATOR = "|"
ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png']
APP_URL = os.getenv('APP_SETTINGS_URL')
PARENT_FOLDER = os.getenv('APP_IMAGE_FOLDER')
FILE_UPLOAD_ENDPOINT = 'api/product/attachment/'
UPLOAD_FILES = True

IMAGE_UNPROCESSED_FOLDER = os.path.join(PARENT_FOLDER, 'unprocessed')
IMAGE_PROCESSED_FOLDER = os.path.join(PARENT_FOLDER, 'processed')
IMAGE_ERROR_FOLDER = os.path.join(PARENT_FOLDER, 'errors')
IMAGE_THUMBNAIL_FOLDER = os.path.join(PARENT_FOLDER, 'thumbnails')
IMAGE_LOG_FOLDER = os.path.join(PARENT_FOLDER, 'logs')
IMAGE_CURRENT_ERROR_FOLDER = None

PROCESS_TEMPLATES = True
CORRELATION_TRESHOLD = 0.330 #no logo recognized below this level
TEMPLATES = ['template_kalorik_h95_vertical.jpg', 'template_kalorik_w95_horizontal.jpg',
             'template_efbe_h95_vertical.jpg', 'template_efbe_w95_horizontal.jpg',
             'template_kitchen_h165_vertical.jpg', 'template_kitchen_w165_horizontal.jpg']
VISUALIZE = False

FILENAME_FILTER = '' #will process only files containing this string - case sensitive
CREATE_THUMBNAILS = True
THUMBNAIL_HEIGHT = 96
THUMBNAIL_FORMAT = 'PNG'

SQL_CONNECTION_STRING_TEMPLATE = 'Driver=%SQL_DRIVER%;Server=%SQL_SERVER%;Database=%SQL_DATABASE%;Uid=%SQL_LOGIN%;Pwd=%SQL_PASSWORD%;'
SQL_CONNECTION = None
SQL_CURSOR = None

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
    def __init__(self, file_path, process_id):
        self.file_path = file_path
        self.process_id = process_id
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

        logging.debug('*** CHECK DB DATA ***')
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

        logging.debug('*** PROCESS TEMPLATES ***')
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

        logging.debug('*** DPI CHECK ***')
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

        if self.errors == 0:
            if os.path.isfile(self.processed_filepath):
                logging.warning("File: '{0}' already exists in 'processed' folder: '{1}' and will be replace with newer version with the same name".format(self.new_filename, IMAGE_PROCESSED_FOLDER))
                #self.errors.append("File: '{0}' already exists in folder: '{1}'".format(self.new_filename, IMAGE_PROCESSED_FOLDER))
            try:
                os.rename(self.file_path, self.processed_filepath)
                #copy2(self.file_path,self.processed_filepath)
            except Exception as ex:
                self.errors.append("Unable to move file: '{0}' to folder: '{1}'. Message: {2}".format(self.file_path, IMAGE_PROCESSED_FOLDER, repr(ex)))

            logging.debug('*** CREATE THUMBNAILS ***')
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
                if x_dpi != round(x_dpi) or y_dpi != round(y_dpi):
                    self.warnings.append("DPI: Image file has DPI as floating point number: x={0}, y={1}. It will be converted to integer: x={2}, y={3}".format(x_dpi, y_dpi, round(x_dpi), round(y_dpi)))
                    x_dpi = int(round(x_dpi))
                    y_dpi = int(round(y_dpi))
                    image_file.save(image_path, dpi=(x_dpi, y_dpi))
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
        image_file = None
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
                pass # we no longer have to close this file
                #image_file.close()

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
            sql = ""
            #sql = "SELECT [product_id],[product_code],[product_description] FROM [data].[product]"
            #sql = "SELECT [ID],[Guid],[Kod],[Nazwa],[NumerKatalogowy] FROM [TEAM].[dbo].[Towary] WHERE Kod LIKE '" + product_code_for_like + "%'"
            if strict_level == 1:
                sql = "SELECT [product_id],[product_code],[product_description] FROM [data].[product] WHERE [product_code] = '" + product_code.replace("'", "''") + "'"
            elif strict_level == 2:
                sql = "SELECT [product_id],[product_code],[product_description] FROM [data].[product] WHERE [product_code] LIKE '" + product_code_for_like + "%'"
            elif strict_level == 3:
                sql = "SELECT [product_id],[product_code],[product_description] FROM [data].[product] WHERE [product_code] LIKE '%" + product_code_for_like + "%'"
            elif strict_level == 4:
                sql = "SELECT [product_id],[product_code],[product_description] FROM [data].[product] WHERE REPLACE([product_code],'/','-') LIKE '%" + product_code_for_like + "%'"

            SQL_CURSOR.execute(sql)
            row = SQL_CURSOR.fetchone()
            while row:
                rowcount = rowcount + 1
                if rowcount == 1:
                    self.product_code_from_db = row[1].lower().encode('utf-8', 'ignore').decode(sys.stdout.encoding)
                try:
                    self.products_from_db.append(
                        str(row[0])+'~"' + row[1]+'"~"'
                        + row[2].lower().encode('utf-8', 'ignore').decode(sys.stdout.encoding).replace('"', '""')+'"')
                except UnicodeDecodeError as ex:
                    logging.error("Error occured while converting product description with code: '{0}'. Error description: '{1}'".format(row[1], repr(ex)))
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

def check_folder_structure(process_id):
    folders_ok = True
    if not os.path.exists(PARENT_FOLDER):
        logging.error("Image directory does not exists: '{0}'".format(PARENT_FOLDER))
        folders_ok = False
    else:
        if not os.path.isdir(PARENT_FOLDER):
            logging.error("Image directory path: '{0}' is not valid.".format(PARENT_FOLDER))
            folders_ok = False

    if folders_ok:
        try:
            if not os.path.isdir(IMAGE_ERROR_FOLDER):
                os.makedirs(IMAGE_ERROR_FOLDER)
            if not os.path.isdir(IMAGE_CURRENT_ERROR_FOLDER):    
                os.makedirs(IMAGE_CURRENT_ERROR_FOLDER)
            if not os.path.isdir(IMAGE_UNPROCESSED_ERROR_FOLDER): 
                os.makedirs(IMAGE_UNPROCESSED_ERROR_FOLDER)
            if not os.path.isdir(IMAGE_LOG_FOLDER):
                os.makedirs(IMAGE_LOG_FOLDER)
            if not os.path.isdir(IMAGE_PROCESSED_FOLDER):
                os.makedirs(IMAGE_PROCESSED_FOLDER)
            if not os.path.isdir(IMAGE_THUMBNAIL_FOLDER):
                os.makedirs(IMAGE_THUMBNAIL_FOLDER)
            if not os.path.isdir(IMAGE_UNPROCESSED_FOLDER):
                os.makedirs(IMAGE_UNPROCESSED_FOLDER)
        except Exception as ex:
            logging.error("Exception occured while creating flder structure. Error description: '{0}'".format(repr(ex)))
            folders_ok = False
    
    if folders_ok:
        #move all items from parent to unprocessed/errors folder
        for filename in os.listdir(PARENT_FOLDER):
            try:
                if os.path.join(PARENT_FOLDER, filename) not in [IMAGE_ERROR_FOLDER, IMAGE_LOG_FOLDER, IMAGE_PROCESSED_FOLDER, IMAGE_THUMBNAIL_FOLDER, IMAGE_UNPROCESSED_FOLDER]:
                    if os.path.isfile(os.path.join(PARENT_FOLDER, filename)):
                        if os.path.splitext(filename)[-1].lower() in ALLOWED_EXTENSIONS:
                            if os.path.isfile(os.path.join(IMAGE_UNPROCESSED_FOLDER, filename)):
                                move(os.path.join(PARENT_FOLDER, filename), os.path.join(IMAGE_CURRENT_ERROR_FOLDER, filename))
                                logging.warning("File: '{0}' already exists in unprocessed folder and has been moved to destination '{1}'. Object will not be processed.".format(os.path.join(PARENT_FOLDER, filename), os.path.join(IMAGE_CURRENT_ERROR_FOLDER, filename)))
                            else:
                                move(os.path.join(PARENT_FOLDER, filename), os.path.join(IMAGE_UNPROCESSED_FOLDER, filename))
                                logging.info("File: '{0}' was moved to location '{1}'".format(os.path.join(PARENT_FOLDER, filename), os.path.join(IMAGE_UNPROCESSED_FOLDER, filename)))
                        else:
                            move(os.path.join(PARENT_FOLDER, filename), os.path.join(IMAGE_CURRENT_ERROR_FOLDER, filename))
                            logging.warning("File: '{0}' has not allowed extension: '{1}' and has been moved to destination '{2}'. Object will not be processed.".format(os.path.join(PARENT_FOLDER, filename), os.path.splitext(filename)[-1].lower(), os.path.join(IMAGE_CURRENT_ERROR_FOLDER, filename)))
                    elif os.path.isdir(os.path.join(PARENT_FOLDER, filename)):
                        move(os.path.join(PARENT_FOLDER, filename), os.path.join(IMAGE_CURRENT_ERROR_FOLDER, filename))
                        logging.warning("Item: '{0}' is a directory, which is not expected in this location and it was moved to destination: '{1}'. Object will not be processed.".format(os.path.join(PARENT_FOLDER, filename), os.path.join(IMAGE_CURRENT_ERROR_FOLDER, filename)))
            except PermissionError as ex:
                logging.error("Unable to move item: '{0}' to destination location. Item is opened in another process or current user does not have permission to move it. System error description: '{1}'".format(os.path.join(PARENT_FOLDER, filename), repr(ex)))
                folders_ok = False
            except Exception as ex:
                logging.error("Exception occured while moving object: '{0}'. System error description: '{1}'".format(os.path.join(PARENT_FOLDER, filename), repr(ex)))
                folders_ok = False
            except:
                logging.error("Unspecified error occured while moving object: '{0}'").format(os.path.join(PARENT_FOLDER, filename))
                folders_ok = False
    return folders_ok

#========================================================= SCRIPT =========================================================#
process_id = datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f") #get process timestamp/id
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-ll", "--loglevel", choices=['debug', 'info', 'warning', 'error', 'critical'],\
                        required=False, help="Information type captured in log file") #default='warning',
arg_parser.add_argument("-ff", "--filenamefilter", default='', required=False,\
                        help="Only files containing this value will be processed (case sensitive)")
args = vars(arg_parser.parse_args())

loglevel = logging.WARNING
gettrace = getattr(sys, 'gettrace', None)
if gettrace():
    loglevel = logging.DEBUG

if args["loglevel"] == "debug":
    loglevel = logging.DEBUG
elif args["loglevel"] == "info":
    loglevel = logging.INFO
elif args["loglevel"] == "warning":
    loglevel = logging.WARNING
elif args["loglevel"] == "error":
    loglevel = logging.ERROR
elif args["loglevel"] == "critical":
    loglevel = logging.CRITICAL

FILENAME_FILTER = args["filenamefilter"]

logging.basicConfig(handlers=[logging.FileHandler(filename=os.path.join(IMAGE_LOG_FOLDER, process_id + '.log'), encoding='utf-8')], \
                    format='%(asctime)s:%(levelname)s:%(message)s', level=loglevel) #, level=logging.INFO - default is WARNING
logging.info("TeamImage process [{0}] version: '{1}'".format(process_id, VERSION))
IMAGE_CURRENT_ERROR_FOLDER = os.path.join(IMAGE_ERROR_FOLDER, process_id)
IMAGE_UNPROCESSED_ERROR_FOLDER = os.path.join(IMAGE_CURRENT_ERROR_FOLDER, IMAGE_UNPROCESSED_FOLDER.rsplit('\\', 1)[1])

if check_folder_structure(process_id) == False:
    logging.critical("Error occured while validating folder structure inside directory: '{0}'".format(PARENT_FOLDER))
    exit(1)

sql_driver = ""
if sys.platform == "linux" or sys.platform == "linux2":
    sql_driver = "{SQL Server}"
elif sys.platform == "win32" or sys.platform == "win64":
    sql_driver = "{SQL Server Native Client 11.0}"
else:
    logging.critical("Unsupported system type: '{0}'".format(sys.platform))
    exit(1)

ConnectionString = SQL_CONNECTION_STRING_TEMPLATE.replace('%SQL_SERVER%', os.getenv('APP_SETTINGS_TEAM_SERVER'))
ConnectionString = ConnectionString.replace('%SQL_DRIVER%', sql_driver)
ConnectionString = ConnectionString.replace('%SQL_DATABASE%', os.getenv('APP_SETTINGS_TEAM_DATABASE'))
ConnectionString = ConnectionString.replace('%SQL_LOGIN%', os.getenv('APP_SETTINGS_TEAM_USER'))
ConnectionString = ConnectionString.replace('%SQL_PASSWORD%', os.getenv('APP_SETTINGS_TEAM_PWD'))
try:
    SQL_CONNECTION = pyodbc.connect(ConnectionString)
    logging.info("Connected to server: '{0}'".format(os.getenv('APP_SETTINGS_TEAM_SERVER')))
except Exception as ex:
    logging.critical("Unable to connect to database server: '{0}'. Error: {1}".format(os.getenv('APP_SETTINGS_TEAM_SERVER'), repr(ex)))
    exit(1)

if SQL_CONNECTION is not None:
    SQL_CURSOR = SQL_CONNECTION.cursor()
#print(get_column_descriptions())
#onlyfiles = [f for f in listdir(IMAGE_FOLDER) if isfile(join(IMAGE_FOLDER, f))]
if len(FILENAME_FILTER) > 0:
    logging.warning("File name filter is applied for this run: '{0}'".format(FILENAME_FILTER))

onlyfiles = os.listdir(IMAGE_UNPROCESSED_FOLDER)
for filename in onlyfiles:
    if os.path.isfile(os.path.join(IMAGE_UNPROCESSED_FOLDER, filename)):
        if os.path.splitext(filename)[-1].lower() in ALLOWED_EXTENSIONS:
            if filename.find(FILENAME_FILTER) >= 0 or len(FILENAME_FILTER.strip()) == 0:
                team_image = None
                try:
                    logging.info("Processing file: '{0}'".format(os.path.join(IMAGE_UNPROCESSED_FOLDER, filename)))
                    team_image = TeamImage(os.path.join(IMAGE_UNPROCESSED_FOLDER, filename), process_id)
                    logging.info(team_image)
                    #process_exif(os.path.join(IMAGE_FOLDER, filename))
                except UnicodeEncodeError as ex:
                    logging.error("UnicodeEncodeError captured while processing file: '{0}' Message: {1}".format(os.path.join(IMAGE_UNPROCESSED_FOLDER, filename), repr(ex)))
                except Exception as ex:
                    logging.error("Exception captured while processing file: '{0}' Message: {1}".format(os.path.join(IMAGE_UNPROCESSED_FOLDER, filename), repr(ex)))

                if UPLOAD_FILES == False:
                    logging.warning("Process is set NOT to upload images. UPLOAD_FILES variable is expected to be True.")
                elif team_image is None:
                    logging.error("File: '{0}' was not processed correctly.".format(os.path.join(IMAGE_UNPROCESSED_FOLDER, filename)))
                elif team_image.product_code_from_db is None or len(team_image.product_code_from_db) == 0:
                    logging.error("File: '{0}' was processed but product code was not found in data set".format(os.path.join(IMAGE_UNPROCESSED_FOLDER, filename)))
                elif len(team_image.errors) > 0:
                    logging.error("File: '{0}' was processed with errors: '{1}'".format(os.path.join(IMAGE_UNPROCESSED_FOLDER, filename), list_to_str(team_image.errors)))
                else:
                    #send post with metadata
                    list_of_items = []
                    file_data = {}
                    tile_data = {}
                    items = {}

                    #file_data
                    file_data["product_code"] = team_image.product_code_from_db.upper()
                    file_data["file_name"] = team_image.new_filename
                    file_data["tile_file_name"] = team_image.new_thumbnail_filename
                    file_data["file_size"] = str(os.path.getsize(team_image.processed_filepath))
                    if team_image.filename_image_type == 'JPEG':
                        file_data["mime"] = "jpg"
                    elif team_image.filename_image_type == 'PNG':
                        file_data["mime"] = "png"
                    file_data["width"] = team_image.metadata_image_width
                    file_data["height"] = team_image.metadata_image_height
                    if team_image.filename_is_offer:
                        file_data["category"] = 'offer'
                    elif team_image.filename_is_boxoffer:
                        file_data["category"] = 'boxoffer'
                    elif team_image.filename_arranged:
                        file_data["category"] = 'arranged'
                    else:
                        file_data["category"] = 'undefined'
                    if team_image.logo_removed:
                        file_data["no_logo"] = "Y"
                    else:
                        file_data["no_logo"] = "N"
                    if team_image.filename_is_label:
                        file_data["label"] = "Y"
                    else:
                        file_data["label"] = "N"
                    file_data["DPI"] = str(team_image.metadata_image_dpi)
                    file_data["version"] = str(team_image.filename_image_sequence)
                    if team_image.filename_attributes:
                        attributes = ''
                        for iterator in range(0, len(team_image.filename_attributes)):
                            if team_image.filename_attributes[iterator] is not None and len(team_image.filename_attributes[iterator]) > 0:
                                if iterator == 0:
                                    attributes += team_image.filename_attributes[iterator]
                                else:
                                    attributes += '-' + team_image.filename_attributes[iterator]
                        if len(attributes) > 0:
                            file_data["atributes"] = attributes
                        else:
                            file_data["atributes"] = ""
                    list_of_items.append(file_data)
                    #tile_data
                    tile_data["product_code"] = team_image.product_code_from_db.upper()
                    tile_data["file_name"] = team_image.new_thumbnail_filename
                    tile_data["tile_file_name"] = ""
                    tile_data["file_size"] = str(os.path.getsize(team_image.thumbnail_filepath))
                    tile_data["mime"] = "png"
                    tile_data["width"] = int(team_image.metadata_image_width * (THUMBNAIL_HEIGHT/team_image.metadata_image_height))
                    tile_data["height"] = THUMBNAIL_HEIGHT
                    tile_data["category"] = 'tile'
                    if team_image.logo_removed:
                        tile_data["no_logo"] = "Y"
                    else:
                        tile_data["no_logo"] = "N"
                    if team_image.filename_is_label:
                        tile_data["label"] = "Y"
                    else:
                        tile_data["label"] = "N"
                    tile_data["DPI"] = str(team_image.metadata_image_dpi)
                    tile_data["version"] = str(team_image.filename_image_sequence)
                    if team_image.filename_attributes:
                        attributes = ''
                        for iterator in range(0, len(team_image.filename_attributes)):
                            if team_image.filename_attributes[iterator] is not None and len(team_image.filename_attributes[iterator]) > 0:
                                if iterator == 0:
                                    attributes += team_image.filename_attributes[iterator]
                                else:
                                    attributes += '-' + team_image.filename_attributes[iterator]
                        if len(attributes) > 0:
                            tile_data["atributes"] = attributes
                        else:
                            tile_data["atributes"] = ""
                    list_of_items.append(tile_data)
                    
                    items['items'] = list_of_items
                    json_data = json.dumps(items)

                    token = token_refresh()
                    headers = {"Token": token, "Content-Type": "application/json"}
                    file_exists_on_server = False
                    url_get = APP_URL + FILE_UPLOAD_ENDPOINT + team_image.new_filename
                    try:
                        r = requests.get(url_get, headers=headers, data=json_data)
                        logging.debug("Response code: {0}".format(r.status_code))
                        logging.debug("Response body: {0}".format(r.text).replace("\r", "<CR>").replace("\n","<LF>"))
                        if r.status_code >= 200 and r.status_code < 300:
                            file_exists_on_server = True
                            response_dict = json.loads(r.text)
                            logging.info("File: '{0}' already exists on server".format(team_image.new_filename))
                        else:
                            logging.error("Status code: '{0}' was returned while checking file's data: {1} on server".format(r.status_code, team_image.new_filename))
                            continue
                    except requests.exceptions.RequestException as re:
                        logging.error("RequestException was captured while checking file's: '{0}' metadata on server. Message {1}".format(team_image.new_filename, repr(re)))
                        continue
                    except Exception as ex:
                        logging.error("Exception was captured while checking file's: '{0}' metadata on server. Message {1}".format(team_image.new_filename, repr(ex)))
                        continue

                    if not file_exists_on_server:
                        url_post_meta = APP_URL + FILE_UPLOAD_ENDPOINT
                        try:
                            r = requests.post(url_post_meta, headers=headers, data=json_data)
                            logging.debug("Response code: {0}".format(r.status_code))
                            logging.debug("Response body: {0}".format(r.text).replace("\r", "<CR>").replace("\n", "<LF>"))
                            if r.status_code >= 200 and r.status_code < 300:
                                response_dict = json.loads(r.text)
                                if response_dict[0].get("status") == "200" and response_dict[1].get("status") == "200":
                                    logging.info("Metadata for file: '{0}' and thumbnail '{1}' was uploaded successfully".format(team_image.new_filename, team_image.new_thumbnail_filename))
                                else:
                                    logging.error("Server has processed request but status codes: {0}/{1} were returned while processing metadata for file: '{2}' and thumbnail: '{3}'".format(response_dict[0].get("status"), response_dict[1].get("status"), team_image.new_filename, team_image.new_thumbnail_filename))
                                    continue
                            else:
                                logging.error("Status code: '{0}' was returned while sending metadata to server".format(r.status_code))
                                continue
                        except requests.exceptions.RequestException as re:
                            logging.error("RequestException was captured while sending file's: '{0}' metadata to server. Message {1}".format(team_image.new_filename, repr(re)))
                            continue
                        except Exception as ex:
                            logging.error("Exception was captured while sending file's: '{0}' metadata to server. Message {1}".format(team_image.new_filename, repr(ex)))
                            continue
                    else:
                        url_put_meta = APP_URL + FILE_UPLOAD_ENDPOINT
                        try:
                            r = requests.put(url_put_meta, headers=headers, data=json_data)
                            logging.debug("Response code: {0}".format(r.status_code))
                            logging.debug("Response body: {0}".format(r.text).replace("\r", "<CR>").replace("\n", "<LF>"))
                            if r.status_code >= 200 and r.status_code < 300:
                                response_dict = json.loads(r.text)
                                if response_dict[0].get("status") == "200" and response_dict[1].get("status") == "200":
                                    logging.info("Metadata for file: '{0}' and thumbnail '{1}' was uploaded successfully".format(team_image.new_filename, team_image.new_thumbnail_filename))
                                else:
                                    logging.error("Server has processed request but status codes: {0}/{1} were returned while processing metadata for file: '{2}' and thumbnail: '{3}'".format(response_dict[0].get("status"), response_dict[1].get("status"), team_image.new_filename, team_image.new_thumbnail_filename))
                                    continue
                            else:
                                logging.error("Status code: '{0}' was returned while sending metadata to server".format(r.status_code))
                                continue
                        except requests.exceptions.RequestException as re:
                            logging.error("RequestException was captured while sending file's: '{0}' metadata to server. Message {1}".format(team_image.new_filename, repr(re)))
                            continue
                        except Exception as ex:
                            logging.error("Exception was captured while sending file's: '{0}' metadata to server. Message {1}".format(team_image.new_filename, repr(ex)))
                            continue

                    url_put_file = APP_URL + FILE_UPLOAD_ENDPOINT + 'image/' + team_image.new_filename
                    fin = open(team_image.processed_filepath, 'rb')
                    files = {'product_image': fin}
                    try:
                        r = requests.put(url_put_file, headers={'Token' : token}, files=files)
                        if r.status_code >= 200 and r.status_code < 300:
                            response_dict = json.loads(r.text)
                            if response_dict.get("status") == "200":
                                logging.info("Image file: '{0}' was uploaded successfully".format(team_image.new_filename))
                            else:
                                logging.error("Server has processed request but status code: {0} was returned while processing image file: '{1}'".format(response_dict.get("status"), team_image.new_thumbnail_filename))
                                continue
                        else:
                            logging.error("Status code: '{0}' was returned while uploading file: '{1}' to server.".format(r.status_code, team_image.new_filename))
                            continue
                    except requests.exceptions.RequestException as re:
                        logging.error("RequestException was captured while uploading image file: '{0}' to server. Message {1}".format(team_image.new_filename, repr(re)))
                        continue
                    except Exception as ex:
                        logging.error("Exception was captured while uploading image file: '{0}' to server. Message {1}".format(team_image.new_filename, repr(ex)))
                        continue
                    finally:
                        fin.close()

                    tile_file = None
                    try:
                        url_put_thumbnail = APP_URL + FILE_UPLOAD_ENDPOINT + 'image/' + team_image.new_thumbnail_filename
                        tile_file = open(team_image.thumbnail_filepath, 'rb')
                        files = {'product_image': tile_file}
                        r = requests.put(url_put_thumbnail, headers={'Token' : token}, files=files)
                        if r.status_code >= 200 and r.status_code < 300:
                            response_dict = json.loads(r.text)
                            if response_dict.get("status") == "200":
                                logging.info("Thumbnail file: '{0}' was uploaded successfully".format(team_image.new_thumbnail_filename))
                            else:
                                logging.error("Server has processed request but status code: {0} was returned while processing tile file: '{1}'".format(response_dict.get("status"), team_image.new_thumbnail_filename))
                                continue
                        else:
                            logging.error("Status code: '{0}' was returned while uploading tile file: '{1}' to server".format(r.status_code, team_image.new_thumbnail_filename))
                            continue
                    except requests.exceptions.RequestException as re:
                        logging.error("RequestException was captured while uploading tile file: '{0}' to server. Message {1}".format(team_image.new_thumbnail_filename, repr(re)))
                        continue
                    except Exception as ex:
                        logging.error("Exception was captured while uploading tile file: '{0}' to server. Message {1}".format(team_image.new_thumbnail_filename, repr(ex)))
                        continue
                    finally:
                        tile_file.close()
        else:
            move(os.path.join(IMAGE_UNPROCESSED_FOLDER, filename), os.path.join(IMAGE_UNPROCESSED_ERROR_FOLDER, filename))
            logging.warning("File: '{0}' has not allowed extension: '{1}' and has been moved to destination '{2}'. Object will not be processed.".format(os.path.join(IMAGE_UNPROCESSED_FOLDER, filename), os.path.splitext(filename)[-1].lower(), os.path.join(IMAGE_UNPROCESSED_ERROR_FOLDER, filename)))
    if os.path.isdir(os.path.join(IMAGE_UNPROCESSED_FOLDER, filename)):
        logging.warning("Item: '{0}' is a directory, which is not expected in this location and it was moved to destination: '{1}'. Object will not be processed.".format(os.path.join(IMAGE_UNPROCESSED_FOLDER, filename), os.path.join(IMAGE_UNPROCESSED_ERROR_FOLDER, filename)))
        move(os.path.join(IMAGE_UNPROCESSED_FOLDER, filename), os.path.join(IMAGE_UNPROCESSED_ERROR_FOLDER, filename))

if SQL_CONNECTION is not None:
    if SQL_CURSOR is not None:
        SQL_CURSOR.close()
    SQL_CONNECTION.close()

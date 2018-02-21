"""Parse and upload images"""
import os
import sys
from math import floor
import re
import glob
import requests
import pyodbc
from PIL import Image
#import PIL.ExifTags
import piexif
import numpy as np
import imutils
import cv2

DEFAULT_DPI = 96 #72
STR_SEPARATOR = "; "
LIST_SEPARATOR = "|"
CSV_SEPARATOR = ","
ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png']#, '.gif'
URL = 'http://192.168.0.51:5000/fileupload'
EXIF_TAG_SEPARATOR = "|"
IMAGE_FOLDER = r'C:\! D\jakubas.eu_team\ZDJECIA INTERNET\KALORIK'
#IMAGE_FOLDER = r'C:\! D\jakubas.eu_team\ZDJECIA INTERNET\template_test'
TEMPLATES = ['template_kalorik_h95_vertical.jpg', 'template_kalorik_w95_horizontal.jpg',
             'template_efbe_h95_vertical.jpg', 'template_efbe_w95_horizontal.jpg',
             'template_kitchen_h165_vertical.jpg', 'template_kitchen_w165_horizontal.jpg']
VISUALIZE = False
CORRELATION_TRESHOLD = 0.30
SQL_CONNECTION = pyodbc.connect('Driver={SQL Server Native Client 11.0};'
                                +'Server=localhost;Database=TEAM;Uid=team_reader;Pwd=team_reader;')
#SQL_CONNECTION = pyodbc.connect('DSN=Team;Uid=team_reader;Pwd=team_reader;')
UPLOAD_FILES = 0
FILENAME_FILTER = '' #SP2#TO1008AG#A#Schott Typ 836

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
        self.filename_is_box_offer = False
        self.filename_is_box_front_offer = False
        self.filename_is_box_back_offer = False
        self.filename_older_version = False
        self.filename_is_label = False
        self.filename_arranged = False
        self.filename_dpi = -1
        self.logo_removed = False
        self.product_code_from_db = ""
        self.exif_dpi = 0
        self.exif_image_description = ''
        self.exif_image_title = ''
        self.exif_image_subject = ''
        self.exif_image_comment = ''
        self.exif_image_keywords = ''
        self.exif_image_author = ''

        self.get_metadata_from_image_file(self.file_path)
        self.parse_file_name()
        if self.find_product_code_in_db(self.possible_product_codes, 1) == 0:
            if self.find_product_code_in_db(self.possible_product_codes, 2) == 0:
                if self.find_product_code_in_db(self.possible_product_codes, 3) == 0:
                    self.find_product_code_in_db(self.possible_product_codes, 4)

        for template in TEMPLATES:
            correlation = 0.0
            correlation = self.image_has_template(self.file_path, template)
            if correlation >= CORRELATION_TRESHOLD:
                self.logo_removed = False
                break
            else:
                self.logo_removed = True

        if len(self.product_code_from_db) > 0:
            if self.product_code_from_file_name.lower() != self.product_code_from_db.lower():
                self.warnings.append('PCE: Product code from file does not match database product code')
        elif len(self.product_code_from_db) == 0:
            self.errors.append('PCE: Product code was not determined')

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
            + str(self.filename_is_box_offer) + STR_SEPARATOR\
            + str(self.filename_is_box_front_offer) + STR_SEPARATOR\
            + str(self.filename_is_box_back_offer) + STR_SEPARATOR\
            + str(self.filename_older_version) + STR_SEPARATOR\
            + str(self.filename_is_offer) + STR_SEPARATOR\
            + str(self.filename_is_label) + STR_SEPARATOR\
            + str(self.filename_arranged) + STR_SEPARATOR\
            + str(self.filename_dpi) + STR_SEPARATOR\
            + str(self.logo_removed) + STR_SEPARATOR\
            + str(self.filename_image_sequence) + STR_SEPARATOR\
            + self.product_code_from_db + STR_SEPARATOR\
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
                if x_dpi == y_dpi and x_dpi > 0:
                    self.metadata_image_dpi = x_dpi
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
            image_file.close()

    def parse_file_name(self):
        """Get image attrubutes from file name"""
        self.temp_file_name_no_extension = self.file_name_no_extension
        if self.temp_file_name_no_extension.find('box_back_offer') > -1:
            self.temp_file_name_no_extension = \
                self.temp_file_name_no_extension.replace('box_back_offer', '_boxbackoffer_')
        elif self.temp_file_name_no_extension.find('box_front_offer') > -1:
            self.temp_file_name_no_extension = self.temp_file_name_no_extension.replace('box_front_offer', '_boxfrontoffer_')
        elif self.temp_file_name_no_extension.find('box_offer') > -1:
            self.temp_file_name_no_extension = self.temp_file_name_no_extension.replace('box_offer', '_boxoffer_')
        elif self.temp_file_name_no_extension.find('box') > -1:
            self.temp_file_name_no_extension = self.temp_file_name_no_extension.replace('box', '_boxoffer_')

        if self.file_extension == '.png':
            self.filename_image_type = 'PNG'
        elif self.file_extension == '.jpg' or self.file_extension == '.jpeg':
            self.filename_image_type = 'JPEG'
        elif self.file_extension == '.gif':
            self.filename_image_type = 'GIF'
        else:
            self.errors.append('EXT: File extension is not suported.')

        image_name_splitted = self.temp_file_name_no_extension.split('_')
        self.product_code_from_file_name = image_name_splitted[0].upper()
        self.possible_product_codes = self.get_all_possible_product_codes(self.product_code_from_file_name)

        image_name_splitted.remove(image_name_splitted[0])
        for part in image_name_splitted:
            part = part.strip()
            part = part.replace('copy', '')
            part = part.replace('app', '')
            #part = part.replace('arr', '')
            part = part.replace('ar', '')
            part = part.replace('kopia', '')
            part = part.replace(' - ', '')
            part = part.replace('(1)', '')
            part = part.replace('(2)', '')
            part = part.replace('(3)', '')
            part = part.replace('etap', '')
            part = part.strip()
            if len(part) > 0:
                processed_attribute = False
                if part == 'l' or part == 'll':
                    self.filename_logo_removed = True
                    processed_attribute = True
                elif part == 'boxoffer':  #get info about box offer
                    self.filename_is_box_offer = True
                    processed_attribute = True
                elif part == 'boxfrontoffer':
                    self.filename_is_box_front_offer = True
                    processed_attribute = True
                elif part == 'boxbackoffer':
                    self.filename_is_box_back_offer = True
                    processed_attribute = True
                elif part == 'old':
                    self.filename_older_version = True
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
                elif part =='arr':
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

                if not processed_attribute:
                    self.warnings.append('ATR: Attribute ' + part + ' was not processed')
        return

    def get_all_possible_product_codes(self, product_code):
        """Tries to guess similar product codes"""
        split_char = '-'
        possible_product_codes = list()
        possible_product_codes.append(product_code)
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
        
        possible_product_codes = list(set(possible_product_codes))
        possible_product_codes.sort(reverse=True)
        return possible_product_codes

    def find_product_code_in_db(self, product_codes, strict_level):
        rowcount = 0
        for product_code in product_codes:
            product_code_for_like = product_code.replace("'","''").replace("%", "[%]").replace("_", "[_]")
            sql = "SELECT [ID],[Guid],[Kod],[Nazwa],[NumerKatalogowy] FROM [TEAM].[dbo].[Towary] WHERE Kod LIKE '" + product_code_for_like + "%'"
            if strict_level == 1:
                sql = "SELECT [ID],[Guid],[Kod],[Nazwa],[NumerKatalogowy] FROM [TEAM].[dbo].[Towary] WHERE Kod = '" + product_code.replace("'","''") + "'"
            elif strict_level == 2:
                sql = "SELECT [ID],[Guid],[Kod],[Nazwa],[NumerKatalogowy] FROM [TEAM].[dbo].[Towary] WHERE Kod LIKE '" + product_code_for_like + "%'"
            elif strict_level == 3:
                sql = "SELECT [ID],[Guid],[Kod],[Nazwa],[NumerKatalogowy] FROM [TEAM].[dbo].[Towary] WHERE Kod LIKE '%" + product_code_for_like + "%'"
            elif strict_level == 4:
                sql = "SELECT [ID],[Guid],[Kod],[Nazwa],[NumerKatalogowy] FROM [TEAM].[dbo].[Towary] WHERE REPLACE(Kod,'/','-') LIKE '%" + product_code_for_like + "%'"
            
            cursor.execute(sql)
            row = cursor.fetchone()
            while row:
                rowcount = rowcount + 1
                if rowcount == 1:
                    self.product_code_from_db = row[2].lower().encode('utf-8', 'ignore').decode(sys.stdout.encoding)
                try:
                    self.products_from_db.append(str(row[0])+'~"'\
                        + row[1]+'"~"'
                        + row[2].lower().encode('utf-8', 'ignore').decode(sys.stdout.encoding).replace('"', '""')+'"~"'\
                        + row[3].lower().encode('utf-8', 'ignore').decode(sys.stdout.encoding).replace('"', '""')+'"~"'\
                        + row[4].lower().encode('utf-8', 'ignore').decode(sys.stdout.encoding).replace('"', '""')+'"')
                except UnicodeDecodeError as ex:
                    exc_type = ex.__class__.__name__
                    print('ID: ' + str(row[0]) + ' Exception Type: ' + exc_type)
                #title.encode('utf-8', 'ignore').decode(sys.stdout.encoding)
                #title = title.encode('utf8').decode('utf8')
                #break
                row = cursor.fetchone()
            if rowcount > 1 and rowcount < 4:
                self.warnings.append('SQL: More than one [' + str(rowcount) + '] product returned for the code: [' + product_code + ']')
            if rowcount >= 4:
                self.product_code_from_db = ''
                self.products_from_db.clear()
                self.errors.append('SQL: Too many records [' + str(rowcount) + '] returned for the code: [' + product_code + ']')
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
        for scale in np.linspace(0.01, 1.0, 100)[::-1]:
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
        + 'filename_is_box_front_offer' + STR_SEPARATOR\
        + 'filename_is_box_back_offer' + STR_SEPARATOR\
        + 'filename_older_version' + STR_SEPARATOR\
        + 'filename_is_offer' + STR_SEPARATOR\
        + 'filename_is_label' + STR_SEPARATOR\
        + 'filename_arranged' + STR_SEPARATOR\
        + 'filename_dpi' + STR_SEPARATOR\
        + 'logo_removed' + STR_SEPARATOR\
        + 'filename_image_sequence' + STR_SEPARATOR\
        + 'product_code_from_db' + STR_SEPARATOR\
        + 'products' + STR_SEPARATOR\
        + 'warnings' + STR_SEPARATOR\
        + 'errors'

def exif_str_2_tuple(input_string):
    converted_list = list()
    for char in input_string:
        char2int = ord(char)
        if(char2int < 256):
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

cursor = SQL_CONNECTION.cursor()
print(get_column_descriptions())
#onlyfiles = [f for f in listdir(IMAGE_FOLDER) if isfile(join(IMAGE_FOLDER, f))]
onlyfiles = os.listdir(IMAGE_FOLDER)
for filename in onlyfiles:
    if os.path.isfile(os.path.join(IMAGE_FOLDER, filename)):
        if os.path.splitext(filename)[-1].lower() in ALLOWED_EXTENSIONS\
            and (filename.find(FILENAME_FILTER) >= 0 or len(FILENAME_FILTER.strip()) == 0):
            try:
                #print(filename)
                team_image = TeamImage(os.path.join(IMAGE_FOLDER, filename))
                print(team_image)
                #process_exif(os.path.join(IMAGE_FOLDER, filename))
            except UnicodeEncodeError as ex:
                exc_type = ex.__class__.__name__
                print('FILE: ' + team_image.file_name + ' Exception Type: ' + exc_type)

            #process_image(IMAGE_FOLDER, filename)
            if UPLOAD_FILES:
                files = {'file': open(os.path.join(IMAGE_FOLDER, filename), 'rb')}
                r = requests.post(URL, files=files)
                print(r.text)
    if os.path.isdir(os.path.join(IMAGE_FOLDER, filename)):
        pass#print(IMAGE_FOLDER + filename + '\\')

cursor.close()
SQL_CONNECTION.close()

#Legacy functions
def process_image(folder_name, file_name):
    "Get image data and attributes"
    product_name = ''
    image_sequence = -1
    image_type = ''
    logo_removed = False
    is_offer = False
    is_box_offer = False
    is_box_front_offer = False
    is_box_back_offer = False
    older_version = False
    is_label = False
    file_name_dpi = -1
    image_dpi = -1

    file_name_no_ext = os.path.splitext(file_name)[0].lower()
    
    #if file_name_no_ext.find('box') > -1 and file_name_no_ext.find('box_offer') == -1:
    #    print('we have box but not box_offer?')

    if file_name_no_ext.find('box_back_offer') > -1:
        file_name_no_ext = file_name_no_ext.replace('box_back_offer', 'boxbackoffer_')
    elif file_name_no_ext.find('box_front_offer') > -1:
        file_name_no_ext = file_name_no_ext.replace('box_front_offer', 'boxfrontoffer_')
    elif file_name_no_ext.find('box_offer') > -1:
        file_name_no_ext = file_name_no_ext.replace('box_offer', 'boxoffer_')
    elif file_name_no_ext.find('box') > -1:
        file_name_no_ext = file_name_no_ext.replace('box', 'boxoffer_')

    image_name_splitted = file_name_no_ext.split('_')
    #get product name
    product_name = image_name_splitted[0].upper()
    #if product_name.startswith('1-') or product_name.startswith('2-'):
    #    product_name = product_name[2:]
    print('=================== ' + file_name + ' ===================')
    print('Filename: ' + file_name + '; Product code: ' + product_name)
    find_product_in_db(product_name)
    #find_product_code_in_db(get_all_possible_product_codes(product_name))

    image_name_splitted.remove(image_name_splitted[0])
    #print('SPLITTED:' + str(image_name_splitted))
    for part in image_name_splitted:
        part = part.strip()
        part = part.replace('copy','')
        part = part.replace('app','')
        part = part.replace('arr','')
        part = part.replace('ar','')
        part = part.replace('kopia','')
        part = part.replace(' - ','')
        part = part.replace('(1)','')
        part = part.replace('(2)','')
        part = part.replace('(3)','')
        part = part.replace('etap','')
        part = part.strip()
        if len(part) > 0:
            processed_attribute = False
            if part == 'l' or part == 'll':
                logo_removed = True
                processed_attribute = True
            elif part == 'boxoffer':  #get info about box offer
                is_box_offer = True
                processed_attribute = True
            elif part == 'boxfrontoffer':
                is_box_front_offer = True
                processed_attribute = True
            elif part == 'boxbackoffer':
                is_box_back_offer = True
                processed_attribute = True
            elif part == 'old':
                older_version = True
                processed_attribute = True
            elif part == 'offer':
                is_offer = True
                processed_attribute = True
            elif part == 'offerl':
                is_offer = True
                logo_removed = True
                processed_attribute = True
            elif part == 'label':
                is_label = True
                processed_attribute = True
            elif (len(part) == 1 and re.match(r'[0-9]', part)) \
                or (len(part) == 2 and re.match(r'[0-9][0-9]', part)): #integer
                #print('FOUND INT:' + part)
                image_sequence = int(part)
                processed_attribute = True
            elif (len(part) == 2 and re.match(r'[0-9]l', part)) \
                or (len(part) == 3 and re.match(r'[0-9][0-9]l', part)) \
                or (len(part) == 3 and re.match(r'[0-9]-l', part)) \
                or (len(part) == 4 and re.match(r'[0-9][0-9]-l', part)):
                logo_removed = True
                image_sequence = int(part.replace('l', '').replace('-', ''))
                processed_attribute = True
            elif part.find('dpi') > -1:
                dpi = part.replace('dpi', '')
                if (len(dpi) == 2 and re.match(r'[0-9][0-9]', dpi)) \
                    or (len(dpi) == 3 and re.match(r'[0-9][0-9][0-9]', dpi)) \
                    or (len(dpi) == 4 and re.match(r'[0-9][0-9][0-9][0-9]', dpi)):
                    file_name_dpi = int(dpi)
                    processed_attribute = True
            elif (len(part) == 2 and re.match(r'[0-9]a', part)) \
                or (len(part) == 3 and re.match(r'[0-9][0-9]a', part)):
                image_sequence = int(part.replace('a', ''))
                processed_attribute = True

            if not processed_attribute:
                print('=== Attribute: "' + part + '" was not processed ===')
    
    print('product_name: ' + product_name + '; filename_logo_removed: ' + str(logo_removed) \
        + '; is_box_offer: ' + str(is_box_offer) + '; is_box_front_offer: ' + str(is_box_front_offer) \
        + '; is_box_back_offer: ' + str(is_box_back_offer) + '; older_version: ' + str(older_version) \
        + '; is_offer: ' + str(is_offer) + '; is_label: ' + str(is_label) \
        + '; file_name_dpi: ' + str(file_name_dpi) + '; image_dpi: ' + str(image_dpi) \
        + '; logo_removed: ' + str(logo_removed) + '; image_sequence: ' + str(image_sequence))
    return
def find_product_code_in_db(product_codes):
    for product_code in product_codes:
        SQL = "SELECT [ID],[Guid],[Kod],[Nazwa],[NumerKatalogowy] FROM [TEAM].[dbo].[Towary] WHERE Kod LIKE '" + product_code.replace("'","") + "%'"   #
        cursor.execute(SQL)
        row = cursor.fetchone()
        if row:
            #print(row)
            print(str(row[0])+'|"'\
                +row[1]+'"|"'+row[2]+'"|"'\
                +row[3].encode('utf-8', 'ignore').decode(sys.stdout.encoding).replace('"', '""')\
                +'"|"'\
                +row[4].replace('"', '""')+'"')
            #title.encode('utf-8', 'ignore').decode(sys.stdout.encoding)
            #title = title.encode('utf8').decode('utf8')
            break
    return
def older_function_for_templates():
    for imagePath in glob.glob(IMAGE_FOLDER + "/*.jpg"):
        max_correlation = 0.0
        max_correlation_template = ''
        image_with_logo = False
        for template in TEMPLATES:
            correlation = 0.0
            correlation = image_has_template(imagePath, template)
            if correlation > max_correlation:
                max_correlation = correlation
                max_correlation_template = template
            if correlation >= CORRELATION_TRESHOLD:
                image_with_logo = True
                break
        print(os.path.basename(imagePath), image_with_logo, max_correlation, max_correlation_template)

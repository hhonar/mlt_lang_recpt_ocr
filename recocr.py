import easyocr
import os
import cv2
import re
import base64
import numpy as np
from price_parser import Price
from PIL import Image
from io import BytesIO
from dateutil.parser import parse, ParserError
from datetime import datetime
from price_parser import Price
import pytesseract
from decimal import *
import argostranslate.package
import argostranslate.translate
import pathlib


####    Translation
def translate_text(text,from_lang,to_lang, package_path):
    response = []
    argostranslate.package.install_from_path(package_path)
    # Create a new Translator instance with the downloaded model
    translatedText  = argostranslate.translate.translate(text, from_lang, to_lang)
    return translatedText

##################################   FR  OCR  ##########################################

def frOCR(image_base64, HH_id, language,path):
    
    # note: the language could be set to 'fr'
    # install argostranlate into the path
    argostranslate.package.install_from_path(path)
    # decode received image base 64
    image_64_decode = base64.b64decode(image_base64)
    # set the language using easyocr
    reader = easyocr.Reader([language]) 
    result = reader.readtext(image_64_decode, detail=1)
    nparr = np.frombuffer(image_64_decode, np.uint8)
    # using cv2 for image shape, and leverage coordinates and bounding box
    im = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    h,w,c = im.shape

    # capture the prices leveraging coordinates by thresholding [on generic receipts threshold is set]
    for i in range(len(result)):
        if result[i][0][0][0] > 0.75*w:
            cv2.rectangle(im, (int(result[i][0][0][0]),int(result[i][0][0][1])), (int(result[i][0][2][0]), int(result[i][0][2][1])), (36, 255, 12) , 1)
    price_indx = []
    item_price = []
    item = []
    itm_tr = []
    itm_pr = []

    # price parsing
    for i in range(len(result)):
#        # to do the price parsing
        price = Price.fromstring(result[i][-2])
        # leveraing regex
        if result[i][0][0][0] > int(0.7*w):
                if re.findall(r"\s*total\s*|\s*cb auto\s*$", result[i-1][-2], re.IGNORECASE) != []:
                    break
                if re.findall("^[\s*a-zA-Z]",result[i-1][-2]) != []:
                    item_price.append(price.amount)
                    item.append(result[i-1][-2])
    tot_idx = i
    items = []

    # translating item descriptions
    for i in range(len(item)):
        items.append({"item_name": item[i].lower(),"en_item_name": argostranslate.translate.translate(item[i].lower(),'fr','en'), "item_price":item_price[i], "item_quantity": 1, "item_currency": "USD", "total_price": item_price[i]})

    # Capturing date
    date = []
    for i in range(len(result)):
        try:
            date.append(parse(result[i][-2]).date())
        except (ParserError, OverflowError):
            date.append( [])

    def get_first_none_empty(lst):
            non_empty_list = [element for element in lst if element]
            return non_empty_list[0] if non_empty_list else None

    # putting the receipts info into dict
    receipt = {"shop_name": '', "manual_input": "(0)", "is_online": "(0)", "date": '', "tax": 0.0,"total": 0.0, "HH_id": ''}
    receipt.update({"shop_name": result[0][-2], "date": get_first_none_empty(date).strftime('%Y-%m-%d'),"total": max(item_price), "HH_id": HH_id})
    #receipt
    response = {"receipt": '',"products": []}
    response.update({"receipt": receipt, "products": items})

    return response



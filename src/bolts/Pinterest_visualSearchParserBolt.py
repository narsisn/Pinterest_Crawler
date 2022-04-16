import os
from collections import Counter
import json
from streamparse import Bolt
import requests
from bs4 import BeautifulSoup
import time
import pysolr 
from datetime import datetime
from retry_requests import retry
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from random import randint
import uuid

import numpy as np

from docopt import docopt
import pandas as pd
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color  

class Pinterest_visualSearchParserBolt(Bolt):
    outputs = ["url","product_category", "main_category", "business_name", "gender", "type", "business_type", "business_id"]
    def initialize(self, conf, ctx):
        self.solr_con = pysolr.Solr("http://192.168.104.100:8983/solr/Product_Core",always_commit=True, timeout=100)
        self.solr_ackedCon = pysolr.Solr("http://192.168.104.100:8983/solr/PAcked_Core",always_commit=True, timeout=100)
        self.samples = []
        self.lables = []
        self.storagePath = '/home/safari/logo_images/'


    def process(self, tup):
        if tup.values[0] != 'unknown_url':
            main_url = tup.values[0]
            product_category = tup.values[1]
            main_category = tup.values[2]
            business_name = tup.values[3]
            gender = tup.values[4]
            type_ = tup.values[5]
            business_type = tup.values[6]
            business_id = tup.values[7]
            try:
                retry_strategy = Retry(
                                    total=20,
                                    backoff_factor=8,
                                    )
                adapter = HTTPAdapter(max_retries=retry_strategy)
                adapter.max_retries.respect_retry_after_header = False
                http = requests.Session()
                http.mount("https://", adapter)
                http.mount("http://", adapter)
                main_response = http.get(main_url, verify=False ,timeout=30)
                j = json.loads(main_response.text)
            except:
                self.logger.info("reqyest get error ...." + str(main_url))
                # --- add acked number --- #
                self.solr_ackedCon.add([{
                    "business_name":business_name,
                    "acked_no" :{"inc": 1}
                }])
                return

       
            self.logger.info("---------------- Number of products: " + main_url)
            url = "url"
            brand ="متفرقه"
            product_description ="متفرقه"
            price = "0.0"
            has_discount="0"
            price_discount ="0.0"
            image_id ='image_id'
            product_link ='https://www.snapmode.ir'
            if j["resource_response"]["data"] is None:
                self.solr_ackedCon.add([{
                    "business_name":business_name,
                    "acked_no" :{"inc": 1}
                }])
                return 
            for i in range(1, len(j["resource_response"]["data"]["results"])):
                # try:
                image_id = j["resource_response"]["data"]["results"][i]["image_signature"]
                # --- save  image --- 
                img_url = j["resource_response"]["data"]["results"][i]["images"]["orig"]["url"]
                iamge_name = img_url.split('/')[-1]
                data_img = http.get(img_url ,timeout=50)
                imagePath = self.storagePath + iamge_name
                with open(imagePath, 'wb') as fobj:
                    fobj.write(data_img.content) 
                url = 'https://images.snapmode.ir/'+ iamge_name
                #--------
                product_description = j["resource_response"]["data"]["results"][i]["description"] 
                price = price_discount = 0
                product_link ="https://www.snapmode.ir/products/" + image_id
           
                # except: 
                    # self.logger.info("Extract Data Error.")
                    # continue
                # check if product exsit at database 
                try:
                    url_result=self.solr_con.search("url:"+'"'+url+'"')
                except:
                    self.logger.info("Solr Connection Error...")
                    continue

                    
                    # index solr 
                    try:
                        if url == "" or url == None or url is None:
                            url = "url"
                        if product_description == "" or product_description == None or product_description is None:
                            product_description = "متفرقه"
                        if brand == "" or brand == None or brand is None:
                            brand = 'متفرقه'
                        if price == "" or price == None or price is None:
                            price = 0.0
                        if has_discount == "" or has_discount == None or has_discount is None:
                            has_discount = "0"
                        if price_discount == "" or price_discount == None or price_discount is None:
                            price_discount == 0.0
                        if image_id == ""  or image_id == None or image_id is None:
                            image_id = business_name + "_" + str(randint(1, 1004663))
                        if product_link  == "" or product_link == None or product_link is None:
                            product_link = "https://www.snapmode.ir"
                        self.solr_con.add([
                                    {
                                    "product_id" : image_id,
                                    "price" : float(price),
                                    "url" : url,
                                    "product_link" : product_link,
                                    "brand" : brand, 
                                    "product_description" : product_description,                    
                                    "product_category" : product_category,
                                    "main_category" : main_category,
                                    "business_name" : business_name,
                                    "gender" : gender,
                                    "type_" : type_,
                                    "business_type" : business_type,
                                    "business_id" : business_id,
                                    "date" : datetime.now().isoformat(timespec='seconds') + "Z",
                                    "has_discount":has_discount,
                                    "price_discount":float(price_discount),
                                  
                                    "tags":product_description,
                                    "phase_status":"active",
                                    "product_view":"true",
                                    
                                        }
                                            ])
                        self.logger.info("Initial Solr indexing.")
                                        
                    except:
                            self.logger.info("Index Solr Error.")
                else:
                    # --- just update price, price discount, date ---- #
                    try :
                        self.solr_con.add([{
                            "url": url,
                            "price" :{"set": float(price)},
                            "date" : {"set":datetime.now().isoformat(timespec='seconds') + "Z"},
                            "has_discount":{"set":has_discount},
                            "price_discount":{"set":float(price_discount)},
                        }])
                        self.logger.info("Update Solr indexing.")
                    except:
                        self.logger.info("Update Solr Error.")

            # -- add acked number -- #
            self.solr_ackedCon.add([{
                "business_name":business_name,
                "acked_no" :{"inc": 1}
                }])
        else:
            # kill the topology 
            try:
            
                os.system('storm kill Pinterest_VisualSearchTopology -w 30')
            except :
                self.logger.info("Pinterest_VisualSearchTopology Topolgy Killing Error ... ")

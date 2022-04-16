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
from color_extractor import FromJson, FromFile
from docopt import docopt
import pandas as pd
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color  

main_url = 'https://www.pinterest.com/resource/VisualLiveSearchResource/get/?source_url=/pin/208784132704948683/visual-search/&data={%22options%22:{%22isPrefetch%22:false,%22pin_id%22:%22208784132704948683%22,%22image_signature%22:%222de268c33fe49d0f20a410185f132aab%22,%22crop%22:{%22x%22:0.028368794326241134,%22y%22:0.02546922142549273,%22w%22:0.9397163120567376,%22h%22:0.9455448454214177},%22crop_source%22:5,%22no_fetch_context_on_resource%22:false},%22context%22:{}}&_=1604852570417'
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
if j["resource_response"]["data"] is None:
    print('olk')
# print(j["resource_response"]["data"]["results"])
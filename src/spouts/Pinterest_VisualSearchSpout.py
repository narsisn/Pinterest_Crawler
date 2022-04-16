from itertools import cycle

from streamparse import Spout
import pandas as pd
import time
import os
import pysolr
from datetime import datetime #***
from datetime import timedelta #***

class Pinterest_VisualSearchSpout(Spout):
    outputs = ["url", "product_category","main_category", "business_name", "gender", "type", "business_type", "business_id"]

    def initialize(self, stormconf, context):
        self.in_path = '/home/safari/Documents/snapmode_git/SnapMode_Pinterest_Crawler/csv_files/pinterest_visualsearch.csv'
        self.url_pd = pd.read_csv(self.in_path, quotechar="'")
        self.solr_conn = pysolr.Solr("http://192.168.104.100:8983/solr/PAcked_Core",always_commit=True, timeout=100)
        self.solr_prd_conn = pysolr.Solr("http://192.168.104.100:8983/solr/Product_Core",always_commit=True, timeout=100)
        self.solr_update_conn = pysolr.Solr("http://192.168.104.100:8983/solr/Update-Core",always_commit=True, timeout=100)
        self.business_name = 'Pinterest' #***
        # --- add business_name acked no --- # 
        self.solr_conn.add([{
            "business_name":self.business_name,
            "total_url": str(len(self.url_pd)),
            "acked_no" : 0
        }])
        # self.delta_day = 7
        # self.ex_update_date = datetime.today() - timedelta(days=int(self.delta_day))
        # self.ex_update_date= self.ex_update_date.strftime('%Y-%m-%d')+'T00:00:00Z'
        self.i = 0 

    def next_tuple(self):

        if self.i != len(self.url_pd):
            row = self.url_pd.iloc[self.i]
            self.logger.info("Emittedddd..."+ str(row['url']) )
            self.emit([row['url'], row['product_category'], row['main_category'], row['business_name'], row['gender'], row['type'], row['business_type'], row['business_id']], tup_id=self.i)
            self.i = self.i + 1
        else: 
            self.logger.info("no data for emitt, starting to delete ex product data ... " )
            # # delete ex data
            # del_query_str = "date: " + "[* TO " +self.ex_update_date +"]" + " AND " + "business_name: " + "'" + self.business_name + "'"          
            # self.solr_prd_conn.delete(q=del_query_str)
            while(1):
                # --- check aked no --- #
                results =self.solr_conn.search('business_name:'+'"'+self.business_name+'"')
                for res in results:
                    acked_no = res['acked_no']
                if acked_no == len(self.url_pd):
                    self.logger.info("no data for emitt, starting to send kill command ... " )
                    self.emit(['unknown_url', 'product_category', 'main_category', 'business_name', 'gender', 'type', 'business_type', 'business_id'], tup_id=self.i) #***
                    # self.solr_update_conn.add([{
                    #     "business_name":self.business_name,
                    #     "status" : {"set":"Down"}
                    #     }])
                    time.sleep(60)
                else :
                    self.logger.info("Waiting for all Executers Ackes ... " ) 
                    time.sleep(120)
    def ack(self, tup_id):
        pass  # if a tuple is processed properly, do nothing
                





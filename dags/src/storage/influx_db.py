import os
import dotenv
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

class InfluxDB :

    def __init__ (self) :
        dotenv.load_dotenv()
        token = '5bd2ec12b6e72e5b5af2aa33f5bee7e5a6ad909cc24da15baeb86cee7eaa9c88'
        self.org = 'calib'
        self.url = "http://192.168.200.136:8086"
        
        write_client = influxdb_client.InfluxDBClient(url=self.url,token=token,org=self.org)
        self.write_api = write_client.write_api(write_options=SYNCHRONOUS)

    def storage (self,bucket_name,data) :
        self.write_api.write(bucket=bucket_name,org=self.org,record=data)

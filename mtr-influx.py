import subprocess
import json
import datetime as dt
import logging
from influxdb import InfluxDBClient, SeriesHelper
import time

logging.basicConfig(level=logging.INFO)

DB_NAME = 'mtr'
user = 'root'
password = 'root'


# number of pings sent
CYCLES=3
# inverval between MTR tests in seconds
INTERVAL=40
MTR_HOSTS=["sebmmm90001v01.ww002.siemens.net",
            "defthw9913nv01.ww002.siemens.net",
            "tcip10lb.gecot.siemens.net"]

INFLUXDB_HOST="sn1gra01.ad101.siemens-energy.net"
INFLUXDB_PORT=8086



class HubEntry(SeriesHelper):
    class Meta:
        series_name = '{destination}'
        fields = ['time', 'loss', 'snt', 'last', 'avg', 'best', 'wrst', 'stdev']
        tags = ['destination', 'hop']


def save_data(mtr_result):
    db_client = InfluxDBClient(INFLUXDB_HOST, INFLUXDB_PORT, user, password, DB_NAME)
    db_client.create_database(DB_NAME)
    HubEntry.Meta.client = db_client

    # ping destination
    destination = mtr_result['report']['mtr']['dst']
    report_time = dt.datetime.utcnow()
    for hub in mtr_result['report']['hubs']:
        # persist the hub entry
        # Modifying the data if needed so that is can be easily sorted in the event of more than 9 hops.
        if len(hub['count']) < 2:
            hop = "0" + hub['count'] + "-" + hub['host']
        else:
            hop = hub['count'] + "-" + hub['host']
        HubEntry(
            time=report_time,
            destination=destination,
            hop=hop,
            loss=hub['Loss%'],
            snt=hub['Snt'],
            last=hub['Last'],
            avg=hub['Avg'],
            best=hub['Best'],
            wrst=hub['Wrst'],
            stdev=hub['StDev']
        )
    logging.info(f"save to influxdb: {INFLUXDB_HOST}:{INFLUXDB_PORT} dbname: {DB_NAME}")
    HubEntry.commit()

def main():
    while True:
        for mrt_host in MTR_HOSTS:
            logging.info(f"start mtr against {mrt_host}")
            mtr = subprocess.check_output(f"mtr --report --json --report-cycles {CYCLES} {mrt_host}", shell=True)
                                      #    stdout=subprocess.PIPE,
                                      #    stdout=subprocess.DEVNULL,
                                      #    stderr=subprocess.STDOUT)
            mrt_dic = json.loads(mtr)
            save_data(mrt_dic)
    time.sleep(INTERVAL)




if __name__ == '__main__':
    main()
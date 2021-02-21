import subprocess
import json
import datetime as dt
import logging
import graphitesend
import time

logging.basicConfig(level=logging.INFO)



# number of pings sent
CYCLES=3
# inverval between MTR tests in seconds
INTERVAL=30
MTR_HOSTS=["google.se",
           "www.sunet.se"]

GRAPHITES_HOST="192.168.1.199"


def save_data(mtr_result):
    report_time = dt.datetime.utcnow()
    destination = mtr_result['report']['mtr']['dst']
    destination = destination.replace(".","_")
    
    for hub in mtr_result['report']['hubs']:
        # persist the hub entry
        # Modifying the data if needed so that is can be easily sorted in the event of more than 9 hops.
        if len(hub['count']) < 2:
            hop = "0" + hub['count'] + "-" + hub['host']
        else:
            hop = hub['count'] + "-" + hub['host']
        hop = hop.replace(".","_")
        grafhite  = graphitesend.init(group=f"{destination}.{hop}", graphite_server=GRAPHITES_HOST, system_name='mtr')

        grafhite.send_dict( 
            {
            #   'time': report_time,
            # destination': destination,
            #'hop': hop,
            'loss': hub['Loss%'],
            'snt': hub['Snt'],
            'last': hub['Last'],
            'avg': hub['Avg'],
            'best': hub['Best'],
            'wrst': hub['Wrst'],
            'stdev': hub['StDev']
        }
        )
        
        



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
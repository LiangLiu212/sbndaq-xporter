#!/usr/bin/env python3

import requests
import re
run_number = 5458

parameter_spec={"metadata.fcl": {
          "components":"components",
          "configuration":"config_name",
          'projectversion':'sbndaq_commit_or_version'
          #'start_time':'daqinterface_start_time',
          #'stop_time':'daqinterface_stop_time'
    }}

ucondb_uri = 'https://dbdata0vm.fnal.gov:9443/sbnd_on_ucon_prod/app/data/run_records_pending/configuration/key=%d'

class RunHistoryiReader:
    def __init__(self,
            parameter_spec=parameter_spec,
            ucondb_uri=ucondb_uri):
        self.parameter_spec=parameter_spec
        self.ucondb_uri=ucondb_uri

    def unpack_clob(self,clob):
        pattern = re.compile (r'#{5}[^#{5}](.*\.fcl):\s#{5}\s([\s\S]*?)(?=(#{5}|End of Record))')
        for match in re.finditer(pattern, clob):
           yield (match.group(1),match.group(2))

    def fetch_clob(self,run_number):
        try:
            #in case of issues with RunHistory DB, a hotfix to disable SSL certificate checking is to add verify=False option to the get command below
            response = requests.get(self.ucondb_uri%(run_number))
            response.raise_for_status()
            return (0, response.text)
        except requests.exceptions.HTTPError as ex:
            return (-1, "Http Error: %s"%(ex))
        except requests.exceptions.ConnectionError as ex:
            return (-2 , "Error Connecting: %s"% (ex))
        except requests.exceptions.Timeout as ex:
            return (-3, "Timeout Error: %s"%(ex))
        except requests.exceptions.RequestException as ex:
            return (-4,  "Error: %s"%(ex))

    def parse_fhicl(self,fhicl_file):
        #Rewrite to use the fhiclpy libary
        results = {}
        error_count=0
        for file_name, export_params in self.parameter_spec.items():
            for name, key in export_params.items():
                pattern=r'%s:\s+(.*)'%key
                matches=re.findall(pattern,fhicl_file[1])
                if matches is None or not matches:
                    results[name]='Error: no matches for the regex /%s/ in %s.'%(pattern,file_name)
                    error_count+=1
                    continue
                if len(matches) > 1 :
                    results[name]='Error: too many matches for the regex /%s/ in %s.'%(pattern,file_name)
                    error_count+=1
                    continue
                results[name]=matches[0].replace('"', '').strip()
        return (error_count,results)


    def read(self,run_number):
        err, clob = self.fetch_clob(run_number)
        if err != 0:
            return(err,{'error':clob})
        results = {}
        error_count=0
        for fhicl_file in self.unpack_clob(clob):
            if fhicl_file[0] not in self.parameter_spec:
                continue
            tmp=self.parse_fhicl(fhicl_file)
            error_count+=tmp[0]
            results = {**results, **tmp[1]}
        return (error_count, results)

if __name__ == '__main__':
    my_existing_data={'run_number':12208 }
    result=RunHistoryiReader().read(run_number)
    if(result[0]!=0):
        print("ErrorCode=%d."%result[0])

    #merge and print
    print({**my_existing_data,**result[1]})

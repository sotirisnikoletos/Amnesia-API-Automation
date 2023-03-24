import requests
import os
import json
import ast
import subprocess
import time

path = "C:/Program Files/IMSI/Amnesia"

os.chdir(path)

command = ["java", "-Xms1024m", "-Xmx4096m", "-Dorg.eclipse.jetty.server.Request.maxFormKeys=1000000", "-Dorg.eclipse.jetty.server.Request.maxFormContentSize=1000000", "-jar", "amnesiaBackEnd-1.0-SNAPSHOT.jar", "--server.port=8181"]
subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


response=requests.post('http://localhost:8181/getSession')
json_response = json.loads(response.text)

session_id = json_response['Session_Id']

print(session_id)


#START FIRST CALL, LOAD DATA SET
cookies = {
    'JSESSIONID': f"{session_id}",
}

headers = {
    'Cookie': f"{session_id}",
    
}
#COLUMNS TAKEN FROM PRESIDIO###################################################
#
#
#
presidio_dict = '{"Lastname":"string","Firstname":"string","Country":"string"}'
#
#
#
################################################################################
files = {
    'file': open('C:/Users/sothr/Desktop/venetia/estonia-passenger-list.csv','rb'),
    'del': (None, ';'),
    'datasetType': (None, 'tabular'),
    'columnsType': (None, presidio_dict),
}

response = requests.post('http://localhost:8181/loadData', cookies=cookies, files=files,allow_redirects=True)


print(response.text)





#2ND CALL GENERATE HIERARCHY

files = {
    'hierType': (None,'distinct'),
    'varType': (None,'string'),
    'attribute': (None,'Lastname'),
    'hierName': (None,'codes_hier'),
    'sorting': (None,'alphabetical'),
    'fanout': (None,'3'),
}

response = requests.post('http://localhost:8181/generateHierarchy', cookies=cookies, files=files,allow_redirects=True)

with open('C:/Users/sothr/Desktop/venetia/pos_p_codes.txt', 'wb') as f:
   f.write(response.content)

print(response.text)



files = {
    'hierType': (None,'distinct'),
    'varType': (None,'string'),
    'attribute': (None,'Firstname'),
    'hierName': (None,'fcodes_hier'),
    'sorting': (None,'alphabetical'),
    'fanout': (None,'3'),
}

response = requests.post('http://localhost:8181/generateHierarchy', cookies=cookies, files=files,allow_redirects=True)

with open('C:/Users/sothr/Desktop/venetia/pos1_p_codes.txt', 'wb') as f:
   f.write(response.content)

print(response.text)

#masking attribs --form hierType=mask 
#--form varType=string
#--form attribute="Procedure Codes"
#--form hierName=codes_hier 
#--form length=3


files = {
    'hierType': (None,'mask'),
    'varType': (None,'string'),
    'attribute': (None,'Country'),
    'hierName': (None,'ccodes_hier'),
    'length': (None,'4'),
}

response = requests.post('http://localhost:8181/generateHierarchy', cookies=cookies, files=files,allow_redirects=True)

with open('C:/Users/sothr/Desktop/venetia/posc_p_codes.txt', 'wb') as f:
   f.write(response.content)

print(response.text)

time.sleep(3)


#3RD CALL GENERATE THE HIERARCHY 
files = {
    'hierarchies': open('C:/Users/sothr/Desktop/venetia/pos_p_codes.txt', 'rb'),
}

response = requests.post('http://localhost:8181/loadHierarchies', cookies=cookies, files=files)

print(response.text)



files = {
    'hierarchies': open('C:/Users/sothr/Desktop/venetia/pos1_p_codes.txt', 'rb'),
}

response = requests.post('http://localhost:8181/loadHierarchies', cookies=cookies, files=files)

print(response.text)

files = {
    'hierarchies': open('C:/Users/sothr/Desktop/venetia/posc_p_codes.txt', 'rb'),
}

response = requests.post('http://localhost:8181/loadHierarchies', cookies=cookies, files=files)

print(response.text)

time.sleep(3)

#4TH CALL ANONYMIZE

files = {
    'bind': (None, '{"Lastname":"codes_hier","Firstname":"fcodes_hier","Country":"ccodes_hier"}'),
    'k': (None, '3'),
}

response = requests.post('http://localhost:8181/anonymization', cookies=cookies,  files=files)

with open('C:/Users/sothr/Desktop/venetia/anonymized_mixedData2.csv', 'wb') as f:
    f.write(response.content)
print(response.text)


#5TH CALL SAVE ANONYMIZED DATA

time.sleep(4)

with open('C:/Users/sothr/Desktop/venetia/anonymized_mixedData2.csv', 'r') as f:
    dict_str = f.read().replace('{"Solutions":', '').strip()[:-1]
    my_dict = ast.literal_eval(dict_str)

last_safe = None
for key, value in my_dict.items():
    if isinstance(value, dict):
        if "result" in value and value["result"] == "safe":
            if "levels" in value:
                last_safe = value["levels"]

if last_safe is not None:
    print(last_safe)
    last=last_safe.replace(" ","")



files = {
    'sol': (None, last),
}

response = requests.post('http://localhost:8181/getSolution', cookies=cookies,  files=files)

with open('C:/Users/sothr/Desktop/venetia/anonymized_simple_table_data2.txt', 'wb') as f:
    f.write(response.content)
    
# Try number 2 at updating the student email field, this time via API instead of database writes. Should be "safer" and actually work

# importing modules
import oracledb  # used to connect to PowerSchool database
import datetime  # used to get current date and time
import os  # needed to get environement variables
from datetime import *
import acme_powerschool # a library to interact with the PowerSchool REST API. Found and documented here: https://easyregpro.com/acme.php
import json # needed to manipulate the json objects we pass and receive from the API


d118_client_id = os.environ.get("POWERSCHOOL_API_ID")
d118_client_secret = os.environ.get("POWERSCHOOL_API_SECRET")


un = os.environ.get('POWERSCHOOL_READ_USER') # username for read only user in PowerSchool
pw = os.environ.get('POWERSCHOOL_DB_PASSWORD') # password for read only user
cs = os.environ.get('POWERSCHOOL_PROD_DB') # connection string containing IP address, port, and database name to connect to

print("Username: " + str(un) + " |Password: " + str(pw) + " |Server: " + str(cs)) #debug so we can see where oracle is trying to connect to/with

if __name__ == '__main__': # main file execution
    with oracledb.connect(user=un, password=pw, dsn=cs) as con: # create the connecton to the database
        with con.cursor() as cur:  # start an entry cursor
            with open('studentEmailLog.txt', 'w') as log:
                startTime = datetime.now()
                startTime = startTime.strftime('%H:%M:%S')
                print(f'Execution started at {startTime}')
                print(f'Execution started at {startTime}', file=log)

                ps = acme_powerschool.api('d118-powerschool.info', client_id=d118_client_id, client_secret=d118_client_secret) # create ps object via the API to do requests on

                # Query of all active students
                cur.execute('SELECT dcid, student_number, schoolid FROM students WHERE enroll_status = 0 ORDER BY student_number DESC')
                users = cur.fetchall()
                for user in users:
                    dcid = int(user[0])
                    studentNumber = str(int(user[1]))
                    email = str(int(user[1])) + '@d118.org' # CHANGE THIS IF YOU ARE NOT AT D118
                    homeschool = int(user[2])
                    try: # put overall processing in try/except blocks so we can just skip a user on an error and continue
                        print(f'INFO: Starting student {studentNumber} at building {homeschool} with DCID: {dcid}')
                        # print(f'INFO: Starting user {studentNumber} at building {homeschool} with DCID: {dcid}', file=log)

                        response = ps.get(f'ws/v1/student/{dcid}?expansions=contact_info') # get the student info for the current DCID, with the contact info expansion which contains the student email
                        currentEmail = response.json().get('student').get('contact_info') # get the contact info entry, which should contain a key called email and the value of their email. But may not exist for new students
                        # print(currentEmail) #debug
                        
                        if type(currentEmail) is str: # if there is an email already, it will be the type dict otherwise it will be a string. This block means there is no email currently
                            print(f'ACTION: Student {studentNumber} with DCID {dcid} currently has no email in their contact info, adding it')
                            print(f'ACTION: Student {studentNumber} with DCID {dcid} currently has no email in their contact info, adding it', file=log)
                            # do the actual API request with a post of the correct student info (dcid as both id and client_uid), and include the desired email in the contact info field
                            result = ps.post('ws/v1/student', data=json.dumps({'students' : {'student' : [{'id': str(dcid), 'client_uid' : str(dcid), 'action' : 'UPDATE', 'contact_info' : {'email' : email}}]}}))
                            statusCode = result.json().get('results').get('result').get('status')
                            if statusCode != 'SUCCESS':
                                print(f'ERROR: Student {studentNumber} with DCID {dcid} did not update successfully, status {statusCode}')
                                print(f'ERROR: Student {studentNumber} with DCID {dcid} did not update successfully, status {statusCode}', file=log)

                        else: # if there already is an email in the contact info, just check to make sure its accurate
                            currentEmail = currentEmail.get('email') # get the actual email field
                            if currentEmail != email: # check to see if the current email matches what it should be
                                print(f'ACTION: Student {studentNumber} with DCID {dcid} currently has email {currentEmail}, updating!')
                                print(f'ACTION: Student {studentNumber} with DCID {dcid} currently has email {currentEmail}, updating!', file=log)
                                # do the actual API request with a post of the correct student info (dcid as both id and client_uid), and include the desired email in the contact info field
                                result = ps.post('ws/v1/student', data=json.dumps({'students' : {'student' : [{'id': str(dcid), 'client_uid' : str(dcid), 'action' : 'UPDATE', 'contact_info' : {'email' : email}}]}}))
                                statusCode = result.json().get('results').get('result').get('status')
                                if statusCode != 'SUCCESS':
                                    print(f'ERROR: Student {studentNumber} with DCID {dcid} did not update successfully, status {statusCode}')
                                    print(f'ERROR: Student {studentNumber} with DCID {dcid} did not update successfully, status {statusCode}', file=log)
                        
                    except Exception as err: # general error catching
                        print(f'ERROR on student {studentNumber} at building {homeschool} with DCID: {dcid} | Error: {err}')
                        print(f'ERROR on student {studentNumber} at building {homeschool} with DCID: {dcid} | Error: {err}', file=log)
                
                endTime = datetime.now()
                endTime = endTime.strftime('%H:%M:%S')
                print(f'INFO: Execution ended at {endTime}')
                print(f'INFO: Execution ended at {endTime}', file=log)
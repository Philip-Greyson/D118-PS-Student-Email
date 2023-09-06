# D118-PS-Student-Email

Smallish script to populate the student email field in PS automatically

Needs the API Client ID saved as an environment variable named "POWERSCHOOL_API_ID"  
Needs the API Client Secret saved as an environment variable named "POWERSCHOOL_API_SECRET"  
  
Needs the PS Database username (I suggest a read only user) saved as an environment variable named "POWERSCHOOL_READ_USER"  
Needs the PS Database password for the username above saved as an environment variable named "POWERSCHOOL_DB_PASSWORD"  
Needs the PS Database IP address, portnumber, and database name (x.x.x.x:xxxx/db) saved as environment variable named "POWERSCHOOL_PROD_DB"  
  
Needs the oracledb and acme_powerschool libraries installed.

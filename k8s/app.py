import os
import pyodbc, struct
import requests
import time

def connectToAzureSQL():
    tenant_id = os.getenv('AZ_TENANT_ID')
    client_id = os.getenv('AZ_CLIENT_ID')
    server = os.getenv('AZ_SERVER')
    database = os.getenv('AZ_DATABASE')   
    connection_string = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30"

    service_account_token_path = '/var/run/secrets/tokens/sa-token'
    with open(service_account_token_path, 'r') as token_file:
        service_account_token = token_file.read().strip()
    
    # print the environment variables to the console
    print("AZ_TENANT_ID: " + tenant_id)
    print("AZ_CLIENT_ID: " + client_id)
    print("AZ_SERVER: " + server)
    print("AZ_DATABASE: " + database)
    
    # print a message if the service token is not null and has a length greater than 0
    if service_account_token is not None and len(service_account_token) > 0:
        # truncate the token to 10 characters for security reasons
        print("Service Account Token: " + service_account_token[:10] + "...")        
    else:
        print("Service Account Token is null or empty")


    url = f'https://login.microsoftonline.com:443/{tenant_id}/oauth2/v2.0/token '
    payload = (
        "scope=https%3A%2F%2Fdatabase.windows.net%2F.default"
        f"&client_id={client_id}"
        "&client_assertion_type=urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer"
        f"&client_assertion={service_account_token}"
        "&grant_type=client_credentials"
    )
    response = requests.post(url, data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    if response.status_code == 200:
        print("Token obtained from Azure AD:")
        responseJson = response.json()
        access_token = responseJson['access_token']
        print("Federated token obtained fro Entra")

        token_bytes = access_token.encode("UTF-16-LE")
        token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
        SQL_COPT_SS_ACCESS_TOKEN = 1256 
        conn = pyodbc.connect(connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
        cursor = conn.cursor()
        cursor.execute("SELECT TOP (1000) * FROM [dbo].[Customer]") 
        row = cursor.fetchone()
        while row:
            print("Customer ID-->" + str(row[0]))
            row = cursor.fetchone()        
    else:
        print("Error:", response.text)
    
connectToAzureSQL()

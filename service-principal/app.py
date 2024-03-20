import os
import pyodbc, struct
from azure.identity import DefaultAzureCredential, ClientSecretCredential


def test001():
    tenant_id = os.getenv('AZ_TENANT_ID')
    client_id = os.getenv('AZ_CLIENT_ID')
    client_secret = os.getenv('AZ_CLIENT_SECRET')
    server = os.getenv('AZ_SERVER')
    database = os.getenv('AZ_DATABASE')    
    
    credential = ClientSecretCredential(tenant_id, client_id, client_secret)    
    connection_string = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30"
    token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
    token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
    SQL_COPT_SS_ACCESS_TOKEN = 1256 
    conn = pyodbc.connect(connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
    cursor = conn.cursor()
    cursor.execute("SELECT TOP (1000) * FROM [dbo].[Customer]") 
    row = cursor.fetchone()
    while row:
       print("Customer ID-->" + str(row[0]))
       row = cursor.fetchone()

test001()

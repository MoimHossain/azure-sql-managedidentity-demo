# azure-sql-managedidentity-demo
A python demo to address workload identity of Kubernetes can connect to azure sql

# Steps

## Create a SQL server with AD ADMIN
Using portal for now to create the SQL server.

## Create table and rows

Using portal SQL editor, create the table and insert rows.

```sql
CREATE TABLE Customer (
    customer_id INT PRIMARY KEY IDENTITY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    active BIT
);
```

Insert some sample rows:

```sql
INSERT INTO Customer (first_name, last_name, active) VALUES ('John', 'Doe', 1);
INSERT INTO Customer (first_name, last_name, active) VALUES ('Jane', 'Smith', 0);
INSERT INTO Customer (first_name, last_name, active) VALUES ('Alice', 'Johnson', 0);
INSERT INTO Customer (first_name, last_name, active) VALUES ('Bob', 'Brown', 1);
INSERT INTO Customer (first_name, last_name, active) VALUES ('Emily', 'Davis', 0);
```

## Create a user Service Principal

```sql
CREATE USER [SP-AZURESQL-USER] FROM EXTERNAL PROVIDER;

ALTER ROLE db_datareader ADD MEMBER [SP-AZURESQL-USER];
ALTER ROLE db_datawriter ADD MEMBER [SP-AZURESQL-USER];
ALTER ROLE db_ddladmin ADD MEMBER [SP-AZURESQL-USER];

SELECT * FROM sys.database_principals WHERE type_desc = 'EXTERNAL_USER'
```


# Python app (building from directory)

## Installing requirement

```bash
    pip install -r requirements.txt
``` 

## Running the app

You need the following service principal environment variables:

```bash
    export AZ_TENANT_ID="your_tenant_id"
    export AZ_CLIENT_ID="your_client_id"
    export AZ_CLIENT_SECRET="your_client_secret"
    export AZ_SERVER="your_server"
    export AZ_DATABASE="your_database"
```

Now run the app:

```bash
    python app.py
```

## Containerize the app

```bash
    docker build -t moimhossain/python-odbc-azure-sql:beta .
```

## Running the container

```bash
    docker run --rm -e AZ_TENANT_ID="your_tenant_id" -e AZ_CLIENT_ID="your_client_id" -e AZ_CLIENT_SECRET="your_client_secret" -e AZ_SERVER="your_server" -e AZ_DATABASE="your_database" moimhossain/python-odbc-azure-sql:beta
```
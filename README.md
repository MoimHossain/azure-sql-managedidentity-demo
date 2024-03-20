# azure-sql-managedidentity-demo
A python demo to address workload identity of Kubernetes can connect to azure sql. 

The federated credentials token exchange can be found in here:

[Access token request with a federated credential](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-client-creds-grant-flow#third-case-access-token-request-with-a-federated-credential)

Essentially, 
```
POST /{tenant}/oauth2/v2.0/token HTTP/1.1               // Line breaks for clarity
Host: login.microsoftonline.com:443
Content-Type: application/x-www-form-urlencoded

scope=https%3A%2F%2Fgraph.microsoft.com%2F.default
&client_id=97e0a5b7-d745-40b6-94fe-5f77d35c6e05
&client_assertion_type=urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer
&client_assertion=eyJhbGciOiJSUzI1NiIsIng1dCI6Imd4OHRHeXN5amNScUtqRlBuZDdSRnd2d1pJMCJ9.eyJ{a lot of characters here}M8U3bSUKKJDEg
&grant_type=client_credentials
```

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


# Azure Kubernetes services

## Create AKS

Create an AKS cluster using the az aks create command with the --enable-oidc-issuer parameter to use the OIDC Issuer.

```
export RESOURCE_GROUP="AKS_SQL_WORKLOAD_IDENTITY"
export CLUSTER_NAME="moimhaakscluster"

az aks create -g "${RESOURCE_GROUP}" -n $CLUSTER_NAME --node-count 1 --enable-oidc-issuer --enable-workload-identity --generate-ssh-keys
```

Get the OIDC Issuer URL and save it to an environmental variable using the following command. Replace the default value for the arguments -n, which is the name of the cluster.

```
export AKS_OIDC_ISSUER="$(az aks show -n $CLUSTER_NAME -g "${RESOURCE_GROUP}" --query "oidcIssuerProfile.issuerUrl" -otsv)"

echo $AKS_OIDC_ISSUER 

#example output: https://eastus.oic.prod-aks.azure.com/000000000000/0000000000000/

```

### Create namespace

```
kubectl create namespace workload-demo 
```

### Create service account into the new namespace:

```
kubectl apply -f service-account.yaml 
kubectl describe serviceaccount/workload-demo-service-account -n workload-demo
```

## Establish federated identity credential

Create the federated identity credential between the managed identity, service account issuer, and subject using the az identity federated-credential create command.

> NOTE: When you configure federation, the audience for AKS should be the same URI as the OIDC issuer.

```
az identity federated-credential create --name ${FEDERATED_IDENTITY_CREDENTIAL_NAME} --identity-name ${USER_ASSIGNED_IDENTITY_NAME} --resource-group ${RESOURCE_GROUP} --issuer ${AKS_OIDC_ISSUER} --subject system:serviceaccount:${SERVICE_ACCOUNT_NAMESPACE}:${SERVICE_ACCOUNT_NAME}
```


## Manually proofing the token

Get Kubernetes service token

```
kubectl create token workload-demo-service-account -n workload-demo
```

### Deploy the pod

```
kubectl apply -f pod.yaml 

kubectl get pods -A # Sampel> workload-demo pyodbc-demo-pod  0/1  Completed
```

using Microsoft.Data.SqlClient;

string serverName = Environment.GetEnvironmentVariable("DATABASE_SERVER");
string databaseName = Environment.GetEnvironmentVariable("DATABASE_NAME");
string clientId = Environment.GetEnvironmentVariable("CLIENT_ID");
string clientSecret = Environment.GetEnvironmentVariable("CLIENT_SECRET");

string ConnectionString = $"Server={serverName}.database.windows.net; Authentication=Active Directory Service Principal; Encrypt=True; Database={databaseName}; User Id={clientId}; Password={clientSecret}";

using SqlConnection conn = new SqlConnection(ConnectionString);
conn.Open();
using SqlCommand cmd = new SqlCommand("SELECT TOP (1000) * FROM [dbo].[Customer]", conn);
using SqlDataReader reader = cmd.ExecuteReader();
while (reader.Read())
{
    Console.WriteLine(reader["first_name"]);
}

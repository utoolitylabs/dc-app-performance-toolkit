param (
    [string]$targetBaseUrl = "https://bamboo.ifaws-1573-20220221-1.tst.utoolity.net",
    [Parameter(Mandatory = $true)][string]$accessKeyId,
    [string]$secretAccessKey = $( Read-Host "Enter secretAccessKey" ),
    [int]$numAccounts = 10,
    [int]$numConnectors = 100,
    [string]$accountBaseName = "TestAccount-",
    [string]$connectorBaseName = "TestConnector-",
    [string]$user = "admin",
    [string]$pass = $( Read-Host "Enter host instance password" )
)
$accountsEndpoint = $targetBaseUrl + "/rest/identity-federation-for-aws/2.2/accounts?skipValidation=true"
$connectorsEndpoint = $targetBaseUrl + "/rest/identity-federation-for-aws/2.2/connectors"
$statusEndpoint = $targetBaseUrl + "/rest/identity-federation-for-aws/2.2/status/info"
$sessionName = [guid]::NewGuid().toString()

# Prime the session
$auth = $user + ":" + $pass
http --auth $auth --session=$sessionName GET $statusEndpoint

# Using here-doc-string for a fixed payload json, replacing some entries on the fly later on
$accountTemplate = @"
{
    "name": "ACCOUNT_NAME_TBR",
    "awsAccessKeyId": "ACCESS_KEY_ID_TBR",
    "awsSecretKey": "SECRET_ACCESS_KEY_TBR",
    "cloudProviderKey": "aws"
}
"@

# Create accounts, collecting ids on the fly
$accountIds = New-Object System.Collections.ArrayList
foreach($i in 1..$numAccounts) {
    $accountName = $accountBaseName + $i
    $json = $accountTemplate.Replace("ACCOUNT_NAME_TBR", $accountName).Replace("ACCESS_KEY_ID_TBR", $accessKeyId).Replace("SECRET_ACCESS_KEY_TBR", $secretAccessKey)
    $accountResponse = (Write-Output $json | http --session=$sessionName POST $accountsEndpoint)
    # Write-Output $accountResponse
    # NOTE: Extracting account id by regex, which of course relies a bit on stable JSON output format
    $regEx = '"id":"(.*?)"';
    $accountResponse -match $regEx
    $accountId = $matches[1]
    # Write-Output $accountId
    $accountIds.Add($accountId)
}

# Using here-doc-string for a fixed payload json, replacing some entries on the fly later on
# NOTE/TODO: Hardcoded groups would need to be in place in target instance, or adjusted/removed here
$connectorTemplate = @"
{
    "name": "CONNECTOR_NAME_TBR",
    "type": "ASSUME_ROLE",
    "scope": "SYSTEM",
    "partition": "aws",
    "accountId": "ACCOUNT_ID_TBR",
    "roleArn": "arn:aws:iam::288727192237:role/ifaws-quickstart-uaa-453-IdentityFederationForAWS-1L84NAN9NUAYQ",
    "externalId": "",
    "iamPolicy": "",
    "groups": [
        "performance-user"
    ]
}
"@

# Create connectors
foreach($i in 1..$numConnectors) {
    $connectorName = $connectorBaseName + $i
    $accountId = Get-Random -InputObject $accountIds
    $json = $connectorTemplate.Replace("CONNECTOR_NAME_TBR", $connectorName).Replace("ACCOUNT_ID_TBR", $accountId)
    Write-Output $json | http --session=$sessionName POST $connectorsEndpoint
    # Write-Output $json
}

param (
    [string]$targetBaseUrl = "https://bamboo.ifaws-1573-20220216-1.tst.utoolity.net",
    [string]$groupName = "bamboo-user",
    [string]$user = "admin",
    [string]$pass = $( Read-Host "Enter host instance password" )
)

$sessionName = [guid]::NewGuid().toString()
$currentUserEndpoint = $targetBaseUrl + "/rest/api/latest/currentUser"
$getUsersEndpoint = $targetBaseUrl + "/rest/api/latest/admin/users?start=1&limit=2010"
$addUsersEndpoint = $targetBaseUrl + "/rest/api/latest/admin/groups/performance-user/add-users"

# Prime the session
$auth = $user + ":" + $pass
http --auth $auth --session=$sessionName GET $currentUserEndpoint

$getUsersResponse = http --session=$sessionName --json GET $getUsersEndpoint
$namesOnlyArray = $getUsersResponse | jq '[.results[] | {name} | .name]'
Write-Output $namesOnlyArray

$addToGroupResponse = Write-Output $namesOnlyArray | http --session=$sessionName POST $addUsersEndpoint
Write-Output $addToGroupResponse

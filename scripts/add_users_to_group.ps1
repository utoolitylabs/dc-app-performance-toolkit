param (
    [string]$targetBaseUrl = "https://bamboo.ifaws-1573-20220216-1.tst.utoolity.net",
    [string]$groupName = "bamboo-user",
    [string]$user = "admin",
    [string]$pass = $( Read-Host "Enter host instance password" )
)

$sessionName = [guid]::NewGuid().toString()
$currentUserEndpoint = $targetBaseUrl + "/rest/api/latest/currentUser"
$getUsersEndpoint = $targetBaseUrl + "/rest/api/latest/admin/users"
$addUsersEndpoint = $targetBaseUrl + "/rest/api/latest/admin/groups/performance-user/add-users"

# Prime the session
$auth = $user + ":" + $pass
http --auth $auth --session=$sessionName GET $currentUserEndpoint

# Grab users and put them into groups in chunks to prevent hibernate constraint violations (presumed overload)
$chunkSize = 32
$assumedCout = 2010
$iterations = [int][Math]::Ceiling($assumedCout / $chunkSize)
$currentIndex = 0 # includes the admin, no harm in him being in the groups as well
foreach($i in 1..$iterations) {
    Write-Output "Iteration: $i / $iterations"
    $requestUrl = $getUsersEndpoint + "?start=" + $currentIndex + "&limit=" + $chunkSize
    $getUsersResponse = http --session=$sessionName --json GET $requestUrl
    $namesOnlyArray = $getUsersResponse | jq '[.results[] | {name} | .name]'
    Write-Output $namesOnlyArray
    Write-Output $namesOnlyArray | http --session=$sessionName POST $addUsersEndpoint
    $currentIndex = $currentIndex + $chunkSize
}

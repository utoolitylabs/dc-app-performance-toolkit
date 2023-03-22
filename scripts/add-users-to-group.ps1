param (
    [Parameter(Mandatory,HelpMessage='targetBaseUrl')][string]$targetBaseUrl,
    [string]$groupName = "performance-user",
    [string]$user = "admin",
    [Parameter(Mandatory,HelpMessage='Enter host instance password')][string]$pass
)

$sessionName = [guid]::NewGuid().toString()
$currentUserEndpoint = $targetBaseUrl + "/rest/api/latest/currentUser"
$adminGroupsEndpoint = $targetBaseUrl + "/rest/api/latest/admin/groups"
$getUsersEndpoint = $targetBaseUrl + "/rest/api/latest/admin/users"
$addUsersEndpoint = $targetBaseUrl + "/rest/api/latest/admin/groups/" + $groupName +"/add-users"

# Prime the session
$auth = $user + ":" + $pass
http --auth $auth --session=$sessionName GET $currentUserEndpoint

# Create group, if not there already
$getGroupsResponse = http --session=$sessionName --json GET $adminGroupsEndpoint
$groupNamesOnlyArray = $getGroupsResponse | jq '[.results[] | {name} | .name]'
Write-Output $groupNamesOnlyArray
if($groupNamesOnlyArray -Match $groupName) {
    Write-Output "Found group name '"  $groupName  "' using that ..."
}
else {
    Write-Output "Did not find group name '"  $groupName  "' creating ..."
    $payload = '{"name": "' + $groupName + '"}'
    Write-Output $payload | http --session=$sessionName --json POST $adminGroupsEndpoint
}

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

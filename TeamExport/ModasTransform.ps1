
$MTeamExport_GIT_path = "D:\WORK\TeamPolska\git\TeamAssets\TeamExport\TeamExport"
$buildFile = $MTeamExport_GIT_path+"\TeamExport.sqlproj"
$msbuild = "C:\Windows\Microsoft.Net\Framework\v4.0.30319\MSBuild.exe"
$sqlpackage = "C:\Program Files (x86)\Microsoft SQL Server\140\DAC\bin\SqlPackage.exe"
$dacpac_sourceFile = $MTeamExport_GIT_path+"\bin\Debug\TeamExport.dacpac"
$ServerName = "."
$DBName = "TeamExport"
$Mode = "Debug"

$commands = 
{

	$RunMSBuild = 
		{
		Write-host "----------------------Build start-------------------------" -foregroundcolor "black" -backgroundcolor "yellow"
		$collectionOfArgs = @($buildFile, "/target:Build", "/p:VisualStudioVersion=14.0", "/p:Configuration=$Mode", "/p:Platform=AnyCPU")
		& $msbuild $collectionOfArgs
		}

	&$RunMSBuild
        #if ($LastExitCode -ne 0){break}	

	$RunSQLPackage = 
		{
		Write-host "----------------------SQLPackage start----------------------" -foregroundcolor "black" -backgroundcolor "yellow"

		$collectionOfDeployArgs =
			@(
			 "/SourceFile:$dacpac_sourceFile"
			,"/Action:Publish"
			,"/TargetServerName:$ServerName"
			,"/TargetDatabaseName:$DBName"
			,"/p:IncludeCompositeObjects=True"
			,"/p:BlockWhenDriftDetected=False"
			,"/p:RegisterDataTierApplication=False"
			,"/p:BlockOnPossibleDataLoss=False"
			,"/p:GenerateSmartDefaults=True"
			,"/p:DropObjectsNotInSource=True"
			,"/Variables:ProfileEnv=Global"
			)

		& $sqlpackage $collectionOfDeployArgs
		}
	&$RunSQLPackage		
        #if ($LastExitCode -ne 0){break}		
		
$defaultAgain = "Y"
if(($again = Read-Host "Again?") -eq '') {$again = $defaultAgain}
	if ($again -eq "Y")
	{
		&$commands
	}
	else
	{
		Write-Host "Bye Bye!"    
	}		
}

&$commands
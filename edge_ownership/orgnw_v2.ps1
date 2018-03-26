$reportedorgnws = New-Object System.Collections.ArrayList
$orgnws = Get-Get-OrgVdcNetwork
Foreach ($nw in $orgnws) {
	$reportedorgnw = New-Object PSObject
	Add-Member -InputObject $reportedorgnw -MemberType NoteProperty -name "orgnw" -value $nw.Name
	Add-Member -InputObject $reportedorgnw -MemberType NoteProperty -name "providerinfo" -value $nw.ExtensionData.ProviderInfo
	$reportedorgnws.add($reportedorgnw)|Out-Null
}
$reportedorgnws|Export-Csv z:\orgnwreport.csv
# Windows torrenting with qBittorrent and McAfee Secure VPN

This setup uses qBittorrent's network interface binding and Windows Firewall rules to restrict qBittorrent traffic to the McAfee tunnel. Start with an official Debian installer torrent. Use this setup for files you have permission to download and share.

## Connect McAfee and bind qBittorrent

1. Install [qBittorrent for Windows](https://www.qbittorrent.org/download) and review its first-run notice. Pause any existing torrents while configuring the client.
2. In McAfee Secure VPN, turn **Safe reconnect** on and **Split tunneling** off, then connect the VPN.
3. In PowerShell, run the commands below. Identify the tunnel adapter by comparing the interface list and the selected route for a public IPv4 address. This route lookup uses the local routing table. In the tested setup, `McAfee_VPN` was the tunnel and `McAfee VPN` was a separate adapter. Check the name on your own system.

   ```powershell
   Get-NetAdapter -IncludeHidden | Format-Table Name, InterfaceDescription, Status
   Find-NetRoute -RemoteIPAddress 1.1.1.1 |
       Format-List InterfaceAlias, InterfaceIndex, DestinationPrefix, NextHop
   ```

4. In qBittorrent, open **Tools → Options → Advanced → Network interface**. Select the confirmed tunnel adapter and apply the change. Exit qBittorrent fully, including from the notification area if it is still running. Reopen it and confirm the setting persisted. See the [qBittorrent options reference](https://github.com/qbittorrent/qBittorrent/wiki/Explanation-of-Options-in-qBittorrent).

## Add the Windows Firewall rules

Keep the VPN connected and qBittorrent open. Open **PowerShell as administrator**. Replace `McAfee_VPN` below if your confirmed tunnel alias differs. The script displays the other visible adapters so you can review the list before it adds inbound and outbound blocks for the running `qbittorrent.exe`. If either rule already exists, inspect it with the verification commands below before making changes.

```powershell
$vpnAlias = 'McAfee_VPN'
$adapters = @(Get-NetAdapter -ErrorAction Stop)
if (-not ($adapters | Where-Object { $_.Name -eq $vpnAlias -and $_.Status -eq 'Up' })) {
    throw "The selected VPN adapter is missing or down: $vpnAlias"
}

$blockedAliases = @($adapters | Where-Object Name -ne $vpnAlias | Select-Object -ExpandProperty Name)
if ($blockedAliases.Count -eq 0) { throw 'No other adapters were found.' }

$clientPath = (Get-Process -Name qbittorrent -ErrorAction Stop | Select-Object -First 1).Path
if (-not $clientPath) { throw 'Could not resolve the path to the running qBittorrent client.' }

$ruleNames = @('qBittorrent-McAfeeVPN-Block-Outbound', 'qBittorrent-McAfeeVPN-Block-Inbound')
if (Get-NetFirewallRule -PolicyStore PersistentStore -Name $ruleNames -ErrorAction SilentlyContinue) {
    throw 'At least one setup rule already exists. Inspect the current rules before editing them.'
}

$blockedAliases
if ((Read-Host 'Type YES if these are the non-tunnel adapters to block') -cne 'YES') { return }

foreach ($direction in @('Outbound', 'Inbound')) {
    $name = "qBittorrent-McAfeeVPN-Block-$direction"
    New-NetFirewallRule -Name $name -DisplayName $name -Direction $direction `
        -Action Block -Enabled True -Profile Any -Program $clientPath `
        -InterfaceAlias $blockedAliases -ErrorAction Stop | Out-Null
}
```

Verify that the firewall is enabled for the applicable network profiles, both rules are in the active policy, the program path matches the running client, and the blocked interfaces exclude the tunnel. If a rule creation failed partway through, inspect both rules and use Windows Defender Firewall with Advanced Security to correct the existing rule or add the missing direction using the same program and adapter list. Recheck the list after adding or changing adapters, and recheck the program path after moving or reinstalling qBittorrent.

```powershell
Get-NetFirewallProfile -PolicyStore ActiveStore | Format-Table Name, Enabled
$ruleNames = @('qBittorrent-McAfeeVPN-Block-Outbound', 'qBittorrent-McAfeeVPN-Block-Inbound')
$rules = Get-NetFirewallRule -PolicyStore ActiveStore -Name $ruleNames -ErrorAction Stop
foreach ($rule in $rules) {
    $rule | Format-List Name, Enabled, Direction, Action, Profile
    $rule | Get-NetFirewallApplicationFilter | Format-List Program
    $rule | Get-NetFirewallInterfaceFilter | Format-List InterfaceAlias
}
```

See Microsoft's [New-NetFirewallRule reference](https://learn.microsoft.com/en-us/powershell/module/netsecurity/new-netfirewallrule) for the program and interface filters.

## Test with Debian

1. With McAfee connected, add an official Debian `netinst.iso.torrent` for your architecture. Use the [Debian amd64 torrent directory](https://cdimage.debian.org/debian-cd/current/amd64/bt-cd/) for 64-bit Intel and AMD PCs, or the [Debian download page](https://www.debian.org/distrib/) to find other architectures. Wait for sustained download activity. If the test finishes too quickly, set a temporary per-torrent download limit and repeat while there is still data to download.
2. Leave qBittorrent open. Disconnect McAfee for about 15 seconds, then reconnect it. This briefly interrupts VPN protection for other apps. Look for peer connections to drop during the disconnect and for transfer to resume after reconnecting. The speed display can take several seconds to settle.
3. For a stronger check, sample established qBittorrent TCP connections throughout the cycle. In a separate PowerShell window run the following, stop it with **Ctrl+C**, and compare the connection `LocalAddress` values with the addresses assigned to the tunnel. The loop displays a timestamp even when there are no established connections.

   ```powershell
   while ($true) {
       Get-Date -Format 'HH:mm:ss'
       $client = Get-Process -Name qbittorrent -ErrorAction SilentlyContinue
       if ($client) {
           Get-NetTCPConnection -OwningProcess $client.Id -State Established -ErrorAction SilentlyContinue |
               Format-Table LocalAddress, RemoteAddress, RemotePort
       } else {
           Write-Host 'qBittorrent is not running. Keep it open during the test.'
       }
       Get-NetIPAddress -InterfaceAlias 'McAfee_VPN' -ErrorAction SilentlyContinue |
           Select-Object -ExpandProperty IPAddress
       Start-Sleep -Seconds 1
   }
   ```

   Substitute your confirmed adapter alias in the loop if needed. Loopback connections are local to the PC. For external peers, look for connections sourced from the tunnel's addresses while connected, an absence of established external connections during the disconnect, and tunnel-sourced connections after reconnecting. An external connection sourced from a non-tunnel address calls for pausing the test and reviewing the binding and active rules.

4. Remove the test torrent from the queue after verification to stop seeding. Keep or discard the ISO as needed. Restore the original global download limit if you changed it for the test.

### What the test showed

With qBittorrent 5.3.0, the Debian download transferred while McAfee was connected. During two observed VPN disconnects, samples showed zero established external qBittorrent TCP connections while Windows routed through Wi-Fi. After reconnecting, the sampled external TCP connections used the McAfee tunnel again and the transfer resumed. UDP was outside the test's coverage. Download speed and on-disk file growth alone cannot identify the interface carrying the traffic.

### If the torrent stalls

- First confirm McAfee is connected and qBittorrent still shows the active tunnel in **Network interface**. If the adapter changed, update the binding and review the firewall rules before resuming.
- Select the torrent and check the **Trackers** tab and peer activity. The Ubuntu test stalled even though its tracker responded. Use the official Debian torrent to check for sustained transfer before attempting the disconnect test.
- If you still cannot establish a baseline, verify the bound adapter's IP addresses and confirm the active firewall rules exclude that adapter. Keep the binding in place while troubleshooting.

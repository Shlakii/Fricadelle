# Example scan results for testing
# Place your actual scan results in this directory

# Examples of supported file types:

## 1. Nmap JSON output
# nmap -sV -sC -oJ nmap_scan.json target.com

## 2. Kerbrute output
# kerbrute passwordspray -d domain.local --dc 10.10.10.10 users.txt Password123 > kerbrute.txt

## 3. CrackMapExec output
# crackmapexec smb 192.168.1.0/24 > crackmapexec.txt

## 4. Nuclei JSON output
# nuclei -u https://target.com -json-export nuclei.json

## 5. Any text-based tool output
# tool --scan target > scan_output.txt

# The AI will analyze each file and extract vulnerabilities automatically

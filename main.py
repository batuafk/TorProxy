import subprocess
import threading
import requests
import psutil
import time

class Tor:
    def write_torrc():
        with open("torrc", "w") as file:
            file.write(
                "BandwidthRate 2 GBytes\n"
                "BandwidthBurst 2 GBytes\n"
                "PerConnBWRate 2 GByte\n"
                "ClientTransportPlugin obfs4 exec obfs4/obfs4proxy\n"
                "ConnLimit 65535\n"
                "ConstrainedSockets 1\n"
                "ControlPort auto\n"
                "CookieAuthentication 1\n"
                "DataDirectory working_data\n"
                "DataDirectoryGroupReadable 1\n"
                "LogMessageDomains 1\n"
                "HardwareAccel 1\n"
                "ClientOnly 1\n"
                "SocksPort auto IsolateClientAddr IsolateSOCKSAuth IsolateClientProtocol IsolateDestPort IsolateDestAddr KeepAliveIsolateSOCKSAuth PreferSOCKSNoAuth\n"
                "TokenBucketRefillInterval 100 msec\n"
                "UseGuardFraction 1\n"
                "NumEntryGuards 1\n" # higher = more secure, but less performance
                "NumDirectoryGuards 1\n"
                "SafeSocks 1\n"
                "TestSocks 1\n"
                "WarnUnsafeSocks 1\n"
                "FastFirstHopPK 1\n" # gets ready slower but more secure
                "DNSPort auto IsolateClientAddr IsolateSOCKSAuth IsolateClientProtocol IsolateDestPort IsolateDestAddr KeepAliveIsolateSOCKSAuth PreferSOCKSNoAuth\n"
                "AllowSingleHopCircuits 1\n"
                "OptimisticData 1\n"
                "ServerDNSRandomizeCase 1\n"
                "GeoIPFile data/geoip\n"
                "GeoIPv6File data/geoip6\n"
            )

    def start():
        global bootstrapped, socks_port, dns_port, control_port
        process = subprocess.Popen("tor -f torrc", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        while True:
            output = process.stdout.readline().decode().strip()
            if output:
                print(output)
                if "Socks listener listening on port" in output:
                    socks_port = output.split()[-1].split(":")[-1].replace(".", "")
                elif "DNS listener listening on port" in output:
                    dns_port = output.split()[-1].split(":")[-1].replace(".", "")
                elif "Control listener listening on port" in output:
                    control_port = output.split()[-1].split(":")[-1].replace(".", "")
                elif "Bootstrapped 100% (done): Done" in output:
                    bootstrapped = True
                    print("\033[32m\nTor started\033[0m")
                    print(f"Control port: {control_port}")
                    print(f"Socks port: {socks_port}")
                    print(f"DNS port: {dns_port}\n")

    def stop():
        global bootstrapped
        for process in ["tor", "tor.exe"]:
            for proc in psutil.process_iter(['pid', 'name']):
                if process.lower() in proc.info['name'].lower():
                    print(f"Terminating PID: {proc.pid}")
                    process = psutil.Process(proc.pid)
                    process.terminate()
                    bootstrapped = False
                    return True
        return False
    
if __name__ == "__main__":
    bootstrapped = False

    socks_port = None
    dns_port = None
    control_port = None

    Tor.write_torrc()

    thread = threading.Thread(target=Tor.start)
    thread.start()

    while True:
        if bootstrapped is True:
            proxies = {
                'http': f'socks5h://127.0.0.1:{socks_port}',
                'https': f'socks5h://127.0.0.1:{socks_port}'
            }
            
            response = requests.get("http://api.ipify.org", proxies=proxies)
            print("Proxy IP:", response.text)
            break
        else:
            time.sleep(5)
    
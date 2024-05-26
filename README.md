# TorProxy
Python Tor SOCKS5 Proxy with best torrc settings for security

Linux:
```bash
pip install pysocks requests psutil
git clone https://github.com/Bt08s/TorProxy.git
cd TorProxy
python main.py

sudo apt install torsocks -y
torsocks <appname>

Examples:
  - torsocks firefox
  - torsocks ./script.sh
  - torsocks curl https://api.ipify.org
```

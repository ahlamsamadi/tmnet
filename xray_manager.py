import json
import os
import subprocess
import asyncio
import logging

XRAY_CONFIG_PATH = "/usr/local/bin/config.json"
XRAY_BIN = "/usr/local/bin/xray"

xray_process = None

def generate_xray_config(inbounds_data):
    clients_vless = []
    clients_vmess = []
    clients_trojan = []

    for ib in inbounds_data:
        if not ib.get("enabled", True):
            continue
            
        uuid = ib["uuid"]
        # We use uuid as the email to track stats per user
        clients_vless.append({"id": uuid, "email": uuid})
        clients_vmess.append({"id": uuid, "email": uuid})
        clients_trojan.append({"password": uuid, "email": uuid})

    config = {
        "log": {"loglevel": "warning"},
        "api": {
            "tag": "api",
            "services": ["StatsService"]
        },
        "stats": {},
        "policy": {
            "levels": {
                "0": {
                    "statsUserUplink": True,
                    "statsUserDownlink": True
                }
            },
            "system": {
                "statsInboundUplink": True,
                "statsInboundDownlink": True
            }
        },
        "inbounds": [
            {
                "listen": "127.0.0.1",
                "port": 10085,
                "protocol": "dokodemo-door",
                "settings": {"address": "127.0.0.1"},
                "tag": "api"
            },
            {
                "listen": "127.0.0.1",
                "port": 10001,
                "protocol": "vless",
                "settings": {"clients": clients_vless, "decryption": "none"},
                "streamSettings": {"network": "ws", "wsSettings": {"path": "/vl-ws"}}
            },
            {
                "listen": "127.0.0.1",
                "port": 10002,
                "protocol": "vmess",
                "settings": {"clients": clients_vmess},
                "streamSettings": {"network": "ws", "wsSettings": {"path": "/vm-ws"}}
            },
            {
                "listen": "127.0.0.1",
                "port": 10003,
                "protocol": "trojan",
                "settings": {"clients": clients_trojan},
                "streamSettings": {"network": "ws", "wsSettings": {"path": "/tr-ws"}}
            },
            {
                "listen": "127.0.0.1",
                "port": 10004,
                "protocol": "vless",
                "settings": {"clients": clients_vless, "decryption": "none"},
                "streamSettings": {"network": "xhttp", "xhttpSettings": {"path": "/vl-xhttp"}}
            }
        ],
        "outbounds": [{"protocol": "freedom"}],
        "routing": {
            "rules": [
                {
                    "inboundTag": ["api"],
                    "outboundTag": "api",
                    "type": "field"
                }
            ]
        }
    }

    with open(XRAY_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def restart_xray():
    global xray_process
    if xray_process and xray_process.poll() is None:
        xray_process.terminate()
        try:
            xray_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            xray_process.kill()
    
    # Start Xray
    if os.path.exists(XRAY_BIN):
        xray_process = subprocess.Popen([XRAY_BIN, "run", "-c", XRAY_CONFIG_PATH])
    else:
        logging.warning("Xray binary not found. Running in mock/dev mode.")

previous_stats = {}

async def get_xray_stats():
    global previous_stats
    if not os.path.exists(XRAY_BIN):
        return {}
        
    try:
        proc = await asyncio.create_subprocess_exec(
            XRAY_BIN, "api", "statsquery", "--server=127.0.0.1:10085",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        out = stdout.decode("utf-8")
        
        deltas = {}
        import re
        matches = re.findall(r'name:\s*"([^"]+)"\s*value:\s*(\d+)', out)
        
        current_stats = {}
        for name, value in matches:
            parts = name.split(">>>")
            if len(parts) == 4 and parts[0] == "user" and parts[2] == "traffic":
                uuid = parts[1]
                direction = parts[3] # uplink or downlink
                val = int(value)
                
                if uuid not in current_stats:
                    current_stats[uuid] = {"up": 0, "down": 0}
                if direction == "uplink":
                    current_stats[uuid]["up"] += val
                elif direction == "downlink":
                    current_stats[uuid]["down"] += val

        for uuid, stats in current_stats.items():
            prev = previous_stats.get(uuid, {"up": 0, "down": 0})
            up_delta = stats["up"] - prev["up"]
            down_delta = stats["down"] - prev["down"]
            
            # If Xray restarted, value might be less than prev, just take current as delta
            if up_delta < 0: up_delta = stats["up"]
            if down_delta < 0: down_delta = stats["down"]
            
            if up_delta > 0 or down_delta > 0:
                deltas[uuid] = {"up": up_delta, "down": down_delta}
                
        previous_stats = current_stats
        return deltas
    except Exception as e:
        logging.error(f"Error querying Xray stats: {e}")
        return {}


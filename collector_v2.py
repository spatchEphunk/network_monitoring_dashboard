import csv
import time
from datetime import datetime
from pathlib import Path
from pysnmp.hlapi import *

# Replace these OIDs with the correct OIDs for each metric.
OIDS = {
    "total_utilization": "1.3.6.1.2.1.2.2.1.10.1",
    "port_1gb_utilization": "1.3.6.1.2.1.2.2.1.10.2",
    "port_10gb_utilization": "1.3.6.1.2.1.2.2.1.10.3",
    "backplane_utilization": "1.3.6.1.2.1.2.2.1.10.4",
    "current_speed": "1.3.6.1.2.1.2.2.1.5.1",
    "packet_forwarding_rate": "1.3.6.1.2.1.2.2.1.11.1"
}

def snmp_get(ip, community, oid):
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((ip, 161), timeout=5, retries=3),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )
    
    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    if errorIndication:
        print(f"Error fetching OID {oid}: {errorIndication}")
        return None
    elif errorStatus:
        print(f"{errorStatus.prettyPrint()} at {errorIndex}")
        return None
    else:
        for varBind in varBinds:
            value = varBind[1]
            try:
                # Convert to float if the response is numeric
                return float(value)
            except (ValueError, TypeError):
                # Handle non-numeric responses
                print(f"Non-numeric SNMP response for OID {oid}: {value}")
                return None

def collect_metrics(switch_ip, community="pysnmp"):
    timestamp = datetime.now().isoformat()
    metrics = {
        "Timestamp": timestamp,
        "Total Utilization (%)": snmp_get(switch_ip, community, OIDS["total_utilization"]),
        "1Gb Port Utilization (%)": snmp_get(switch_ip, community, OIDS["port_1gb_utilization"]),
        "10Gb Port Utilization (%)": snmp_get(switch_ip, community, OIDS["port_10gb_utilization"]),
        "Backplane Utilization (%)": snmp_get(switch_ip, community, OIDS["backplane_utilization"]),
        "Current Speed (Mbps)": snmp_get(switch_ip, community, OIDS["current_speed"]),
        "Packet Forwarding Rate (pps)": snmp_get(switch_ip, community, OIDS["packet_forwarding_rate"])
    }
    return metrics

def save_metrics_to_csv(metrics, switch_ip):
    filename = f"switch_metrics_{switch_ip}.csv"
    filepath = Path(filename)
    write_header = not filepath.exists()
    
    with open(filepath, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=metrics.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(metrics)

def main():
    switch_ip = "10.37.0.254"  # Replace with actual IP
    community = "pysnmp"  # Replace with the actual community string
    interval = 60  # Time in seconds between collections
    
    while True:
        metrics = collect_metrics(switch_ip, community)
        save_metrics_to_csv(metrics, switch_ip)
        print(f"Metrics collected at {metrics['Timestamp']} for IP {switch_ip}")
        time.sleep(interval)

if __name__ == "__main__":
    main()
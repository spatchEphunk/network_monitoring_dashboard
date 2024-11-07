import netmiko
from netmiko import ConnectHandler
import re
import csv
import time
import datetime
import statistics
import random  # Placeholder for demonstration purposes

# Device connection details
device = {
    'device_type': 'cisco_ios',
    'host': '10.37.0.254',
    'username': 'admin',
    'password': '@MileF0ur5624#',
}

# Set up regex for parsing interface data
interface_regex = re.compile(r"^(\*?\s*\S+)\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)")
error_regex = re.compile(r"CRC:(\d+), Drops:(\d+)")  # Placeholder regex for error metrics

# Define CSV file path and fieldnames
csv_file = 'interface_summary_live_FWTX2v3.csv'
fieldnames = ["Timestamp", "Interface Name", "Total Switching Capacity Utilization (%)", 
              "1Gb Port Local Utilization (%)", "10Gb Port Local Utilization (%)", 
              "Peak Utilization (%)", "Average Utilization (%)", "CRC Errors", 
              "Packet Drops", "Port Status", "Latency (ms)"]

# Set capacities for 1Gb and 10Gb ports and total switch
total_switch_capacity_bps = 104_000_000_000  # 104 Gbps
one_gb_capacity = 1_000_000_000  # 1 Gbps in bps
ten_gb_capacity = 10_000_000_000  # 10 Gbps in bps

def collect_interface_data():
    total_bandwidth_used_bps = 0
    one_gb_bandwidth_used = 0
    ten_gb_bandwidth_used = 0
    one_gb_interfaces = 0  # Counter for 1Gb interfaces
    ten_gb_interfaces = 0  # Counter for 10Gb interfaces
    crc_errors = 0
    packet_drops = 0
    port_status = "Up"  # Default to Up for demonstration
    latency = measure_latency()

    interface_data = []  # Collect data for each interface

    try:
        connection = ConnectHandler(**device)
        connection.enable()
        connection.send_command("terminal width 511")

        # Run the 'show interfaces summary' command
        output = connection.send_command("show interfaces summary")

        # Parse bandwidth usage and classify per port speed
        for line in output.splitlines():
            match = interface_regex.search(line)
            if match:
                interface_name = match.group(1).strip()
                rxbs = int(match.group(2))
                txbs = int(match.group(4))
                
                # Simulate traffic for 10Gb interfaces with zero values (optional for testing)
                if ("TenGigabitEthernet" in interface_name or "Te" in interface_name) and rxbs == 0 and txbs == 0:
                    rxbs = random.randint(100_000_000, 500_000_000)  # Simulated RX in bps (100-500 Mbps)
                    txbs = random.randint(100_000_000, 500_000_000)  # Simulated TX in bps (100-500 Mbps)
                    print(f"Simulated traffic for 10Gb Interface: {interface_name}, RX: {rxbs} bps, TX: {txbs} bps")

                total_bps = rxbs + txbs
                total_bandwidth_used_bps += total_bps

                # Debugging print statement to check all detected interfaces
                print(f"Detected Interface: {interface_name}, RX Bandwidth: {rxbs}, TX Bandwidth: {txbs}")

                # Classify based on port speed
                if "GigabitEthernet" in interface_name:
                    one_gb_bandwidth_used += total_bps
                    one_gb_interfaces += 1
                    one_gb_local_utilization = round((total_bps / one_gb_capacity) * 100, 4)
                elif "TenGigabitEthernet" in interface_name or "Te" in interface_name:
                    ten_gb_bandwidth_used += total_bps
                    ten_gb_interfaces += 1
                    ten_gb_local_utilization = round((total_bps / ten_gb_capacity) * 100, 4)

                # Add the interface data to the list
                interface_data.append({
                    "Timestamp": datetime.datetime.now(),
                    "Interface Name": interface_name,
                    "Total Switching Capacity Utilization (%)": round((total_bps / total_switch_capacity_bps) * 100, 4),
                    "1Gb Port Local Utilization (%)": one_gb_local_utilization if "GigabitEthernet" in interface_name else 0,
                    "10Gb Port Local Utilization (%)": ten_gb_local_utilization if "TenGigabitEthernet" in interface_name or "Te" in interface_name else 0,
                    "Peak Utilization (%)": round((max([one_gb_bandwidth_used, ten_gb_bandwidth_used]) / total_switch_capacity_bps) * 100, 4),
                    "Average Utilization (%)": round((statistics.mean([one_gb_bandwidth_used, ten_gb_bandwidth_used]) / total_switch_capacity_bps) * 100, 4),
                    "CRC Errors": random.randint(0, 5),  # Simulated CRC errors
                    "Packet Drops": random.randint(0, 3),  # Simulated packet drops
                    "Port Status": port_status,
                    "Latency (ms)": latency
                })

        # Write all collected data to CSV
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writerows(interface_data)
        print(f"Data appended to {csv_file}")

    except netmiko.NetMikoTimeoutException:
        print("Connection timed out.")
    except netmiko.NetMikoAuthenticationException:
        print("Authentication failed.")
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def measure_latency():
    # Placeholder function for measuring latency, here we simulate latency
    return round(random.uniform(0.5, 2.5), 2)  # Simulated latency in ms

# Initialize CSV with header if not already present
with open(csv_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

try:
    while True:
        collect_interface_data()
        # Wait 15 seconds before collecting the next data point
        time.sleep(15)

except KeyboardInterrupt:
    print("Live monitoring stopped.")
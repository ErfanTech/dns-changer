import subprocess
import psutil
import shlex
from dns_config import dnsServers

def get_current_dns():
    try:
        # Execute the nslookup command to retrieve the current DNS servers
        command = "nslookup localhost"
        result = subprocess.run(command, capture_output=True, text=True)

        # Check if the command was successful
        if result.returncode == 0:
            # Find lines containing "Server:" and "Addresses:"
            server_lines = [line for line in result.stdout.splitlines() if "Server:" in line]
            address_lines = [line for line in result.stdout.splitlines() if "Address:" in line]

            # Print the Server and IP addresses together
            for server_line, address_line in zip(server_lines, address_lines):
                server = server_line.split(":")[1].strip()
                ip_addresses = address_line.split(":")[1].strip()
                print(f"Server: {server}, Address: {ip_addresses}")
        else:
            print(f"Error occurred while retrieving current DNS servers:\n{result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while executing the command: {e}")


def get_active_adapter():
    try:
        for intface, addr_list in psutil.net_if_addrs().items():
            stats = psutil.net_if_stats()
            if intface in stats and getattr(stats[intface], "isup"):
                return intface
    except Exception as e:
        print(f"Error occurred while getting active adapter: {e}")

    return None

def set_dns(dns1, dns2):
    adapter_description = get_active_adapter()
    if adapter_description is None:
        print("No active network adapter found.")
        return

    try:
        # Prepare the command with shlex to handle special characters
        command1 = f"netsh interface ip set dns name=\"{adapter_description}\" source=static address={dns1} register=PRIMARY"
        command2 = f"netsh interface ip add dns name=\"{adapter_description}\" address={dns2} index=2"

        # Execute the commands using subprocess
        result1 = subprocess.run(shlex.split(command1), capture_output=True, text=True)
        result2 = subprocess.run(shlex.split(command2), capture_output=True, text=True)

        # Check for errors and print the output if there is an error
        if result1.returncode != 0:
            print(f"Error occurred while setting DNS 1:\n{result1.stdout}")
        if result2.returncode != 0:
            print(f"Error occurred while setting DNS 2:\n{result2.stdout}")

        print(f"DNS servers set for adapter '{adapter_description}'")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while setting DNS: {e}")

def clear_dns():
    adapter_description = get_active_adapter()
    if adapter_description is None:
        print("No active network adapter found.")
        return

    try:
        # Clear DNS settings and use automatic (DHCP) settings
        command = f"netsh interface ip set dns name=\"{adapter_description}\" source=dhcp"
        result = subprocess.run(shlex.split(command), capture_output=True, text=True)

        # Check for errors and print the output if there is an error
        if result.returncode != 0:
            print(f"Error occurred while clearing DNS settings:\n{result.stdout}")
        else:
            print(f"DNS servers cleared for adapter '{adapter_description}'")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while clearing DNS settings: {e}")

def print_dns_options():
    print("Available DNS Server Options:")
    for index, (dns_option, dns_ips) in enumerate(dnsServers.items(), start=1):
        print(f"{index}. {dns_option} ({', '.join(dns_ips)})")
    print(f"{len(dnsServers) + 1}. Clear DNS and use automatic (DHCP)")

def get_dns_option():
    while True:
        try:
            print_dns_options()
            option = int(input(f"Select a DNS Server Option (1-{len(dnsServers) + 1}): "))
            if 1 <= option <= len(dnsServers):
                dns_option = list(dnsServers.values())[option - 1]
                return dns_option
            elif option == len(dnsServers) + 1:
                return "dhcp"
            else:
                print("Invalid option. Please select a valid option.")
        except ValueError:
            print("Invalid input. Please enter a number (1-{len(dnsServers) + 1}).")

if __name__ == "__main__":
    print("Current DNS:")
    get_current_dns()
    dns_option = get_dns_option()

    if dns_option == "dhcp":
        clear_dns()
    else:
        dns1, dns2 = dns_option[0], dns_option[1]
        set_dns(dns1, dns2)

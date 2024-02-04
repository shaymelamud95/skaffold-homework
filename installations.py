import platform
import subprocess
import sys

def run_as_admin():
    # Re-run the script with administrative privileges
    subprocess.run(["powershell.exe", "-Command", "Start-Process", "python", "-ArgumentList", f'"{__file__}"', "-Verb", "RunAs"])

def install_chocolatey():
    print("Installing Chocolatey...")
    subprocess.run(["powershell.exe", "-Command", r"Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"])

def install_skaffold():
    print("Installing Skaffold...")
    subprocess.run(["choco", "install", "skaffold", "-y"])

def install_kind():
    try:
        # Check if Kind is already installed
        subprocess.run(["kind", "version"], check=True)
        print("Kind is already installed.")
    except FileNotFoundError:
        # Install Kind using Chocolatey
        print("Installing Kind...")
        subprocess.run(["choco", "install", "kind", "-y"])
        print("Kind installed successfully.")

# def install_helm():
#     print("Installing Helm...")
#     subprocess.run(["choco", "install", "kubernetes-helm", "-y"])

# def add_helm_repos():
#     print("Adding Helm repositories...")
#     subprocess.run(["helm", "repo", "add", "prometheus-community", "https://prometheus-community.github.io/helm-charts"])
#     subprocess.run(["helm", "repo", "update"])
#     subprocess.run(["helm", "repo", "add", "grafana", "https://grafana.github.io/helm-charts"])
#     subprocess.run(["helm", "repo", "update"])

# def install_and_expose_services():
#     print("Installing and exposing services...")
#     subprocess.run(["helm", "install", "prometheus", "prometheus-community/prometheus"])
#     subprocess.run(["helm", "install", "grafana", "grafana/grafana"])
#     subprocess.run(["kubectl", "expose", "service", "prometheus-server", "--type=NodePort", "--target-port=9090", "--name=prometheus-server-ext"])
#     subprocess.run(["kubectl", "expose", "service", "grafana", "--type=NodePort", "--target-port=3000", "--name=grafana-ext"])

def main():
    print(platform.system())

    if sys.platform == "win32":  # Windows
        print("This script will install Chocolatey, Skaffold, Helm, and configure Helm repositories.")
        print("Automatically answering 'Yes' to confirmation prompt.")
        
        try:
            install_chocolatey()
            install_skaffold()
            install_kind()
            # I didnt work with helm yet
            # install_helm()
            # add_helm_repos()
            # install_and_expose_services()
        except PermissionError:
            print("Running as administrator...")
            run_as_admin()
    elif sys.platform == "darwin":  # macOS
        # Add macOS specific commands here
        pass
    else:  # Assume Linux
        # Add Linux specific commands here
        pass

    # Define the commands for prometheus stack 
    kind_create_command = ["kind", "create", "cluster", "--name", "monitoring", "--config", "prometheus-stack-kub-1.28/kind.yaml"]
    kubectl_setup_command = ["kubectl", "create", "-f", "./prometheus-stack-kub-1.28/manifests/setup/"]
    kubectl_prometheus_command = ["kubectl", "create", "-f", "./prometheus-stack-kub-1.28/manifests/"]
    port_forward_grafana_command = ["kubectl", "-n", "monitoring", "port-forward", "svc/grafana", "3000"]
    port_forward_prometheus_command = ["kubectl", "-n", "monitoring", "port-forward", "svc/prometheus-operated", "9090"]

    # Execute the commands
    subprocess.run(kind_create_command, shell=True)
    subprocess.run(kubectl_setup_command, shell=True)
    subprocess.run(kubectl_prometheus_command, shell=True)
    subprocess.run(port_forward_grafana_command, shell=True)
    subprocess.run(port_forward_prometheus_command, shell=True)

if __name__ == "__main__":
    main()

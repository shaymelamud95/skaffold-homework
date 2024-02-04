import os
import subprocess
import shutil

def get_user_input():
    app_name = input("Enter the app name: ")
    code_language = input("Enter the code language: ")
    ports = input("Enter the ports to open from the container (comma-separated): ")
    base_image_url = input("Enter the base image URL: ")
    metrics_to_collect = input("Enter the metrics to collect for Prometheus (comma-separated): ")

    return app_name, code_language, ports, base_image_url, metrics_to_collect

def generate_files(app_name, code_language, ports, base_image_url, metrics_to_collect):
    # Check if the directory already exists
    if os.path.exists(app_name):
        # Delete the existing directory
        shutil.rmtree(app_name)
        print(f"Deleted existing directory: {app_name}")

    # Create app folder
    os.makedirs(app_name)
    os.chdir(app_name)

    # Generate standard files
    open(f"main.{code_language}", 'a').close()  # Placeholder for the main code file
    open("README.md", 'a').close()

    # Generate Dockerfile
    dockerfile_content = f'''
FROM {base_image_url}
EXPOSE {ports}

RUN mkdir /{app_name}/
# WORKDIR /{app_name}/

# Copy everything under ./{app_name} to /{app_name}/
COPY ./{app_name} /{app_name}/

# Set the working directory to /{app_name}/
WORKDIR /{app_name}/

# Generic CMD based on code language
CMD ["{code_language}", "./main.{code_language}"]
'''
    with open("Dockerfile", 'w') as dockerfile:
        dockerfile.write(dockerfile_content)

    # Generate ServiceMonitor YAML
    servicemonitor_yaml_content = f'''
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  labels:
    name: {app_name}
  namespace: default
spec:
  endpoints:
  - interval: 30s
    port: web
  selector:
    matchLabels:
      app: {app_name}
'''

    with open(f"servicemonitor-{app_name}.yaml", 'w') as servicemonitor_yaml:
        servicemonitor_yaml.write(servicemonitor_yaml_content)


    # Generate Prometheus configuration
    prometheus_config_content = f'''
global:
  scrape_interval: 15s
 
scrape_configs:
  - job_name: '{app_name}'
    static_configs:
      - targets: ['localhost:{ports}']
    metrics_path: /metrics
    '''
    with open("prometheus.yml", 'w') as prometheus_config:
        prometheus_config.write(prometheus_config_content)

    # Generate Kubernetes deployment manifest
    deployment_content = f'''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {app_name}
  template:
    metadata:
      labels:
        app: {app_name}
    spec:
      containers:
      - name: {app_name}
        image: {app_name}:latest
        imagePullPolicy: Always
        ports:
        - containerPort: {ports}
    '''
    # Ensure the 'k8s' directory exists
    os.makedirs("k8s", exist_ok=True)

    with open(f"k8s/{app_name}.yaml", 'w') as deployment_file:
        deployment_file.write(deployment_content)

  # Generate service for monitoring
    app_service_content = f"""
  apiVersion: v1
kind: Service
metadata:
  name: {app_name}
  labels:
    app: {app_name}
spec:
  type: NodePort
  selector:
    app: {app_name}
  ports:
  - name: web
    port: 8082
  """
    with open(f"k8s/service-{app_name}.yaml", 'w') as app_service_file:
        app_service_file.write(app_service_content)

    # Generate Skaffold.yaml inside the app directory
    skaffold_content = f'''
apiVersion: skaffold/v4beta9
kind: Config
metadata:
  name: {app_name}
build:
  artifacts:
    - image: {app_name}
      docker:
        dockerfile: Dockerfile
manifests:
  rawYaml:
    - k8s/{app_name}.yaml
profiles:
- name: {app_name}
    '''
    with open("skaffold.yaml", 'w') as skaffold_config:
        skaffold_config.write(skaffold_content)


if __name__ == "__main__":
    # Run the installations -- I installed with Chocolatey
    # subprocess.run(['python', "installations.py"], check=True)

    # app_name, code_language, ports, base_image_url, metrics_to_collect = get_user_input()
    app_name, code_language, ports, base_image_url, metrics_to_collect = ["shays-app2", "py","8083", "python:3.8-alpine", "http_requests_total,http_request_duration_seconds,cpu_usage,mem_usage"]
    generate_files(app_name, code_language, ports, base_image_url, metrics_to_collect)

    # kubectl apply -n monitoring -f ./kubernetes/servicemonitors/prometheus.yaml
    subprocess.run(["kubectl", "apply", "-n", "monitoring", "-f", "prometheus.yml"])

    # kubectl -n monitoring port-forward prometheus-applications-0 9090
    subprocess.run(["kubectl", "-n", "monitoring", "port-forward", "prometheus-applications-0", "9090"])

    # kubectl apply app service
    subprocess.run(["kubectl", "-n", "default", "apply", "-f", "./k8s/service-{app_name}.yaml"])

    # kubectl apply servicemonitor
    subprocess.run(["kubectl", "-n", "default", "apply", "-f", "./k8s/servicemonitor.yaml"])
    
    
  

from kubernetes import config, client

def get_previous_pod_logs(namespace, pod_name, container_name):
    try:
        # Load the Kubernetes configuration from the default location or specify the path to your kubeconfig file.
        config.load_kube_config()

        # Create a Kubernetes API client.
        api_client = client.CoreV1Api()

        # Get the pod object for the specified pod name and namespace.
        pod = api_client.read_namespaced_pod(name=pod_name, namespace=namespace)

        # Find the previous terminated container with the specified container name.
        previous_terminated_containers = [
            c for c in pod.status.container_statuses if c.state and c.state.terminated
        ]
        previous_terminated_container = next(
            (c for c in previous_terminated_containers if c.name == container_name), None
        )

        if not previous_terminated_container:
            print(f"No previous terminated container with name '{container_name}' found.")
            return

        # Get the logs of the previous terminated container.
        previous_logs = api_client.read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            container=container_name,
            previous=True,
        )

        return previous_logs

    except Exception as e:
        print(f"Error: {e}")
        return None

# Example usage:
namespace = "your-namespace"
pod_name = "your-pod-name"
container_name = "your-container-name"

previous_logs = get_previous_pod_logs(namespace, pod_name, container_name)

if previous_logs:
    print(f"Previous logs for container '{container_name}' in pod '{pod_name}':")
    print(previous_logs)
else:
    print("Logs not found for the specified pod or container.")

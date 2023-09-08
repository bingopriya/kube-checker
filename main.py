from kubernetes import client, config
import sys
import logging as lg
import configparser

k8_config = config.load_kube_config()
v1_pod = client.CoreV1Api()
v2_hpa = client.AutoscalingV1Api()
v3_deployment = client.AppsV1Api()

lg.basicConfig(filename="pod.logs",
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=lg.DEBUG)


env_var = {}

def read_config_file(file_path):
    file_config = configparser.ConfigParser()
    file_config.sections()
    try:
        file_config.read(file_path)
        return(file_config["default"])
                 
    except FileNotFoundError:
        print(f"Configuration file not found: {file_path}")
        return None


default_config = (read_config_file("kube.conf"))


def tail_output(pod_log, num_lines):
    output_lines = pod_log.splitlines()
    return output_lines[-num_lines:]


# Writing logs into the log file


# Get all pods in the given namespace
def get_pods_in_namespace(namespace):
    pods = v1_pod.list_namespaced_pod(namespace = namespace)
    return (pods)


# Get restarted pod log in the given namespace
def print_restarted_pod_logs():
    pods = get_pods_in_namespace(str(default_config["namespace"]))
    try:
        lg.info("The Following pods are restarted ")
        lg.info()
        for pod in pods.items:
            if (pod.status.container_statuses[0].restart_count) > 0:
                pod_logging = v1_pod.read_namespaced_pod_log(name = pod.metadata.name, namespace = pod.metadata.namespace, previous = True)
                lg.warning("Logs of {}".format(pod.metadata.name))
                lg.info("***************************************")
                lg.info(tail_output(pod_logging, num_lines=int(default_config["log_lines_count"])))
                lg.info()
    except Exception as e:
        lg.error(f"Error: {e}")
        return None



#Get horizontal pod autoscaler in the given namespace
def get_hp_autoscaler(namespace):

    hpas = v2_hpa.list_namespaced_horizontal_pod_autoscaler(namespace)
    print("*******The following pods are scaled to maximum*****")
    print()
    print("HPA Name\t\t\t\tCurrent replicas\t\tMaximum reached")
    for hpa in hpas.items:
        if hpa.spec.max_replicas == 1:
            pass
            # print ("{} \t 1".format(hpa.spec.scale_target_ref.name))
        else:
            if hpa.spec.max_replicas == hpa.status.current_replicas:
                print ("{}\t\t\t{}\t\t\t {}".format(hpa.spec.scale_target_ref.name, hpa.status.current_replicas, hpa.spec.max_replicas))

print(get_hp_autoscaler(str(default_config["namespace"])))
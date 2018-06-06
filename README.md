# Sentiment Analysis - Kubernetes Demo

This is a simple python app that analyzes sentiments in input sentences, using the Google Cloud Natural Language API.
This app was used as part of a Kubernetes demo.

## Running the app on your computer
**Prerequisites:**
[Docker](https://docs.docker.com/install/)
[Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
[Enable Cloud Natural Language API on a project in GCP](https://cloud.google.com/natural-language/docs/quickstart#set_up_a_project)

First, lets clone this repo and switch to the directory with all our files.
```
git clone git@github.com:niharathomas/ks8-sentiment-analysis.git
cd ks8-sentiment-analysis
```

Next, we'll build a docker image
`docker build -t k8s-sentiment-analysis .`

**Minikube setup:**
Install [minikube](https://github.com/kubernetes/minikube)

Start minikube: `minikube start`
You should see an output that looks something like this:
```
Starting local Kubernetes v1.10.0 cluster...
Starting VM...
Getting VM IP address...
Moving files into cluster...
Setting up certs...
Connecting to cluster...
Setting up kubeconfig...
Starting cluster components...
Kubectl is now configured to use the cluster.
Loading cached images from config file.
```

Minikube is now ready for use!

Now we're going to create some Kubernetes objects using the config files in the k8s_config directory.
(For the steps below, make sure you're in the k8s_config directory or change the file name to the path to where you have your ks config files.)

Create a K8s Configmap:
`kubectl create -f config_map.yaml`

Create a K8s deployment object:
`kubectl create -f deployment.yaml`

Verify that a deployment object was created:
`kubectl get deploy`

The deployment should have also created a ReplicaSet. Let's look for it.
`kubectl get rs`

And the ReplicaSet should have created a Pod with our container running:
`kubectl get po`

Note:
If your pod is up and running fine, the command above should have "Running" under the status column. If your pod is not "Running", this is how you would debug it:
Copy the name of the pod from the command above.
`kubectl describe po/<<insert_pod_name>>`
To look at logs from the pod:
`kubectl logs po/<<insert_pod_name>>`

Now that we have create our deployment object and have a pod up and running, let's create a service:
`kubectl create -f service.yaml`

Let's make sure that the service is up and running:
`kubectl get svc`

Now lets try hitting our app running on minikube

Get the URL to access the app via the K8s service object:
`minikube service sentiment-analysis --url`

Access the app:
```
curl $(minikube service sentiment-analysis --url)/status 
curl -X POST -d '{"data": "Happy happy day. Sad panda."}' -H "Content-Type: application/json" $(minikube service sentiment-analysis --url)/analyze 
```

Exec into the running pod and look for the volume that was created using the ConfigMap:
```
kubectl exec -it <<insert_pod_name>> bash
cd /sentiment-analysis
cat greeting
```


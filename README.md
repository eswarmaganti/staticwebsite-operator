# Kubernetes StaticWebsite Operator 

## The project structure

```commandline
.
├── Dockerfile
├── README.md
├── kubernetes
│   ├── crd
│   │   └── staticwebsite-crd.yaml
│   ├── deployment
│   │   ├── operator.yaml
│   │   └── secret.yaml
│   ├── rbac
│   │   ├── clusterrole.yaml
│   │   ├── clusterrolebinding.yaml
│   │   └── serviceaccount.yaml
│   └── sample
│       └── website.yaml
├── pytest.ini
├── requirements-dev.txt
├── requirements.txt
├── sw_operator
│   ├── __init__.py
│   ├── builders
│   │   ├── __init__.py
│   │   ├── configmap.py
│   │   ├── deployment.py
│   │   ├── gateway.py
│   │   ├── owner_reference.py
│   │   └── service.py
│   ├── clients
│   │   ├── __init__.py
│   │   └── kubernetes.py
│   ├── config.py
│   ├── handlers
│   │   ├── __init__.py
│   │   └── main.py
│   ├── main.py
│   ├── reconcilers
│   │   ├── __init__.py
│   │   ├── deployment.py
│   │   ├── gateway.py
│   │   ├── service.py
│   │   ├── staticwebsite.py
│   │   └── status.py
│   └── utils
│       ├── __init__.py
│       └── main.py
└── tests
    ├── __init__.py
    ├── builders
    │   ├── __init__.py
    │   ├── test_deployment.py
    │   ├── test_gateway.py
    │   └── test_service.py
    └── conftest.py
```

## Deploying the operator locally

### Prerequisites
- A local Kubernetes cluster running (minikube/kind)
- `kubectl` installed and configured against your cluster
- `python 3.8+` and `pip` available
- Clone the source code repo
```commandline
git clone https://github.com/eswarmaganti/staticwebsite-operator.git
cd staticwebsite-operator
```
- Set up the python virtual environment
```commandline
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### Install the CRD
```commandline
$ kubectl apply -f kubernetes/crd/staticwebsite-crd.yaml 
customresourcedefinition.apiextensions.k8s.io/staticwebsites.platform.eswar.dev created

$kubectl get crd | grep static
staticwebsites.platform.eswar.dev                     2026-06-06T02:00:49Z
```

### Running the Operator locally
```commandline
$ export PYTHONPATH=$(pwd)

$ kopf run -m sw_operator.main --all-namespaces
[2026-06-06 07:33:32,814] kopf.activities.star [INFO    ] Activity 'configure' succeeded.
[2026-06-06 07:33:32,815] kopf._core.engines.a [INFO    ] Initial authentication has been initiated.
[2026-06-06 07:33:32,817] kopf.activities.auth [INFO    ] Activity 'login_via_client' succeeded.
[2026-06-06 07:33:32,817] kopf._core.engines.a [INFO    ] Initial authentication has finished.
```

### Deploy a sample CR
```commandline
$ kubectl apply -f kubernetes/sample/website.yaml
staticwebsite.platform.eswar.dev/portfolio created
```

### Watch the operator logs
```commandline
# Reconciler runs — child resources created in sequence
[2026-06-06 07:40:07,570] kopf.objects         [INFO    ] [test/portfolio] Deployment: portfolio created
[2026-06-06 07:40:07,615] kopf.objects         [INFO    ] [test/portfolio] Service: portfolio created
[2026-06-06 07:40:07,676] kopf.objects         [INFO    ] [test/portfolio] Gateway: portfolio created
[2026-06-06 07:40:07,714] kopf.objects         [INFO    ] [test/portfolio] HTTPRoute: portfolio created

# Main handler completes successfully
[2026-06-06 07:40:07,715] kopf.objects         [INFO    ] [test/portfolio] Handler 'create_staticwebsite' succeeded.
[2026-06-06 07:40:07,716] kopf.objects         [INFO    ] [test/portfolio] Creation is processed: 1 succeeded; 0 failed.

# Field watcher fires as first pod becomes available (1/2 ready)
# Phase is still 'Progressing' - not all replicas are available yet
[2026-06-06 07:40:09,581] kopf.objects         [INFO    ] [test/portfolio] Syncing status: phase=Progressing, available/desired=1/2, ready=1
[2026-06-06 07:40:09,607] kopf.objects         [INFO    ] [test/portfolio] CR: portfolio Status sync is successfully completed
[2026-06-06 07:40:09,607] kopf.objects         [INFO    ] [test/portfolio] Handler 'status/status.availableReplicas' succeeded.
[2026-06-06 07:40:09,607] kopf.objects         [INFO    ] [test/portfolio] Creation is processed: 1 succeeded; 0 failed.

# Field watcher fires again as second pod becomes available (2/2 ready)
# Phase transitions to 'Ready' - desired state fully achieved
[2026-06-06 07:40:09,625] kopf.objects         [INFO    ] [test/portfolio] Syncing status: phase=Ready, available/desired=2/2, ready=2
[2026-06-06 07:40:09,642] kopf.objects         [INFO    ] [test/portfolio] CR: portfolio Status sync is successfully completed
[2026-06-06 07:40:09,643] kopf.objects         [INFO    ] [test/portfolio] Handler 'status/status.availableReplicas' succeeded.
[2026-06-06 07:40:09,644] kopf.objects         [INFO    ] [test/portfolio] Updating is processed: 1 succeeded; 0 failed.
```

### Verify the child resources

```commandline
$ kubectl get all -n test -l app.kubernetes.io/managed-by=staticwebsite-operator
NAME                             READY   STATUS    RESTARTS   AGE
pod/portfolio-7bf55f9d76-cq9pq   1/1     Running   0          17m
pod/portfolio-7bf55f9d76-k6kd9   1/1     Running   0          17m

NAME                TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
service/portfolio   NodePort   10.96.230.79   <none>        80:31321/TCP   17m

NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/portfolio   2/2     2            2           17m

NAME                                   DESIRED   CURRENT   READY   AGE
replicaset.apps/portfolio-7bf55f9d76   2         2         2       17m

$ kubectl get httproute,gateway -n test
NAME                                            HOSTNAMES                   AGE
httproute.gateway.networking.k8s.io/portfolio   ["portfolio.eswar.local"]   18m

NAME                                          CLASS   ADDRESS   PROGRAMMED   AGE
gateway.gateway.networking.k8s.io/portfolio   nginx             True         18m
```
### Check the CR status
```commandline
$kubectl get sw/portfolio -n test
NAME        IMAGE               REPLICAS   DOMAIN                  PHASE   AGE
portfolio   nginx:1.31-alpine   2          portfolio.eswar.local   Ready   15s
```

### Update Scenario — Scaling Replicas from 2 to 3
```commandline
$ kubectl patch sw/portfolio --type merge -p '{"spec": {"replicas": 3}}' -n test
staticwebsite.platform.eswar.dev/portfolio patched
```

#### Operator logs
```commandline
# Reconciler runs — all child resources are patched to reflect the new desired state
# Notice "reconciled" instead of "created" — this is the idempotency pattern:
# resources already exist, so the 409 conflict path patches them instead of creating
[2026-06-06 08:08:29,219] kopf.objects         [INFO    ] [test/portfolio] Deployment: portfolio reconciled
[2026-06-06 08:08:29,258] kopf.objects         [INFO    ] [test/portfolio] Service: portfolio reconciled
[2026-06-06 08:08:29,316] kopf.objects         [INFO    ] [test/portfolio] Gateway: portfolio reconciled
[2026-06-06 08:08:29,342] kopf.objects         [INFO    ] [test/portfolio] HTTPRoute: portfolio reconciled

# Main handler completes - reconciliation took under 200ms
[2026-06-06 08:08:29,343] kopf.objects         [INFO    ] [test/portfolio] Handler 'create_staticwebsite' succeeded.
[2026-06-06 08:08:29,343] kopf.objects         [INFO    ] [test/portfolio] Updating is processed: 1 succeeded; 0 failed.

# Field watcher fires again as third pod becomes available (3/3 ready)
# Phase transitions to 'Ready' - desired state fully achieved
[2026-06-06 08:08:30,130] kopf.objects         [INFO    ] [test/portfolio] Syncing status: phase=Ready, available/desired=3/3, ready=3
[2026-06-06 08:08:30,152] kopf.objects         [INFO    ] [test/portfolio] CR: portfolio Status sync is successfully completed
[2026-06-06 08:08:30,153] kopf.objects         [INFO    ] [test/portfolio] Handler 'status/status.availableReplicas' succeeded.
[2026-06-06 08:08:30,153] kopf.objects         [INFO    ] [test/portfolio] Updating is processed: 1 succeeded; 0 failed.
```

#### Verify the running pods
```commandline
$ kubectl get pods -n test -l app.kubernetes.io/managed-by=staticwebsite-operator
NAME                         READY   STATUS    RESTARTS   AGE
portfolio-7bf55f9d76-7drqm   1/1     Running   0          3m44s
portfolio-7bf55f9d76-7jhlz   1/1     Running   0          3m44s
portfolio-7bf55f9d76-jgs95   1/1     Running   0          3m5s
```

### Delete scenario
```commandline
$ kubectl delete sw/portfolio -n test
staticwebsite.platform.eswar.dev "portfolio" deleted from test namespace
```

```commandline
$ kubectl get all -n test -l app.kubernetes.io/managed-by=staticwebsite-operator
No resources found in test namespace.

$ kubectl get httproute,gateway -n test
No resources found in test namespace.
```
# Kubernetes StaticWebsite Operator 

> Building a kubernetes operator to handle the deployment and lifecycle of a static website using nginx image

## The Operator project structure
```bash
 (base) eswarmaganti~$tree -I '__pycache__' sw_operator


sw_operator
├── __init__.py
├── builders
│   ├── __init__.py
│   ├── configmap.py
│   ├── deployment.py
│   ├── gateway.py
│   ├── owner_reference.py
│   └── service.py
├── clients
│   ├── __init__.py
│   └── kubernetes.py
├── config.py
├── handlers
│   ├── __init__.py
│   ├── create.py
│   └── update.py
├── main.py
├── reconcilers
│   ├── __init__.py
│   ├── deployment.py
│   ├── service.py
│   ├── staticwebsite.py
│   └── status.py
└── utils
    ├── __init__.py
    └── main.py

6 directories, 21 files
```

## Testing the operator package in local

1. Run the operator package using `kopf` commandline
```bash
(env) (base) eswarmaganti~$kopf run -m sw_operator.main
/Users/eswarmaganti/Developer/Projects/DevOps/staticwebsite-operator/env/lib/python3.12/site-packages/kopf/_core/reactor/running.py:179: FutureWarning: Absence of either namespaces or cluster-wide flag will become an error soon. For now, switching to the cluster-wide mode for backward compatibility.
  warnings.warn("Absence of either namespaces or cluster-wide flag will become an error soon."
[2026-06-02 06:29:37,720] kopf._core.engines.a [INFO    ] Initial authentication has been initiated.
[2026-06-02 06:29:37,723] kopf.activities.auth [INFO    ] Activity 'login_via_client' succeeded.
[2026-06-02 06:29:37,723] kopf._core.engines.a [INFO    ] Initial authentication has finished.
```

2. Deploy the `StaticWebsite` custom resource

- The `StaticWebsite` CRD
```yaml
---
apiVersion: apiextensions.k8s.io/v1 # the api version for CRDs
kind: CustomResourceDefinition
metadata:
  name: staticwebsites.platform.eswar.dev # it should be <plural> + <api group>

spec:
  group: platform.eswar.dev # The group name of the CR
  scope: Namespaced # the CR exists inside a namespace
  names: # defines the kubectl behaviour
    plural: staticwebsites
    singular: staticwebsite
    kind: StaticWebsite
    shortNames:
      - sw
  versions:
    - name: v1alpha1
      served: true # the API server serves this version
      storage: true # the version stored in etcd

      schema: # the CR schema for validation
        openAPIV3Schema:
          type: object # root object - the CR is a object
          properties:

            spec:
              type: object
              properties:
                image:
                  type: string
                replicas:
                  type: integer
                  minimum: 1
                  maximum: 10
                domain:
                  type: string
                port:
                  type: integer
                  minimum: 1
                  maximum: 65535
                targetPort:
                  type: integer
                  minimum: 1
                  maximum: 65535
              required: # mandatory fields allowed
                - image
                - replicas
                - port
                - targetPort

            status:
              type: object
              properties:
                phase:
                  type: string
                deploymentName:
                  type: string
                serviceName:
                  type: string

      additionalPrinterColumns: # useful to specify which fields to be displayed in the output of `kubectl get` commands
        - name: Image
          type: string
          jsonPath: .spec.image
        - name: Replicas
          type: integer
          jsonPath: .spec.replicas
        - name: Domain
          type: string
          jsonPath: .spec.domain
```
- The CR manifest
```yaml
#
# The yaml manifest to create a custom resource for StaticWebsite CRD
#
---
apiVersion: platform.eswar.dev/v1alpha1
kind: StaticWebsite
metadata:
  name: my-nginx-sw
spec:
  image: nginx:1.31-alpine
  replicas: 2
  port: 80
  targetPort: 80
  domain: portfolio.eswar.dev
```

```bash
(env) (base) eswarmaganti~$kubectl apply -f website.yaml                                                
staticwebsite.platform.eswar.dev/my-nginx-sw created
(env) (base) eswarmaganti~$kubectl get all                                                              
NAME                               READY   STATUS    RESTARTS   AGE
pod/my-nginx-sw-6d7cf86d55-n7m26   1/1     Running   0          2s
pod/my-nginx-sw-6d7cf86d55-zrbvm   1/1     Running   0          2s

NAME                  TYPE       CLUSTER-IP    EXTERNAL-IP   PORT(S)        AGE
service/my-nginx-sw   NodePort   10.96.99.40   <none>        80:31203/TCP   2s

NAME                          READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/my-nginx-sw   2/2     2            2           2s

NAME                                     DESIRED   CURRENT   READY   AGE
replicaset.apps/my-nginx-sw-6d7cf86d55   2         2         2       2s
```
3. Validate the logs from operator
```bash
[2026-06-02 06:29:45,880] kopf.objects         [INFO    ] [test/my-nginx-sw] Creating the deployment: my-nginx-sw
[2026-06-02 06:29:45,888] kopf.objects         [INFO    ] [test/my-nginx-sw] Created the deployment: my-nginx-sw
[2026-06-02 06:29:45,897] kopf.objects         [INFO    ] [test/my-nginx-sw] Creating the service my-nginx-sw
[2026-06-02 06:29:45,919] kopf.objects         [INFO    ] [test/my-nginx-sw] Created the service my-nginx-sw
[2026-06-02 06:29:45,928] kopf.objects         [INFO    ] [test/my-nginx-sw] Handler 'create_staticwebsite' succeeded.
[2026-06-02 06:29:45,928] kopf.objects         [INFO    ] [test/my-nginx-sw] Creation is processed: 1 succeeded; 0 failed.
[2026-06-02 06:29:45,963] kopf.objects         [WARNING ] [test/my-nginx-sw] Merge-patching finished with inconsistencies: (('remove', ('status', 'availableReplicas'), 0, None), ('remove', ('status', 'readyReplicas'), 0, None), ('remove', ('status', 'replicas'), 0, None))
```
4. Validate the patch operation on the Custom Resource
```bash
(env) (base) eswarmaganti~$kubectl patch sw/my-nginx-sw --type=merge --patch '{"spec": {"replicas": 3}}'
staticwebsite.platform.eswar.dev/my-nginx-sw patched
(env) (base) eswarmaganti~$kubectl get all                                                              
NAME                               READY   STATUS    RESTARTS   AGE
pod/my-nginx-sw-6d7cf86d55-n7m26   1/1     Running   0          37s
pod/my-nginx-sw-6d7cf86d55-wtmnh   1/1     Running   0          32s
pod/my-nginx-sw-6d7cf86d55-zrbvm   1/1     Running   0          37s

NAME                  TYPE       CLUSTER-IP    EXTERNAL-IP   PORT(S)        AGE
service/my-nginx-sw   NodePort   10.96.99.40   <none>        80:31203/TCP   37s

NAME                          READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/my-nginx-sw   3/3     3            3           37s

NAME                                     DESIRED   CURRENT   READY   AGE
replicaset.apps/my-nginx-sw-6d7cf86d55   3         3         3       37s
```
5. Validate the logs from operator for patch operation
```bash
[2026-06-02 06:29:50,899] kopf.objects         [INFO    ] [test/my-nginx-sw] Deployment: my-nginx-sw needs reconciliation
[2026-06-02 06:29:50,909] kopf.objects         [INFO    ] [test/my-nginx-sw] Deployment: my-nginx-sw reconciled
[2026-06-02 06:29:50,910] kopf.objects         [INFO    ] [test/my-nginx-sw] Created the deployment: my-nginx-sw
[2026-06-02 06:29:50,914] kopf.objects         [INFO    ] [test/my-nginx-sw] Reconciling the service my-nginx-sw
[2026-06-02 06:29:50,914] kopf.objects         [INFO    ] [test/my-nginx-sw] Reconciled the service my-nginx-sw
[2026-06-02 06:29:50,918] kopf.objects         [INFO    ] [test/my-nginx-sw] Handler 'update_staticwebsite' succeeded.
[2026-06-02 06:29:50,918] kopf.objects         [INFO    ] [test/my-nginx-sw] Updating is processed: 1 succeeded; 0 failed.
[2026-06-02 06:29:50,938] kopf.objects         [WARNING ] [test/my-nginx-sw] Merge-patching finished with inconsistencies: (('remove', ('status', 'availableReplicas'), 2, None), ('remove', ('status', 'readyReplicas'), 2, None), ('remove', ('status', 'replicas'), 2, None))
```
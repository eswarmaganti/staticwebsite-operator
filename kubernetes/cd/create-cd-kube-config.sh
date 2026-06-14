#! /bin/bash

# get the cluster details from local kube config
CLUSTER_SERVER=$(kubectl config view --minify -o jsonpath="{.clusters[0].cluster.server}")
CLUSTER_CA=$(kubectl config view --minify --raw -o jsonpath="{.clusters[0].cluster.certificate-authority-data}")

# Get the ServiceAccount Token
SA_TOKEN=$(kubectl get secret github-actions-cd \
  -n staticwebsite-operator \
  -o jsonpath="{.data.token}" | base64 -d )

# Build the kubeconfig
cat <<EOF > ${HOME}/.kube/github-actions-cd-config.yaml
apiVersion: v1
kind: Config
clusters:
  - name: kind-cluster
    cluster:
      server: ${CLUSTER_SERVER}
      certificate-authority-data: ${CLUSTER_CA}
contexts:
  - name: github-actions-cd
    context:
      cluster: kind-cluster
      user: github-actions-cd
      namespace: staticwebsite-operator
current-context: github-actions-cd
users:
  - name: github-actions-cd
    user:
      token: ${SA_TOKEN}
EOF

## ERPNext Feature Board

Feature board for ERPNext

### Development Prerequisites

- [k3d](https://k3d.io/#installation)
- [kubectl](https://kubernetes.io/docs/tasks/tools)
- [helm](https://helm.sh/docs/intro/install/)
- [bench](https://github.com/frappe/bench)

### Install K3d Cluster

```shell
# export K3D_FIX_CGROUPV2=1 # use in case of cgroup2, Arch Linux or latest kernels
k3d cluster create devcluster \
  --registry-config ./cluster/k3d-registries.yaml \
  --api-port 127.0.0.1:6443 \
  -p 80:80@loadbalancer \
  -p 443:443@loadbalancer \
  --k3s-server-arg "--no-deploy=traefik"
```

### Install Docker Registry

```
docker volume create local_registry
docker container run -d --name registry.localhost -v local_registry:/var/lib/registry --restart always -p 5000:5000 registry:2
docker network connect k3d-devcluster registry.localhost
```

### Add Helm Repo

```shell
helm repo add fluxcd https://charts.fluxcd.io
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

### Install MariaDB

```shell
kubectl create ns mariadb
helm install mariadb -n mariadb bitnami/mariadb -f ./cluster/mariadb-values.yaml
```

### Install NFS

```shell
kubectl create ns nfs
kubectl create -f ./cluster/nfs-server-provisioner/statefulset.dev.yaml
kubectl create -f ./cluster/nfs-server-provisioner/rbac.yaml
kubectl create -f ./cluster/nfs-server-provisioner/class.yaml
```

### Install Redis

```shell
kubectl create ns redis
helm install redis -n redis bitnami/redis \
  --set auth.enabled=false \
  --set auth.sentinal=false \
  --set architecture=standalone \
  --set master.persistence.enabled=false
```

### Install Helm Operator (Flux Helm Operator)

```shell
kubectl apply -f https://raw.githubusercontent.com/fluxcd/helm-operator/1.2.0/deploy/crds.yaml
kubectl create ns flux
helm upgrade -i helm-operator fluxcd/helm-operator \
  --namespace flux \
  --set helm.versions=v3
```

### Create Namespace for application

```shell
kubectl create ns efb
```

Note: set `kubernetes_namespace` in `site_config.json` to use any other namespace.

### Install Ingress Controller (Optional)

Follow this step to try out created sites locally on port 80 and 443.

```shell
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v0.46.0/deploy/static/provider/cloud/deploy.yaml
```

### Bench start

Install this app on a site and `bench start`, we'll call this site `efb.localhost`

### Initialize Site

- Add `Github Repository`, add the url and github personal access token
- Sync `Github Repository`

### License

MIT

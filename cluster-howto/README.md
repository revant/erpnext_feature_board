### Install K3d Cluster

Prerequisite: `k3d`.

```shell
# export K3D_FIX_CGROUPV2=1 # use in case of cgroup2, Arch Linux or latest kernels
k3d cluster create devcluster \
  --api-port 127.0.0.1:6443 \
  -p 80:80@loadbalancer \
  -p 443:443@loadbalancer \
  --k3s-server-arg "--no-deploy=traefik"
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
helm install mariadb -n mariadb bitnami/mariadb -f mariadb-values.yaml
```

Note: Optionally change passwords and persistence from `mariadb-values.yaml`

### Install NFS

```shell
kubectl create ns nfs
kubectl create -f nfs-server-provisioner/statefulset.dev.yaml
kubectl create -f nfs-server-provisioner/rbac.yaml
kubectl create -f nfs-server-provisioner/class.yaml
```

Note: Change `storageClassName` from `nfs-server-provisioner/statefulset.yaml`

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

### Install Docker Registry

```
kubectl create ns registry
kubectl docker-registry.dev.yaml
```

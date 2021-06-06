### Create a cluster and obtain kubeconfig file

Provider used for testing: Digitalocean

### Create Namespace for ERPNext Feature Board

```shell
kubectl create ns efb
```

### Install Kubernetes ingress-nginx

Refer https://kubernetes.github.io/ingress-nginx/

```shell
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v0.46.0/deploy/static/provider/cloud/deploy.yaml
```

### Install cert-manager

Refer https://cert-manager.io/docs/installation/kubernetes/#option-2-install-crds-as-part-of-the-helm-release

```shell
helm install \
	cert-manager jetstack/cert-manager \
	--namespace cert-manager \
	--version v1.3.1 \
	--set installCRDs=true
```

Edit cluster-issuer.yaml as per your configuration and create cluster-issuer

```shell
kubectl apply -f cluster-issuer.yaml
```

Edit certificate.yaml as per your wildcard domain and create certificate

```shell
kubectl apply -f certificate.yaml
```

### Install MariaDB, Redis, NFS

Install all of these services, same as in development environment, just change the `storageClass` as per your cloud provider. Storage will be required for NFS and MariaDB. No need for persistence for Redis.

### Create Docker Registry

Change the `docker-registry.yaml` as per your configuration and install. Remember to change the secrets and auth data.

```shell
kubectl apply -f docker-registry.yaml
```

### Install ERPNext Feature Board

Change the `efb/values.yaml`, change the registry from `registry.example.com` to your private registry setup in previous step. Also change values for `createSite` and `ingress` as per your configuration.

Install the helm chart with `values.yaml`

```shell
helm install efb -n efb frappe/erpnext -f efb/efb-values.yaml
```

Add additional RBAC for efb to operate cluster.

```shell
kubectl apply -f rbac.yaml
```

### Site Config Keys

Enter the erpnext-python pod and add the following to `site_config.json`

- `container_registry`: Set it to the private registry
- `db_root_password`: Set it to MariaDB superuser password
- `domain_name`: Set it to the base domain name of the review platform.
- `wildcard_tls_secret`: Set it to the secret name where wildcard certificate is stored by cert-manager

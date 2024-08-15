# Microk8s on Ubuntu Server

## Install Microk8s

```bash
sudo snap install microk8s --classic
```

## Enable DNS

```bash
microk8s enable dns
```

## Enable Helm

```bash
microk8s enable helm
```

## Enable Ingress

```bash
microk8s enable ingress
```

## Registry

### Enable Registry

```bash
microk8s enable registry
```
Read more about [Registry](https://microk8s.io/docs/registry-built-in)

Update /etc/docker/daemon.json

```json
{
  "insecure-registries" : ["localhost:32000"]
}
```

Restart Docker

```bash
sudo systemctl restart docker
```


### Push Image

```bash
docker tag my-image localhost:32000/my-image
docker push localhost:32000/my-image
```
# Main Umbrella Chart
This is the main umbrella chart for the project. It contains all the subcharts and dependencies.

## Prerequisites

- Kubernetes 1.12+
- Helm 3.0+

### Namespace

This chart requires a namespace to be available. You can create one using the following command:

```bash
kubectl create namespace main
```

### Persistent Volume

This chart requires a Persistent Volume to be available. You can create one using the following command:

```bash
cd persVolume
kubectl apply -f vol-mongo.yaml -n main
```

## Subcharts

- MongoDB
- Mongo Express

### Install

```bash
cd k8/helm-charts
helm dependency update .
helm upgrade --install main . -n main
```

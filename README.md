# docker-images

The OCI container images used in MENTORED Testbed.

Build instructions

## First get the kubeconfig with a cluster that has both AArch64 and AMD64 nodes
```bash
export KUBECONFIG=<....>
```
## Create a builder for AMD64 stuff
```bash
docker buildx create \
  --bootstrap \
  --name=mentored-ufmg-kube \
  --driver=kubernetes \
  --platform=linux/amd64 \
  --node=builder-amd64 \
  --driver-opt=namespace=mentored,nodeselector="kubernetes.io/arch=amd64"
```

## Create a builder for AArch64, appending to the previous context
```bash
docker buildx create \
  --bootstrap --append \
  --name=mentored-ufmg-kube \
  --driver=kubernetes \
  --platform=linux/arm64 \
  --node=builder-aarch64 \
  --driver-opt=namespace=mentored,nodeselector="kubernetes.io/arch=arm64" 
```

## Use build context
```bash
docker buildx use mentored-ufmg-kube
```

## Dispatch the build

```bash
./publish-container.sh ghcr.io/mentoredtestbed/ latest --all
```

(Otherwise it will build only files in `to-build.csv`)
# docker-images

The OCI container images used in MENTORED Testbed.

Build instructions bellow:

## Option 1) Use the K8S cluster resources
<details>

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

</details>

## Option 2) Local builds

<details>

```bash
docker buildx create \
  --name mentored-local-builder \
  --driver docker-container \
  --platform linux/amd64,linux/arm64
```

### Activate it

```bash
docker buildx use mentored-local-builder
```

### List buildx contexts (should show the current one with a * at the end)

```bash
docker buildx ls # Should list both as inactive or running
```

### Bootstrap the buildkit in that builder:

```bash
docker buildx inspect --bootstrap
```

### Check if it's marked as running

```bash
docker buildx ls
```

</details>

## Dispatch the build

```bash
./publish-container.sh ghcr.io/mentoredtestbed/ latest --all --enable-aarch64
```

(Otherwise it will build only files in `to-build.csv`)

### Speeding up builds during development

You can ommit the `--enable-aarch64` argumment to skip building AArch64 images.
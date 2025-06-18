# docker-images

This is the collection of container images used in the MENTORED Testbed. Bellow are instructions on how to build them.


# Setting up builders:

## Use local machine for AMD64 builds:

```bash
docker buildx create \
  --name mentored-multiarch \
  --driver docker-container \
  --platform linux/amd64 # If no native-AArch64 nodes exist, you can add linux/arm64 here too, the builds will just be slower
```

## Append remote AArch64 builder:

```bash
docker buildx create \
  --append \      
  --name mentored-multiarch \
  --node mentored-arm64 \
  --platform linux/arm64 \
  ssh://USERNAME@some-aarch64-node
```

## Activate them:

```bash
docker buildx use mentored-multiarch
```

## List nodes:

```bash
docker buildx ls # Should list both as inactive or running
```

## Bootstrap builders:

```bash
docker buildx inspect --bootstrap
```

## List nodes:

```bash
docker buildx ls # Should list them as running
```

## Building and pushing multiple images

```bash
sudo ./publish-container.sh ghcr.io/mentoredtestbed/ latest --all
```

(Otherwise it will build only files in `to-build.csv`)
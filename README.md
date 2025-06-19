# docker-images

This is the collection of container images used in the MENTORED Testbed. Bellow are instructions on how to build them.


# Setting up builders:

## Use local machine for AMD64 builds:

### Use SSH for local machine (recommeneded):

#### Add your SSH key to root@localhost:

```bash
ssh-copy-id -p 22 root@localhost
```

If no native-AArch64 nodes exist, you can add linux/arm64 here too, the builds will just be slower:

```bash
docker buildx create \
  --name mentored-multiarch \
  --driver docker-container \
  --node mymachine \
  --platform linux/amd64 \
  ssh://root@localhost:22
```

### Use default socker socket (needs priviledges!):

<details>

If no native-AArch64 nodes exist, you can add linux/arm64 here too, the builds will just be slower:

```bash
docker buildx create \
  --name mentored-multiarch \
  --driver docker-container \
  --node mymachine \
  --platform linux/amd64
```
</details>

## Append remote AArch64 builder:

```bash
docker buildx create \
  --name mentored-multiarch \
  --append \
  --driver docker-container \
  --node some-aarch64-machine \
  --platform linux/arm64 \
  ssh://root@some-aarch64-machine:22
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
./publish-container.sh ghcr.io/mentoredtestbed/ latest --all
```

(Otherwise it will build only files in `to-build.csv`)
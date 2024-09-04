# set -x
REPO=$1 # eg ghcr.io/mentoredtestbed/
TAG=$2  # eg 0.0.1
dependencies=("mentored-base" "infection-scenario")
# sudo docker-buildx build -t '$TAG''$D':latest --platform linux/amd64,linux/arm64 --push '$D'
# Build and push all directories in the dependencies array
# Build dependencies first
for D in "${dependencies[@]}"; do
    bash -c "sudo docker-buildx build -t $REPO$D:$TAG --platform linux/amd64,linux/arm64 --push '$D'";
    # Exit if previous command failed
    if [ $? -ne 0 ]; then
        exit 1
    fi
done
# Build and push all directories in the current directory
for D in *; do
    # skip if dir is a dependency
    if [[ " ${dependencies[@]} " =~ " ${D} " ]]; then
        continue
    fi
    FULL_CONTAINER_IMAGE_URL="$REPO$D:$TAG"
    echo "Building $FULL_CONTAINER_IMAGE_URL"
    bash -c "sudo docker-buildx build --quiet -t $REPO$D:$TAG --platform linux/amd64,linux/arm64 --push $D"; # or use '$D'" &; here to do it in parallel
    # Exit if previous command failed
    if [ $? -ne 0 ]; then
        exit 1
    fi
    echo "Built $FULL_CONTAINER_IMAGE_URL"
done

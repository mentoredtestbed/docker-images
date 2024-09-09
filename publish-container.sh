# set -x
# Usage: sudo bash publish-container.sh ghcr.io/khalilsantana/ foo
REPO=$1 # eg ghcr.io/khalilsantana/
TAG=$2  # eg 0.0.1
dependencies=("mentored-base")

# Read from to-build.csv file to array
IFS=, read -r -a tobuild < to-build.csv
echo "Building ${tobuild[@]}..."

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
# Find dirs based on find -type d, without ./ and only 1 level deep
# https://stackoverflow.com/questions/9612090/how-to-loop-through-file-directory-in-bash
# https://stackoverflow.com/questions/1842254/how-can-i-find-all-of-the-files-in-a-directory-using-find
# for dir in */; do
#     D=$(basename "$dir")
#     # skip if dir is a dependency
#     if [[ " ${dependencies[@]} " =~ " ${D} " ]]; then
#         continue
#     fi
#     FULL_CONTAINER_IMAGE_URL="$REPO$D:$TAG"
#     echo "Building $FULL_CONTAINER_IMAGE_URL"
#     bash -c "sudo docker-buildx build --quiet -t $REPO$D:$TAG --platform linux/amd64,linux/arm64 --push $D" ; # or use '$D'" &; here to do it in parallel
#     # Exit if previous command failed
#     if [ $? -ne 0 ]; then
#         exit 1
#     fi
#     echo "Built $FULL_CONTAINER_IMAGE_URL"
# done

build_all() {
for dir in */; do
    D=$(basename "$dir")
    # skip if dir is a dependency
    if [[ " ${dependencies[@]} " =~ " ${D} " ]]; then
        continue
    fi
    FULL_CONTAINER_IMAGE_URL="$REPO$D:$TAG"
    echo "Building $FULL_CONTAINER_IMAGE_URL"
    bash -c "sudo docker-buildx build --quiet -t $REPO$D:$TAG --platform linux/amd64,linux/arm64 --push $D" ; # or use '$D'" &; here to do it in parallel
    # Exit if previous command failed
    if [ $? -ne 0 ]; then
        exit 1
    fi
    echo "Built $FULL_CONTAINER_IMAGE_URL"
done
}
# Why does this not work?
build_only() {
for dir in ${tobuild[@]}; do
    # skip if dir is a dependency
    if [[ " ${dependencies[@]} " =~ " ${dir} " ]]; then
        continue
    fi
    FULL_CONTAINER_IMAGE_URL="$REPO$dir:$TAG"
    echo "Building $FULL_CONTAINER_IMAGE_URL"
    bash -c "sudo docker-buildx build --quiet -t $REPO$dir:$TAG --platform linux/amd64,linux/arm64 --push $dir" ; # or use '$dir'" &; here to do it in parallel
    # Exit if previous command failed
    if [ $? -ne 0 ]; then
        exit 1
    fi
    echo "Built $FULL_CONTAINER_IMAGE_URL"
done
}

# if --all build all containers, else build only the ones in the to-build.csv file
if [ "$3" == "--all" ]; then
    build_all
else
    build_only
fi
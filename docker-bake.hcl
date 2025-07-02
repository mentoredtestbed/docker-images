variable "REGISTRY" {
  default = "ghcr.io/khalilsantana"
}

variable "TAG" {
  default = "latest"
}

variable "PLATFORMS" {
  default = ["linux/amd64", "linux/arm64"]
}

group "default" {
  targets = [
    "mentored-base",
    "generic-botnet",
    "generic-client",
    "infection-scenario"
  ]
}

target "mentored-base" {
  context = "./mentored-base"
  dockerfile = "./Dockerfile"
  tags = [
    "${REGISTRY}/mentored-base:${TAG}",
  ]
  platforms = PLATFORMS
}

target "generic-botnet" {
  context = "./generic-botnet"
  dockerfile = "./Dockerfile"
  contexts = {
    mentored-base = "target:mentored-base"
  }
  tags = [
    "${REGISTRY}/generic-botnet:${TAG}",
  ]
  platforms = PLATFORMS
  depends_on = ["mentored-base"]
}

target "generic-client" {
  context = "./generic-client"
  dockerfile = "./Dockerfile"
  contexts = {
    mentored-base = "target:mentored-base"
  }
  tags = [
    "${REGISTRY}/generic-client:${TAG}",
  ]
  platforms = PLATFORMS
  depends_on = ["mentored-base"]
}

target "infection-scenario" {
  context = "./infection-scenario"
  dockerfile = "./Dockerfile"
  contexts = {
    generic-botnet = "target:generic-botnet"
  }
  tags = [
    "${REGISTRY}/infection-scenario:${TAG}",
  ]
  platforms = PLATFORMS
  depends_on = ["generic-botnet"]
}
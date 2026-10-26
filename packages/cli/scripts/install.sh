#!/usr/bin/env bash
set -euo pipefail

REPO="hieudoanm/grobid-cli"
BINARY_NAME="grobid"
INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/bin}"

URL="https://github.com/${REPO}/releases/download/latest/${BINARY_NAME}"

echo "Downloading grobid binary from ${URL} ..."
curl -fsSL "${URL}" -o "${INSTALL_DIR}/${BINARY_NAME}"
chmod +x "${INSTALL_DIR}/${BINARY_NAME}"

echo "Installed to ${INSTALL_DIR}/${BINARY_NAME}"
echo "Make sure ${INSTALL_DIR} is in your PATH, e.g.:"
echo "  export PATH=\"\$PATH:${INSTALL_DIR}\""

# Check Docker
if command -v docker >/dev/null 2>&1; then
  echo "Docker is installed."
else
  echo "WARNING: Docker is not installed. grobid-cli requires Docker to run GROBID."
  read -r -p "Would you like to install Docker now? [y/N] " response
  case "$response" in
    [yY]|[yY][eE][sS])
      OS="$(uname -s)"
      case "$OS" in
        Linux)
          if command -v pacman >/dev/null 2>&1; then
            sudo pacman -S --noconfirm docker docker-compose
          elif command -v apt-get >/dev/null 2>&1; then
            sudo apt-get update && sudo apt-get install -y docker.io docker-compose
          elif command -v yum >/dev/null 2>&1; then
            sudo yum install -y docker docker-compose
          elif command -v dnf >/dev/null 2>&1; then
            sudo dnf install -y docker docker-compose
          else
            echo "Unsupported Linux package manager. Install Docker manually: https://docs.docker.com/engine/install/"
            exit 1
          fi
          ;;
        Darwin)
          if command -v brew >/dev/null 2>&1; then
            brew install --cask docker
          else
            echo "Homebrew not found. Install Docker Desktop manually: https://docs.docker.com/docker-mac/install/"
            exit 1
          fi
          ;;
        *)
          echo "Unsupported OS: ${OS}. Install Docker manually: https://docs.docker.com/engine/install/"
          exit 1
          ;;
      esac
      ;;
    *)
      echo "You can install Docker later from https://docs.docker.com/engine/install/"
      ;;
  esac
fi
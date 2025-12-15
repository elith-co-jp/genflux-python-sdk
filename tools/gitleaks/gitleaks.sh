#!/usr/bin/env bash

# Configuration
TOOL_NAME="gitleaks"
VERSION="8.22.1"
BASE_DIR="./tools/${TOOL_NAME}"
BIN_PATH="${BASE_DIR}/bin/${TOOL_NAME}"
CONFIG_FILE="${BASE_DIR}/${TOOL_NAME}.toml"

# Check if installation needed
need_install() {
  if [ ! -x "${BIN_PATH}" ]; then
    return 0
  fi
  
  if [[ "$(${BIN_PATH} version)" != "${VERSION}" ]]; then
    return 0
  fi
  
  return 1
}

# Determine system type
determine_system() {
  local os=""
  local arch=""
  
  # Determine operating system
  if [[ "$OSTYPE" == "linux"* ]]; then
    os="linux"
  elif [[ "$OSTYPE" == "darwin"* ]]; then
    os="darwin"
  else
    echo "Error: Unsupported operating system: ${OSTYPE}"
    exit 1
  fi
  
  # Determine architecture
  case "$(uname -m)" in
    "x86_64")
      arch="x64"
      ;;
    "arm64"|"aarch64")
      arch="arm64"
      ;;
    *)
      echo "Error: Unsupported architecture: $(uname -m)"
      exit 1
      ;;
  esac
  
  echo "${os}_${arch}"
}

# Install gitleaks binary
install_tool() {
  local system_info=$(determine_system)
  local os_type=${system_info%_*}
  local arch_type=${system_info#*_}
  
  local package_name="${TOOL_NAME}_${VERSION}_${os_type}_${arch_type}.tar.gz"
  local download_url="https://github.com/${TOOL_NAME}/${TOOL_NAME}/releases/download/v${VERSION}/${package_name}"
  local temp_file="${BASE_DIR}/bin/${package_name}"
  
  # Create bin directory if not exists
  mkdir -p "${BASE_DIR}/bin"
  
  # Download and extract
  echo "Downloading ${TOOL_NAME} version ${VERSION}..."
  curl -L "${download_url}" -o "${temp_file}"
  tar -xzf "${temp_file}" -C "${BASE_DIR}/bin"
  
  # Clean up
  rm -f "${BASE_DIR}/bin/${TOOL_NAME}_"*
  
  echo "${TOOL_NAME} installed successfully"
}

# Main execution
if need_install; then
  install_tool
fi

# Run gitleaks with arguments
"${BIN_PATH}" git -v -c "${CONFIG_FILE}" "$@"
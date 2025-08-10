#!/usr/bin/env bash
set -euo pipefail

# Ask for username
read -rp "Docker Hub username: " USERNAME

# Today's date
DATE_TAG=$(date +%Y%m%d)

# Dockerfiles and image base names
IMAGES=(
  "agent|agent.dockerfile"
  "tools|tools.dockerfile"
)

for ITEM in "${IMAGES[@]}"; do
  IFS='|' read -r NAME DOCKERFILE <<< "$ITEM"

  IMAGE_NAME="$USERNAME/mcp_search_agent-$NAME"

  echo "=== Building $IMAGE_NAME ==="
  docker build -f "$DOCKERFILE" \
    -t "$IMAGE_NAME:latest" \
    -t "$IMAGE_NAME:${DATE_TAG}-$NAME" .

  echo "=== Pushing $IMAGE_NAME ==="
  docker push "$IMAGE_NAME:latest"
  docker push "$IMAGE_NAME:${DATE_TAG}-$NAME"
done

echo "✅ All done"


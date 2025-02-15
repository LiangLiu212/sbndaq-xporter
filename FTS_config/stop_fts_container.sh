#----------------------------------------
# Stop FTS from a podman container image
#----------------------------------------
#
# Disclaimer:
# FTS is old, and can not be run on EL9 without significant complications.
# A prebuilt FTS container image is provided to work with Podman.
#

host=$(hostname | awk -F'.' '{print $1}')

# stop the container
echo "Stopping FTS podman container on ${host}"
podman stop fts_${host}

# remove the container, so you can run it again
echo "Removing FTS podman container on ${host}"
podman rm fts_${host}

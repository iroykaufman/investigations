#!/bin/bash

set -euo pipefail
# set -x
source common.sh

if [[ "${#}" -ne 1 ]]; then
	echo "Usage: $0 <path-to-ssh-public-key>"
	exit 1
fi

KEY=$1
TRUSTEE_PORT=8080

# Setup reference values, policies and secrets
until IP="$(./scripts/get-ip.sh trustee)" && [ -n "$IP" ] && curl "http://${IP}:${TRUSTEE_PORT}" >/dev/null 2>&1; do
	echo "Waiting for KBS to be available..."
	sleep 1
done
until ssh core@$IP \
	-i "${KEY%.*}" \
	-o StrictHostKeyChecking=no \
	-o UserKnownHostsFile=/dev/null \
	'sudo /usr/local/bin/populate_kbs.sh'; do
	echo "Waiting for KBS to be populated..."
	sleep 1
done

# Setup remote ignition config
IGNITION=$(create_remote_ign_config)

scp -i "${KEY%.*}" \
	-o StrictHostKeyChecking=no \
	-o UserKnownHostsFile=/dev/null \
	tmp/${IGNITION} core@$IP:

ssh core@$IP \
	-i "${KEY%.*}" \
	-o StrictHostKeyChecking=no \
	-o UserKnownHostsFile=/dev/null \
	"sudo mv $IGNITION /srv/www && sudo systemctl restart nginx.service"

#!/bin/bash

MERCURY_LOG_ARGS=""

if [ -n "${MERCURY_LOG_LEVEL}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --log-level ${MERCURY_LOG_LEVEL}"
fi

if [ -n "${MERCURY_API_INVENTORY_ROUTER}" ]; then
    MRCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --inventory-router ${MERCURY_API_INVENTORY_ROUTER}"
fi

if [ -n "${MERCURY_API_RPC_ROUTER}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-router ${MERCURY_API_RPC_ROUTER}"
fi

# All variables defined via Docker-Compose Environment
# for some reason this doesn't seem to work
# mercury-api ${MERCURY_LOG_ARGS}
# while this does:
python -c "import mercury_api.server; mercury_api.server.main()"

echo "Waiting for docker termination"
while true
do
	sleep 120
done

set -eu

npm install --prefix /data --omit=dev --no-audit --no-fund
exec /usr/src/node-red/entrypoint.sh "$@"

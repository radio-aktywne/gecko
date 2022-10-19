#!/bin/bash --login

set +euo pipefail
conda activate emirecorder
set -euo pipefail

exec "$@"

#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "Please run this script as root or using sudo!"
    exit 13
fi

if [ -f /shared/github-runner.env ]; then
    set -a
    # shellcheck disable=SC1091
    . /shared/github-runner.env
    set +a
fi

if [ ! -f /shared/github-runner.env ] && [ -z "${GH_RUNNER_URL:-}" ] && [ -z "${GH_RUNNER_TOKEN:-}" ]; then
    cat <<'EOF' >&2
Runner configuration is missing inside the guest.
If you created vagrant/shared/github-runner.env on the host after the VM was already running,
sync it first with:
  vagrant rsync github-runner
Or bypass the shared file and pass GH_RUNNER_URL / GH_RUNNER_TOKEN in the host environment.
EOF
fi

: "${GH_RUNNER_URL:?Set GH_RUNNER_URL in /shared/github-runner.env or the host environment.}"
: "${GH_RUNNER_TOKEN:?Set GH_RUNNER_TOKEN in /shared/github-runner.env or the host environment.}"

if [ ! -x /opt/actions-runner/config.sh ]; then
    echo "GitHub runner is not installed. Run the base provisioner first." >&2
    exit 1
fi

runner_name="${GH_RUNNER_NAME:-$(hostname -s)}"
runner_labels="${GH_RUNNER_LABELS:-self-hosted,linux,vagrant}"
runner_group="${GH_RUNNER_GROUP:-Default}"
runner_workdir="${GH_RUNNER_WORKDIR:-_work}"
runner_disable_update="${GH_RUNNER_DISABLE_UPDATE:-false}"

export RUNNER_URL="$GH_RUNNER_URL"
export RUNNER_TOKEN="$GH_RUNNER_TOKEN"
export RUNNER_NAME="$runner_name"
export RUNNER_LABELS="$runner_labels"
export RUNNER_GROUP="$runner_group"
export RUNNER_WORKDIR="$runner_workdir"
export RUNNER_DISABLE_UPDATE="$runner_disable_update"

if [ ! -f /opt/actions-runner/.runner ]; then
    sudo -u github-runner --preserve-env=RUNNER_URL,RUNNER_TOKEN,RUNNER_NAME,RUNNER_LABELS,RUNNER_GROUP,RUNNER_WORKDIR,RUNNER_DISABLE_UPDATE bash <<'EOF'
set -euo pipefail
cd /opt/actions-runner

config_args=(
    ./config.sh
    --unattended
    --url "$RUNNER_URL"
    --token "$RUNNER_TOKEN"
    --name "$RUNNER_NAME"
    --labels "$RUNNER_LABELS"
    --work "$RUNNER_WORKDIR"
    --replace
)

if [ "$RUNNER_GROUP" != "Default" ]; then
    config_args+=(--runnergroup "$RUNNER_GROUP")
fi

if [ "$RUNNER_DISABLE_UPDATE" = "true" ]; then
    config_args+=(--disableupdate)
fi

"${config_args[@]}"
EOF
fi

install -d /etc/needrestart/conf.d
cat <<'EOF' > /etc/needrestart/conf.d/actions_runner_services.conf
$nrconf{override_rc}{qr(^actions\.runner\..+\.service$)} = 0;
EOF

if ! compgen -G "/etc/systemd/system/actions.runner.*.service" >/dev/null; then
    (
        cd /opt/actions-runner
        ./svc.sh install github-runner
    )
fi

systemctl daemon-reload

service_units=(/etc/systemd/system/actions.runner.*.service)
if [ "${service_units[0]}" = "/etc/systemd/system/actions.runner.*.service" ]; then
    echo "Runner service unit was not created." >&2
    exit 1
fi

for service_unit in "${service_units[@]}"; do
    systemctl enable --now "$(basename "$service_unit")"
done

echo "GitHub runner configured and started successfully."

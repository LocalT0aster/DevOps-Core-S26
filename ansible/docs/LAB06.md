# LAB06 - Advanced Ansible & CI/CD

## Task 1: Blocks & Tags (2 pts)

### Overview

For Task 1 I refactored the existing Ansible roles to use blocks, rescue handling, and tags without changing the repository's custom file naming convention. The lab sheet mentions `main.yml`, but this repository already uses descriptive files such as `common_tasks.yml` and `docker_tasks.yml`, so I kept that structure.

### Implementation Details

#### `common` role

Changes made:

- Grouped APT cache refresh and package installation into a `block` tagged `packages`.
- Added a `rescue` path that runs `apt-get update --fix-missing`, then retries the cache refresh and package installation.
- Added an `always` section that records block completion in `/tmp/ansible-common-role.log`.
- Added a separate `users` block that ensures managed users exist and also records completion.
- Kept timezone management outside the package block so `--tags packages` only runs package-related work.

Practical result:

- `--tags packages` runs only the package block.
- `--skip-tags common` skips the whole role because the playbook applies the `common` tag at role level.

#### `docker` role

Changes made:

- Grouped Docker installation tasks into a `block` tagged `docker_install`.
- Added a `rescue` path that waits 10 seconds, refreshes APT metadata, and retries the Docker repository/key/package setup.
- Added an `always` section that ensures the Docker service is enabled and running after a successful install path.
- Grouped Docker configuration into a separate `block` tagged `docker_config`.
- Added completion logging to `/tmp/ansible-docker-role.log`.

Practical result:

- `--tags docker` runs the whole Docker role.
- `--tags docker_install` runs only installation-related work.
- Rescue behavior is visible in the collected logs.

#### Playbook tag strategy

Role-level tags are applied in the playbooks so the role can be selected as a whole, while block tags allow narrower execution.

| Tag              | Purpose                                  |
| ---------------- | ---------------------------------------- |
| `common`         | Entire common role                       |
| `packages`       | Package install/update block in `common` |
| `users`          | User-management block in `common`        |
| `docker`         | Entire docker role                       |
| `docker_install` | Docker installation and repository setup |
| `docker_config`  | Docker host configuration                |

### Evidence

The main evidence file is `task1.log`.

#### 1. Selective execution with `--tags "docker"`

This run exercised only the Docker role and also proved that the `rescue` section works:

<details>
<summary><code>ansible-playbook playbooks/provision.yml --tags "docker"</code></summary>

```
$ ansible-playbook playbooks/provision.yml --tags "docker"

PLAY [Provision web servers] ****************************************************************************************************

TASK [Gathering Facts] **********************************************************************************************************
ok: [vagrant]

TASK [Run docker role tasks/defaults/handlers] **********************************************************************************
included: docker for vagrant

TASK [docker : Install Docker prerequisites] ************************************************************************************
[WARNING]: Failed to update cache after 1 retries due to , retrying
[WARNING]: Sleeping for 2 seconds, before attempting to refresh the cache again
[WARNING]: Failed to update cache after 2 retries due to , retrying
[WARNING]: Sleeping for 3 seconds, before attempting to refresh the cache again
[WARNING]: Failed to update cache after 3 retries due to , retrying
[WARNING]: Sleeping for 5 seconds, before attempting to refresh the cache again
[WARNING]: Failed to update cache after 4 retries due to , retrying
[WARNING]: Sleeping for 9 seconds, before attempting to refresh the cache again
[WARNING]: Failed to update cache after 5 retries due to , retrying
[WARNING]: Sleeping for 13 seconds, before attempting to refresh the cache again
[ERROR]: Task failed: Module failed: Failed to update apt cache after 5 retries:
Origin: /home/t0ast/Repos/DevOps-Core-S26/ansible/roles/docker/tasks/docker_tasks.yml:7:7

5     - docker_install
6   block:
7     - name: Install Docker prerequisites
        ^ column 7

fatal: [vagrant]: FAILED! => {"changed": false, "msg": "Failed to update apt cache after 5 retries: "}

TASK [docker : Mark Docker install rescue as triggered] *************************************************************************
ok: [vagrant]

TASK [docker : Wait before retrying Docker apt setup] ***************************************************************************
Pausing for 10 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [vagrant]

TASK [docker : Refresh apt cache before Docker retry] ***************************************************************************
changed: [vagrant]

TASK [docker : Retry adding Docker GPG key] *************************************************************************************
ok: [vagrant]

TASK [docker : Retry adding Docker apt repository] ******************************************************************************
ok: [vagrant]

TASK [docker : Retry installing Docker engine packages] *************************************************************************
ok: [vagrant]

TASK [docker : Retry installing Docker Python SDK package] **********************************************************************
ok: [vagrant]

TASK [docker : Mark Docker service as ready after retry] ************************************************************************
ok: [vagrant]

TASK [docker : Ensure Docker service is enabled and running] ********************************************************************
ok: [vagrant]

TASK [docker : Record Docker installation block completion] *********************************************************************
changed: [vagrant]

TASK [docker : Add deployment user to docker group] *****************************************************************************
ok: [vagrant]

TASK [docker : Record Docker configuration block completion] ********************************************************************
ok: [vagrant]

PLAY RECAP **********************************************************************************************************************
vagrant                    : ok=14   changed=2    unreachable=0    failed=0    skipped=0    rescued=1    ignored=0

```

</details>

This is the strongest proof for Task 1 because it shows:

- only the Docker role was selected,
- the block failed,
- the `rescue` path recovered successfully,
- the play still finished with `failed=0` and `rescued=1`.

#### 2. Skipping the `common` role

<details>
<summary><code>ansible-playbook playbooks/provision.yml --skip-tags "common"</code></summary>

```
$ ansible-playbook playbooks/provision.yml --skip-tags "common"
PLAY [Provision web servers] ***************************************************

TASK [Gathering Facts] *********************************************************
ok: [vagrant]

TASK [Run docker role tasks/defaults/handlers] *********************************
included: docker for vagrant

TASK [docker : Install Docker prerequisites] ***********************************
ok: [vagrant]

TASK [docker : Ensure Docker keyring directory exists] *************************
ok: [vagrant]

TASK [docker : Add Docker GPG key] *********************************************
ok: [vagrant]

TASK [docker : Add Docker apt repository] **************************************
ok: [vagrant]

TASK [docker : Install Docker engine packages] *********************************
ok: [vagrant]

TASK [docker : Install Docker Python SDK package] ******************************
ok: [vagrant]

TASK [docker : Mark Docker service as ready] ***********************************
ok: [vagrant]

TASK [docker : Ensure Docker service is enabled and running] *******************
ok: [vagrant]

TASK [docker : Record Docker installation block completion] ********************
ok: [vagrant]

TASK [docker : Add deployment user to docker group] ****************************
ok: [vagrant]

TASK [docker : Record Docker configuration block completion] *******************
ok: [vagrant]

PLAY RECAP *********************************************************************
vagrant                    : ok=13   changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

```

</details>

No `common` tasks ran, which confirms the role-level `common` tag is working.

#### 3. Running package tasks only

<details>
<summary><code>ansible-playbook playbooks/provision.yml --tags "packages"</code></summary>

```
$ ansible-playbook playbooks/provision.yml --tags "packages"
PLAY [Provision web servers] ***************************************************

TASK [Gathering Facts] *********************************************************
ok: [vagrant]

TASK [Run common role tasks/defaults] ******************************************
included: common for vagrant

TASK [common : Update apt cache] ***********************************************
ok: [vagrant]

TASK [common : Install common packages] ****************************************
ok: [vagrant]

TASK [common : Record common packages block completion] ************************
ok: [vagrant]

PLAY RECAP *********************************************************************
vagrant                    : ok=5    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

```

</details>

This shows the `packages` tag is narrow enough to avoid unrelated common-role tasks.

#### 4. Check mode for Docker tasks

<details>
<summary><code>ansible-playbook playbooks/provision.yml --tags "docker" --check</code></summary>

```
$ ansible-playbook playbooks/provision.yml --tags "docker" --check
PLAY [Provision web servers] ***************************************************

TASK [Gathering Facts] *********************************************************
ok: [vagrant]

TASK [Run docker role tasks/defaults/handlers] *********************************
included: docker for vagrant

TASK [docker : Install Docker prerequisites] ***********************************
ok: [vagrant]

TASK [docker : Ensure Docker keyring directory exists] *************************
ok: [vagrant]

TASK [docker : Add Docker GPG key] *********************************************
changed: [vagrant]

TASK [docker : Add Docker apt repository] **************************************
ok: [vagrant]

TASK [docker : Install Docker engine packages] *********************************
ok: [vagrant]

TASK [docker : Install Docker Python SDK package] ******************************
ok: [vagrant]

TASK [docker : Mark Docker service as ready] ***********************************
ok: [vagrant]

TASK [docker : Ensure Docker service is enabled and running] *******************
ok: [vagrant]

TASK [docker : Record Docker installation block completion] ********************
ok: [vagrant]

TASK [docker : Add deployment user to docker group] ****************************
ok: [vagrant]

TASK [docker : Record Docker configuration block completion] *******************
ok: [vagrant]

PLAY RECAP *********************************************************************
vagrant                    : ok=13   changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

```

</details>

Check mode completed without errors. One task reported `changed`, which is not surprising for repository/key download style tasks; check mode is useful, but not perfect, for external-resource operations.

#### 5. Running only Docker installation tasks

<details>
<summary><code>ansible-playbook playbooks/provision.yml --tags "docker_install"</code></summary>

```
$ ansible-playbook playbooks/provision.yml --tags "docker_install"
PLAY [Provision web servers] ***************************************************

TASK [Gathering Facts] *********************************************************
ok: [vagrant]

TASK [Run docker role tasks/defaults/handlers] *********************************
included: docker for vagrant

TASK [docker : Install Docker prerequisites] ***********************************
ok: [vagrant]

TASK [docker : Ensure Docker keyring directory exists] *************************
ok: [vagrant]

TASK [docker : Add Docker GPG key] *********************************************
ok: [vagrant]

TASK [docker : Add Docker apt repository] **************************************
ok: [vagrant]

TASK [docker : Install Docker engine packages] *********************************
ok: [vagrant]

TASK [docker : Install Docker Python SDK package] ******************************
ok: [vagrant]

TASK [docker : Mark Docker service as ready] ***********************************
ok: [vagrant]

TASK [docker : Ensure Docker service is enabled and running] *******************
ok: [vagrant]

TASK [docker : Record Docker installation block completion] ********************
ok: [vagrant]

PLAY RECAP *********************************************************************
vagrant                    : ok=11   changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

```

</details>

This confirms that installation tasks can be isolated from broader Docker role execution.

#### 6. Available tags

Verified with:

<details>
<summary><code>ansible-playbook playbooks/provision.yml --list-tags</code></summary>

```
$ ansible-playbook playbooks/provision.yml --list-tags


playbook: playbooks/provision.yml

  play #1 (webservers): Provision web servers	TAGS: []
      TASK TAGS: [common, docker, docker_config, docker_install, packages, users]

```

</details>

### Analysis

Blocks improved the structure of both roles because related tasks are now grouped around a single intent instead of being scattered as flat tasks. In practice, this made the Docker install flow easier to reason about: install steps are in one place, recovery steps are in one place, and service enforcement is in one place.

The rescue behavior in the Docker role is especially useful. The first `--tags "docker"` run showed a real transient APT/cache failure, and the play recovered automatically. That is more convincing than a purely theoretical discussion because the log captured an actual `rescued=1` run.

The tag layout is also practical rather than decorative:

- broad tags (`common`, `docker`) support role-level execution,
- narrow tags (`packages`, `users`, `docker_install`, `docker_config`) support targeted runs,
- the tag names are predictable and easy to remember during troubleshooting.

### Research Answers

1. **What happens if the rescue block also fails?**
   - If a task inside `rescue` fails, the block is no longer recovered and the host stays failed for that task sequence. The `always` section still runs, but the play reports a failure unless some higher-level error handling changes that behavior.

2. **Can you have nested blocks?**
   - Yes. Ansible allows nested blocks. That said, I would use them carefully because deep nesting becomes hard to read quickly.

3. **How do tags inherit to tasks within blocks?**
   - Tags applied to a block are inherited by the tasks inside that block, including `rescue` and `always` tasks associated with the block. In this lab, role-level tags are applied from the playbook, while narrower tags are applied directly on the role blocks.

---

## Task 2: Docker Compose

### Implementation Summary

- Renamed the deployment role from `app_deploy` to `web_app`.
- Kept descriptive role filenames for the web app implementation in `ansible/roles/web_app/tasks/web_app_tasks.yml` and `ansible/roles/web_app/defaults/web_app_defaults.yml`.
- Inlined the Docker role logic into `ansible/roles/docker/tasks/main.yml` and `ansible/roles/docker/handlers/main.yml`, leaving only the Ansible-required entrypoints as `main.yml`.
- Replaced the old single-container deployment logic with a Compose-based deployment in `ansible/roles/web_app/tasks/web_app_tasks.yml`.
- Added a Compose template in `ansible/roles/web_app/templates/docker-compose.yml.j2`.
- Added a role dependency in `ansible/roles/web_app/meta/main.yml` so `docker` is installed automatically before the app is deployed.
- Updated `ansible/playbooks/deploy.yml` and `ansible/playbooks/site.yml` to call `web_app`.

### Compose Deployment Design

The new role now:

- optionally logs into Docker Hub when credentials are present,
- creates the project directory under `/opt/{{ app_name }}`,
- removes the legacy standalone container before migration to Compose,
- templates a `docker-compose.yml`,
- deploys the stack with `community.docker.docker_compose_v2`,
- waits for the application port and then verifies `/health`.

### Practical Notes

- I added retries around the Compose deployment step because the first live run hit a transient Docker Hub registry timeout.

### Evidence

The deployment now works end-to-end with Docker Compose:

<details>
<summary><code>ansible-playbook playbooks/deploy.yml</code></summary>

```
$ ansible-playbook playbooks/deploy.yml

PLAY [Deploy application] *******************************************************************************************************

TASK [Gathering Facts] **********************************************************************************************************
ok: [vagrant]

TASK [Run web app role] *********************************************************************************************************
included: web_app for vagrant

TASK [docker : Load docker role defaults] ***************************************************************************************
ok: [vagrant]

TASK [docker : Install Docker prerequisites] ************************************************************************************
ok: [vagrant]

TASK [docker : Ensure Docker keyring directory exists] **************************************************************************
ok: [vagrant]

TASK [docker : Add Docker GPG key] **********************************************************************************************
ok: [vagrant]

TASK [docker : Add Docker apt repository] ***************************************************************************************
ok: [vagrant]

TASK [docker : Install Docker engine packages] **********************************************************************************
ok: [vagrant]

TASK [docker : Install Docker Python SDK package] *******************************************************************************
ok: [vagrant]

TASK [docker : Mark Docker service as ready] ************************************************************************************
ok: [vagrant]

TASK [docker : Ensure Docker service is enabled and running] ********************************************************************
ok: [vagrant]

TASK [docker : Record Docker installation block completion] *********************************************************************
ok: [vagrant]

TASK [docker : Add deployment user to docker group] *****************************************************************************
ok: [vagrant]

TASK [docker : Record Docker configuration block completion] ********************************************************************
ok: [vagrant]

TASK [web_app : Log in to Docker Hub when credentials are available] ************************************************************
ok: [vagrant]

TASK [web_app : Ensure Compose project directory exists] ************************************************************************
ok: [vagrant]

TASK [web_app : Check for legacy standalone container] **************************************************************************
ok: [vagrant]

TASK [web_app : Remove legacy standalone container before Compose migration] ****************************************************
skipping: [vagrant]

TASK [web_app : Template Docker Compose configuration] **************************************************************************
ok: [vagrant]

TASK [web_app : Deploy application stack with Docker Compose] *******************************************************************
changed: [vagrant]

TASK [web_app : Wait for application port] **************************************************************************************
ok: [vagrant -> localhost]

TASK [web_app : Verify application health endpoint] *****************************************************************************
ok: [vagrant -> localhost]

PLAY RECAP **********************************************************************************************************************
vagrant                    : ok=21   changed=1    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
```

</details>

The second deployment run proves idempotency for the Compose-based deployment:

<details>
<summary><code>ansible-playbook playbooks/deploy.yml</code> (second run)</summary>

```
$ ansible-playbook playbooks/deploy.yml

PLAY [Deploy application] *******************************************************************************************************

TASK [Gathering Facts] **********************************************************************************************************
ok: [vagrant]

TASK [Run web app role] *********************************************************************************************************
included: web_app for vagrant

TASK [docker : Load docker role defaults] ***************************************************************************************
ok: [vagrant]

TASK [docker : Install Docker prerequisites] ************************************************************************************
ok: [vagrant]

TASK [docker : Ensure Docker keyring directory exists] **************************************************************************
ok: [vagrant]

TASK [docker : Add Docker GPG key] **********************************************************************************************
ok: [vagrant]

TASK [docker : Add Docker apt repository] ***************************************************************************************
ok: [vagrant]

TASK [docker : Install Docker engine packages] **********************************************************************************
ok: [vagrant]

TASK [docker : Install Docker Python SDK package] *******************************************************************************
ok: [vagrant]

TASK [docker : Mark Docker service as ready] ************************************************************************************
ok: [vagrant]

TASK [docker : Ensure Docker service is enabled and running] ********************************************************************
ok: [vagrant]

TASK [docker : Record Docker installation block completion] *********************************************************************
ok: [vagrant]

TASK [docker : Add deployment user to docker group] *****************************************************************************
ok: [vagrant]

TASK [docker : Record Docker configuration block completion] ********************************************************************
ok: [vagrant]

TASK [web_app : Log in to Docker Hub when credentials are available] ************************************************************
ok: [vagrant]

TASK [web_app : Ensure Compose project directory exists] ************************************************************************
ok: [vagrant]

TASK [web_app : Check for legacy standalone container] **************************************************************************
ok: [vagrant]

TASK [web_app : Remove legacy standalone container before Compose migration] ****************************************************
skipping: [vagrant]

TASK [web_app : Template Docker Compose configuration] **************************************************************************
ok: [vagrant]

TASK [web_app : Deploy application stack with Docker Compose] *******************************************************************
ok: [vagrant]

TASK [web_app : Wait for application port] **************************************************************************************
ok: [vagrant -> localhost]

TASK [web_app : Verify application health endpoint] *****************************************************************************
ok: [vagrant -> localhost]

PLAY RECAP **********************************************************************************************************************
vagrant                    : ok=21   changed=0    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
```

</details>

Runtime verification on the VM confirms that the Compose stack is up and the application health endpoint is reachable:

<details>
<summary><code>docker ps -a</code></summary>

```
vagrant@devops-core-s26:~$ docker ps -a
CONTAINER ID   IMAGE                               COMMAND                  CREATED          STATUS          PORTS                                         NAMES
bc1ac63a19d3   localt0aster/devops-app-py:latest   "sh -c 'gunicorn --b…"   13 seconds ago   Up 12 seconds   0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp   devops-app
```

</details>

<details>
<summary><code>docker compose -f /opt/devops-app-py/docker-compose.yml ps</code></summary>

```
vagrant@devops-core-s26:~$ docker compose -f /opt/devops-app-py/docker-compose.yml ps
NAME         IMAGE                               COMMAND                  SERVICE         CREATED              STATUS              PORTS
devops-app   localt0aster/devops-app-py:latest   "sh -c 'gunicorn --b…"   devops-app-py   About a minute ago   Up About a minute   0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp
```

</details>

<details>
<summary><code>curl -fSsL 127.0.0.1:5000/health | jq</code></summary>

```
vagrant@devops-core-s26:~$ curl -fSsL 127.0.0.1:5000/health | jq
{
  "status": "healthy",
  "timestamp": "2026-03-06T03:15:05.637621+00:00",
  "uptime_seconds": 139
}
```

</details>

### Validation Status

- `ansible-playbook playbooks/deploy.yml --syntax-check` passes.
- `ansible-playbook playbooks/site.yml --syntax-check` passes.
- `ansible-lint` passes on the Task 2 files.
- A real deploy run succeeds with `failed=0` and `changed=1`, confirming that the Compose-based deployment works.
- A second deploy run returns `changed=0`, which demonstrates idempotency for the Compose workflow.
- The VM shows the expected running container, Compose project status, and a healthy `/health` response.

## Task 3: Wipe Logic

### Implementation Summary

- Added the wipe control variables to `ansible/roles/web_app/defaults/web_app_defaults.yml`.
- Added the wipe task file `ansible/roles/web_app/tasks/wipe.yml`.
- Included wipe processing at the top of `ansible/roles/web_app/tasks/web_app_tasks.yml` so clean reinstall works as wipe → deploy.
- Added the `web_app_wipe` tag to the `web_app` role includes in `ansible/playbooks/deploy.yml` and `ansible/playbooks/site.yml`.
- Added optional image and volume cleanup switches with safe defaults of `false`.

### Safety Design

The wipe logic uses two controls:
- `web_app_wipe: true` is required before any destructive action happens.
- `--tags web_app_wipe` allows wipe-only execution without running the deployment block.

Practical behavior:
- Normal deployment leaves wipe tasks skipped because `web_app_wipe` defaults to `false`.
- `ansible-playbook playbooks/deploy.yml -e web_app_wipe=true --tags web_app_wipe` performs wipe only.
- `ansible-playbook playbooks/deploy.yml -e web_app_wipe=true` performs clean reinstall.

I used `-e app_compose_pull_policy=missing` for the deploy-related wipe tests so Docker Hub availability would not distort the wipe-logic results. That override was only for testing.

### Evidence

The evidence file is `task3.log`.

#### Scenario 1: Normal deployment

This shows that wipe tasks are present in the role flow but are skipped by default when `web_app_wipe` is `false`.

<details>
<summary><code>ansible-playbook playbooks/deploy.yml -e app_compose_pull_policy=missing</code></summary>

```
$ ansible-playbook playbooks/deploy.yml -e app_compose_pull_policy=missing

PLAY [Deploy application] ******************************************************

TASK [Gathering Facts] *********************************************************
ok: [vagrant]

TASK [Run web app role] ********************************************************
included: web_app for vagrant

TASK [docker : Load docker role defaults] **************************************
ok: [vagrant]

TASK [docker : Install Docker prerequisites] ***********************************
ok: [vagrant]

TASK [docker : Ensure Docker keyring directory exists] *************************
ok: [vagrant]

TASK [docker : Add Docker GPG key] *********************************************
ok: [vagrant]

TASK [docker : Add Docker apt repository] **************************************
ok: [vagrant]

TASK [docker : Install Docker engine packages] *********************************
ok: [vagrant]

TASK [docker : Install Docker Python SDK package] ******************************
ok: [vagrant]

TASK [docker : Mark Docker service as ready] ***********************************
ok: [vagrant]

TASK [docker : Ensure Docker service is enabled and running] *******************
ok: [vagrant]

TASK [docker : Record Docker installation block completion] ********************
ok: [vagrant]

TASK [docker : Add deployment user to docker group] ****************************
ok: [vagrant]

TASK [docker : Record Docker configuration block completion] *******************
ok: [vagrant]

TASK [web_app : Include web app wipe tasks] ************************************
included: /home/t0ast/Repos/DevOps-Core-S26/ansible/roles/web_app/tasks/wipe.yml for vagrant

TASK [web_app : Check whether Compose file exists for wipe] ********************
ok: [vagrant]

TASK [web_app : Stop and remove Compose-managed containers] ********************
skipping: [vagrant]

TASK [web_app : Remove standalone web app container if present] ****************
skipping: [vagrant]

TASK [web_app : Remove Compose file] *******************************************
skipping: [vagrant]

TASK [web_app : Remove Compose project directory] ******************************
skipping: [vagrant]

TASK [web_app : Optionally remove deployed image] ******************************
skipping: [vagrant]

TASK [web_app : Record web app wipe completion] ********************************
skipping: [vagrant]

TASK [web_app : Report web app wipe status] ************************************
skipping: [vagrant]

TASK [web_app : Log in to Docker Hub when credentials are available] ***********
ok: [vagrant]

TASK [web_app : Ensure Compose project directory exists] ***********************
ok: [vagrant]

TASK [web_app : Check for legacy standalone container] *************************
ok: [vagrant]

TASK [web_app : Remove legacy standalone container before Compose migration] ***
skipping: [vagrant]

TASK [web_app : Template Docker Compose configuration] *************************
ok: [vagrant]

TASK [web_app : Deploy application stack with Docker Compose] ******************
ok: [vagrant]

TASK [web_app : Wait for application port] *************************************
ok: [vagrant -> localhost]

TASK [web_app : Verify application health endpoint] ****************************
ok: [vagrant -> localhost]

PLAY RECAP *********************************************************************
vagrant                    : ok=23   changed=0    unreachable=0    failed=0    skipped=8    rescued=0    ignored=0
```

</details>

<details>
<summary><code>ansible webservers -m ansible.builtin.command -a 'docker compose -f /opt/devops-app-py/docker-compose.yml ps'</code></summary>

```
$ ansible webservers -m ansible.builtin.command -a 'docker compose -f /opt/devops-app-py/docker-compose.yml ps'
vagrant | CHANGED | rc=0 >>
NAME         IMAGE                               COMMAND                  SERVICE         CREATED          STATUS          PORTS
devops-app   localt0aster/devops-app-py:latest   "sh -c 'gunicorn --b…"   devops-app-py   11 minutes ago   Up 11 minutes   0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp
```

</details>

#### Scenario 2: Wipe only

This is the explicit wipe-only path: variable enabled, tag selected, deployment tasks not executed.

<details>
<summary><code>ansible-playbook playbooks/deploy.yml -e web_app_wipe=true --tags web_app_wipe</code></summary>

```
$ ansible-playbook playbooks/deploy.yml -e web_app_wipe=true --tags web_app_wipe

PLAY [Deploy application] ******************************************************

TASK [Gathering Facts] *********************************************************
ok: [vagrant]

TASK [Run web app role] ********************************************************
included: web_app for vagrant

TASK [docker : Load docker role defaults] **************************************
ok: [vagrant]

TASK [web_app : Include web app wipe tasks] ************************************
included: /home/t0ast/Repos/DevOps-Core-S26/ansible/roles/web_app/tasks/wipe.yml for vagrant

TASK [web_app : Check whether Compose file exists for wipe] ********************
ok: [vagrant]

TASK [web_app : Stop and remove Compose-managed containers] ********************
changed: [vagrant]

TASK [web_app : Remove standalone web app container if present] ****************
ok: [vagrant]

TASK [web_app : Remove Compose file] *******************************************
changed: [vagrant]

TASK [web_app : Remove Compose project directory] ******************************
changed: [vagrant]

TASK [web_app : Optionally remove deployed image] ******************************
skipping: [vagrant]

TASK [web_app : Record web app wipe completion] ********************************
changed: [vagrant]

TASK [web_app : Report web app wipe status] ************************************
ok: [vagrant] => {
    "msg": "Web app devops-app-py wipe completed. Project directory=/opt/devops-app-py."
}

PLAY RECAP *********************************************************************
vagrant                    : ok=11   changed=4    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
```

</details>

<details>
<summary><code>ansible webservers -m ansible.builtin.shell -a "docker ps -a | grep -F devops-app || true"</code></summary>

```
$ ansible webservers -m ansible.builtin.shell -a "docker ps -a | grep -F devops-app || true"
vagrant | CHANGED | rc=0 >>
```

</details>

<details>
<summary><code>ansible webservers -m ansible.builtin.shell -a "if [ -d /opt/devops-app-py ]; then echo present; else echo absent; fi"</code></summary>

```
$ ansible webservers -m ansible.builtin.shell -a "if [ -d /opt/devops-app-py ]; then echo present; else echo absent; fi"
vagrant | CHANGED | rc=0 >>
absent
```

</details>

#### Scenario 3: Clean reinstall

This is the key workflow for Task 3: wipe first, then redeploy cleanly in the same playbook run.

<details>
<summary><code>ansible-playbook playbooks/deploy.yml -e web_app_wipe=true -e app_compose_pull_policy=missing</code></summary>

```
$ ansible-playbook playbooks/deploy.yml -e web_app_wipe=true -e app_compose_pull_policy=missing

PLAY [Deploy application] ******************************************************

TASK [Gathering Facts] *********************************************************
ok: [vagrant]

TASK [Run web app role] ********************************************************
included: web_app for vagrant

TASK [docker : Load docker role defaults] **************************************
ok: [vagrant]

TASK [docker : Install Docker prerequisites] ***********************************
ok: [vagrant]

TASK [docker : Ensure Docker keyring directory exists] *************************
ok: [vagrant]

TASK [docker : Add Docker GPG key] *********************************************
ok: [vagrant]

TASK [docker : Add Docker apt repository] **************************************
ok: [vagrant]

TASK [docker : Install Docker engine packages] *********************************
ok: [vagrant]

TASK [docker : Install Docker Python SDK package] ******************************
ok: [vagrant]

TASK [docker : Mark Docker service as ready] ***********************************
ok: [vagrant]

TASK [docker : Ensure Docker service is enabled and running] *******************
ok: [vagrant]

TASK [docker : Record Docker installation block completion] ********************
ok: [vagrant]

TASK [docker : Add deployment user to docker group] ****************************
ok: [vagrant]

TASK [docker : Record Docker configuration block completion] *******************
ok: [vagrant]

TASK [web_app : Include web app wipe tasks] ************************************
included: /home/t0ast/Repos/DevOps-Core-S26/ansible/roles/web_app/tasks/wipe.yml for vagrant

TASK [web_app : Check whether Compose file exists for wipe] ********************
ok: [vagrant]

TASK [web_app : Stop and remove Compose-managed containers] ********************
skipping: [vagrant]

TASK [web_app : Remove standalone web app container if present] ****************
ok: [vagrant]

TASK [web_app : Remove Compose file] *******************************************
ok: [vagrant]

TASK [web_app : Remove Compose project directory] ******************************
ok: [vagrant]

TASK [web_app : Optionally remove deployed image] ******************************
skipping: [vagrant]

TASK [web_app : Record web app wipe completion] ********************************
changed: [vagrant]

TASK [web_app : Report web app wipe status] ************************************
ok: [vagrant] => {
    "msg": "Web app devops-app-py wipe completed. Project directory=/opt/devops-app-py."
}

TASK [web_app : Log in to Docker Hub when credentials are available] ***********
ok: [vagrant]

TASK [web_app : Ensure Compose project directory exists] ***********************
changed: [vagrant]

TASK [web_app : Check for legacy standalone container] *************************
ok: [vagrant]

TASK [web_app : Remove legacy standalone container before Compose migration] ***
skipping: [vagrant]

TASK [web_app : Template Docker Compose configuration] *************************
changed: [vagrant]

TASK [web_app : Deploy application stack with Docker Compose] ******************
changed: [vagrant]

TASK [web_app : Wait for application port] *************************************
ok: [vagrant -> localhost]

TASK [web_app : Verify application health endpoint] ****************************
ok: [vagrant -> localhost]

PLAY RECAP *********************************************************************
vagrant                    : ok=28   changed=4    unreachable=0    failed=0    skipped=3    rescued=0    ignored=0
```

</details>

<details>
<summary><code>ansible webservers -m ansible.builtin.command -a 'docker compose -f /opt/devops-app-py/docker-compose.yml ps'</code></summary>

```
$ ansible webservers -m ansible.builtin.command -a 'docker compose -f /opt/devops-app-py/docker-compose.yml ps'
vagrant | CHANGED | rc=0 >>
NAME         IMAGE                               COMMAND                  SERVICE         CREATED         STATUS         PORTS
devops-app   localt0aster/devops-app-py:latest   "sh -c 'gunicorn --b…"   devops-app-py   4 seconds ago   Up 3 seconds   0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp
```

</details>

<details>
<summary><code>ansible webservers -m ansible.builtin.shell -a "curl -fSsL 127.0.0.1:5000/health"</code></summary>

```
$ ansible webservers -m ansible.builtin.shell -a "curl -fSsL 127.0.0.1:5000/health"
vagrant | CHANGED | rc=0 >>
{"status":"healthy","timestamp":"2026-03-06T03:24:46.458130+00:00","uptime_seconds":3}
```

</details>

#### Scenario 4: Safety checks

For Scenario 4a, the lab text says deployment should run normally when `--tags web_app_wipe` is used with `web_app_wipe=false`. In practice, Ansible tag filtering only selects the wipe-tagged path, so the deployment block does not run. The existing application remains running, which still proves the wipe did not trigger. I believe the lab wording is internally inconsistent here.

<details>
<summary><code>ansible-playbook playbooks/deploy.yml --tags web_app_wipe</code></summary>

```
$ ansible-playbook playbooks/deploy.yml --tags web_app_wipe

PLAY [Deploy application] ******************************************************

TASK [Gathering Facts] *********************************************************
ok: [vagrant]

TASK [Run web app role] ********************************************************
included: web_app for vagrant

TASK [docker : Load docker role defaults] **************************************
ok: [vagrant]

TASK [web_app : Include web app wipe tasks] ************************************
included: /home/t0ast/Repos/DevOps-Core-S26/ansible/roles/web_app/tasks/wipe.yml for vagrant

TASK [web_app : Check whether Compose file exists for wipe] ********************
ok: [vagrant]

TASK [web_app : Stop and remove Compose-managed containers] ********************
skipping: [vagrant]

TASK [web_app : Remove standalone web app container if present] ****************
skipping: [vagrant]

TASK [web_app : Remove Compose file] *******************************************
skipping: [vagrant]

TASK [web_app : Remove Compose project directory] ******************************
skipping: [vagrant]

TASK [web_app : Optionally remove deployed image] ******************************
skipping: [vagrant]

TASK [web_app : Record web app wipe completion] ********************************
skipping: [vagrant]

TASK [web_app : Report web app wipe status] ************************************
skipping: [vagrant]

PLAY RECAP *********************************************************************
vagrant                    : ok=5    changed=0    unreachable=0    failed=0    skipped=7    rescued=0    ignored=0
```

</details>

<details>
<summary><code>ansible webservers -m ansible.builtin.command -a 'docker compose -f /opt/devops-app-py/docker-compose.yml ps'</code></summary>

```
$ ansible webservers -m ansible.builtin.command -a 'docker compose -f /opt/devops-app-py/docker-compose.yml ps'
vagrant | CHANGED | rc=0 >>
NAME         IMAGE                               COMMAND                  SERVICE         CREATED          STATUS          PORTS
devops-app   localt0aster/devops-app-py:latest   "sh -c 'gunicorn --b…"   devops-app-py   11 minutes ago   Up 11 minutes   0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp
```

</details>

Scenario 4b is effectively the same selective wipe-only path as Scenario 2, but rechecked after a clean reinstall.

<details>
<summary><code>ansible-playbook playbooks/deploy.yml -e web_app_wipe=true --tags web_app_wipe</code></summary>

```
$ ansible-playbook playbooks/deploy.yml -e web_app_wipe=true --tags web_app_wipe

PLAY [Deploy application] ******************************************************

TASK [Gathering Facts] *********************************************************
ok: [vagrant]

TASK [Run web app role] ********************************************************
included: web_app for vagrant

TASK [docker : Load docker role defaults] **************************************
ok: [vagrant]

TASK [web_app : Include web app wipe tasks] ************************************
included: /home/t0ast/Repos/DevOps-Core-S26/ansible/roles/web_app/tasks/wipe.yml for vagrant

TASK [web_app : Check whether Compose file exists for wipe] ********************
ok: [vagrant]

TASK [web_app : Stop and remove Compose-managed containers] ********************
changed: [vagrant]

TASK [web_app : Remove standalone web app container if present] ****************
ok: [vagrant]

TASK [web_app : Remove Compose file] *******************************************
changed: [vagrant]

TASK [web_app : Remove Compose project directory] ******************************
changed: [vagrant]

TASK [web_app : Optionally remove deployed image] ******************************
skipping: [vagrant]

TASK [web_app : Record web app wipe completion] ********************************
ok: [vagrant]

TASK [web_app : Report web app wipe status] ************************************
ok: [vagrant] => {
    "msg": "Web app devops-app-py wipe completed. Project directory=/opt/devops-app-py."
}

PLAY RECAP *********************************************************************
vagrant                    : ok=11   changed=3    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
```

</details>

<details>
<summary><code>ansible webservers -m ansible.builtin.shell -a "docker ps -a | grep -F devops-app || true"</code></summary>

```
$ ansible webservers -m ansible.builtin.shell -a "docker ps -a | grep -F devops-app || true"
vagrant | CHANGED | rc=0 >>
```

</details>

<details>
<summary><code>ansible webservers -m ansible.builtin.shell -a "if [ -d /opt/devops-app-py ]; then echo present; else echo absent; fi"</code></summary>

```
$ ansible webservers -m ansible.builtin.shell -a "if [ -d /opt/devops-app-py ]; then echo present; else echo absent; fi"
vagrant | CHANGED | rc=0 >>
absent
```

</details>

### Validation Status

- `ansible-playbook playbooks/deploy.yml --syntax-check` passes.
- `ansible-playbook playbooks/site.yml --syntax-check` passes.
- `ansible-lint` passes on the Task 3 files.
- `ansible-playbook playbooks/deploy.yml --list-tags` shows `web_app_wipe`.
- All four wipe scenarios were exercised against the VM.
- The application was restored after testing.

### Research Answers

1. **Why use both variable AND tag?**
   - The variable is the destructive-action safety switch. The tag is the execution selector. Together they reduce accidental wipes and also support a wipe-only workflow without running normal deployment tasks.

2. **What's the difference between `never` tag and this approach?**
   - `never` disables tasks unless explicitly requested by tag, but it does not express business intent by itself. The variable-plus-tag approach is clearer because it encodes both operator intent and destructive permission. It is also easier to support clean reinstall with the same playbook run.

3. **Why must wipe logic come BEFORE deployment?**
   - Because clean reinstall is a sequential workflow: remove the old deployment first, then recreate it from a known-clean state. If wipe happened after deployment, it would destroy the fresh deployment.

4. **When would you want clean reinstallation vs. rolling update?**
   - Clean reinstall is useful when state is corrupted, migrations need a known baseline, or you want to prove reproducibility from scratch. Rolling update is better when you want lower disruption and the current deployment is already healthy.

5. **How would you extend this to wipe Docker images and volumes too?**
   - The current implementation already exposes `web_app_wipe_remove_images` and `web_app_wipe_remove_volumes`. To go further, I would add named-volume targeting, network cleanup verification, and possibly a confirmation variable for destructive data removal if persistent volumes matter.


## Task 4: CI/CD (3 pts)

### Workflow Architecture

- Added a dedicated GitHub Actions workflow in `.github/workflows/ansible-deploy.yml`.
- Split the workflow logic into local composite actions under `.github/actions/` so the workflow file stays orchestration-focused.
- Kept `lint` on `ubuntu-latest` and `deploy` on the isolated self-hosted runner labels `self-hosted`, `linux`, `vagrant`.
- Limited deployment to `push` and `workflow_dispatch`; pull requests run lint only.
- Added path filters so documentation-only changes under `ansible/docs/` do not trigger the deployment pipeline.

### Modular Actions

- `.github/actions/ansible-setup/action.yml` creates a Python virtual environment, installs `ansible-core` + `ansible-lint`, and installs required collections from `ansible/requirements.yml`.
- `.github/actions/ansible-lint/action.yml` writes the vault password to a temporary file, runs `ansible-lint`, and performs syntax checks on `provision.yml`, `deploy.yml`, and `site.yml`.
- `.github/actions/ansible-ssh-setup/action.yml` writes the target SSH key to `~/.ssh/vagrant` so the existing inventory file continues to work unchanged.
- `.github/actions/ansible-deploy/action.yml` runs `ansible-playbook playbooks/deploy.yml --tags app_deploy` and saves the playbook output as a workflow artifact.
- `.github/actions/http-healthcheck/action.yml` polls `http://<vm-host>:5000/health` and validates that the JSON reports `"status": "healthy"`.

### Secrets and Repository Settings

Required GitHub Actions secrets:
- `ANSIBLE_VAULT_PASSWORD`
- `SSH_PRIVATE_KEY`

The workflow derives the deployment target IP from `ansible/inventory/hosts.ini`, so there is no second host variable to keep in sync.
The self-hosted runner itself is isolated in the separate `github-runner` Vagrant VM described in `vagrant/README.md`.

### Files Added or Updated

- Added `.github/workflows/ansible-deploy.yml`
- Added `.github/actions/ansible-setup/action.yml`
- Added `.github/actions/ansible-lint/action.yml`
- Added `.github/actions/ansible-ssh-setup/action.yml`
- Added `.github/actions/ansible-deploy/action.yml`
- Added `.github/actions/http-healthcheck/action.yml`
- Added `ansible/requirements-ci.txt`
- Added the workflow badge to `README.md`

### Evidence

The raw GitHub Actions run log is saved locally as `task4.log`.

- Successful workflow run: <https://github.com/LocalT0aster/DevOps-Core-S26/actions/runs/22750506418>
- Event: `push`
- Branch: `lab06`
- Result: `success`
- Lint job: <https://github.com/LocalT0aster/DevOps-Core-S26/actions/runs/22750506418/job/65983854868>
- Deploy job: <https://github.com/LocalT0aster/DevOps-Core-S26/actions/runs/22750506418/job/65983886717>
- Deployment log artifact: <https://github.com/LocalT0aster/DevOps-Core-S26/actions/runs/22750506418/artifacts/5792366004>

<details>
<summary><code>Workflow run summary</code></summary>

```json
{
  "run_id": 22750506418,
  "title": "work please",
  "event": "push",
  "branch": "lab06",
  "status": "completed",
  "conclusion": "success",
  "created_at": "2026-03-06T05:29:07Z",
  "updated_at": "2026-03-06T05:31:58Z"
}
```

</details>

<details>
<summary><code>Ansible Lint job excerpt</code></summary>

```text
Passed: 0 failure(s), 0 warning(s) in 9 files processed of 9 encountered. Profile 'production' was required, and it passed.
playbook: playbooks/provision.yml
playbook: playbooks/deploy.yml
playbook: playbooks/site.yml
```

</details>

<details>
<summary><code>Deploy Application job excerpt</code></summary>

```text
Prepare vault password file
Verify target connectivity
vagrant | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
PLAY RECAP *********************************************************************
vagrant                    : ok=22   changed=0    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
Artifact ansible-deploy-log has been successfully uploaded! Final size is 808 bytes. Artifact ID is 5792366004
Remove vault password file
```

</details>

<details>
<summary><code>Health check excerpt</code></summary>

```json
{
  "status": "healthy",
  "timestamp": "2026-03-06T05:31:51.856613+00:00",
  "uptime_seconds": 7603
}
```

</details>

<details>
<summary>Full log</summary>

```log
Ansible Lint	Set up job	﻿2026-03-06T05:29:10.5329423Z Current runner version: '2.332.0'
Ansible Lint	Set up job	2026-03-06T05:29:10.5360328Z ##[group]Runner Image Provisioner
Ansible Lint	Set up job	2026-03-06T05:29:10.5361185Z Hosted Compute Agent
Ansible Lint	Set up job	2026-03-06T05:29:10.5361774Z Version: 20260213.493
Ansible Lint	Set up job	2026-03-06T05:29:10.5362403Z Commit: 5c115507f6dd24b8de37d8bbe0bb4509d0cc0fa3
Ansible Lint	Set up job	2026-03-06T05:29:10.5363145Z Build Date: 2026-02-13T00:28:41Z
Ansible Lint	Set up job	2026-03-06T05:29:10.5363778Z Worker ID: {2041351a-97c7-45c8-90a5-5ac75b9b9cf3}
Ansible Lint	Set up job	2026-03-06T05:29:10.5364557Z Azure Region: northcentralus
Ansible Lint	Set up job	2026-03-06T05:29:10.5365170Z ##[endgroup]
Ansible Lint	Set up job	2026-03-06T05:29:10.5366962Z ##[group]Operating System
Ansible Lint	Set up job	2026-03-06T05:29:10.5367667Z Ubuntu
Ansible Lint	Set up job	2026-03-06T05:29:10.5368167Z 24.04.3
Ansible Lint	Set up job	2026-03-06T05:29:10.5368631Z LTS
Ansible Lint	Set up job	2026-03-06T05:29:10.5369148Z ##[endgroup]
Ansible Lint	Set up job	2026-03-06T05:29:10.5369635Z ##[group]Runner Image
Ansible Lint	Set up job	2026-03-06T05:29:10.5370202Z Image: ubuntu-24.04
Ansible Lint	Set up job	2026-03-06T05:29:10.5370770Z Version: 20260302.42.1
Ansible Lint	Set up job	2026-03-06T05:29:10.5371770Z Included Software: https://github.com/actions/runner-images/blob/ubuntu24/20260302.42/images/ubuntu/Ubuntu2404-Readme.md
Ansible Lint	Set up job	2026-03-06T05:29:10.5373467Z Image Release: https://github.com/actions/runner-images/releases/tag/ubuntu24%2F20260302.42
Ansible Lint	Set up job	2026-03-06T05:29:10.5374434Z ##[endgroup]
Ansible Lint	Set up job	2026-03-06T05:29:10.5375723Z ##[group]GITHUB_TOKEN Permissions
Ansible Lint	Set up job	2026-03-06T05:29:10.5377590Z Contents: read
Ansible Lint	Set up job	2026-03-06T05:29:10.5378212Z Metadata: read
Ansible Lint	Set up job	2026-03-06T05:29:10.5378677Z ##[endgroup]
Ansible Lint	Set up job	2026-03-06T05:29:10.5380727Z Secret source: Actions
Ansible Lint	Set up job	2026-03-06T05:29:10.5381433Z Prepare workflow directory
Ansible Lint	Set up job	2026-03-06T05:29:10.5877192Z Prepare all required actions
Ansible Lint	Set up job	2026-03-06T05:29:10.5932576Z Getting action download info
Ansible Lint	Set up job	2026-03-06T05:29:10.8794598Z Download action repository 'actions/checkout@v4' (SHA:34e114876b0b11c390a56381ad16ebd13914f8d5)
Ansible Lint	Set up job	2026-03-06T05:29:11.1099497Z Complete job name: Ansible Lint
Ansible Lint	Checkout code	﻿2026-03-06T05:29:11.1884697Z ##[group]Run actions/checkout@v4
Ansible Lint	Checkout code	2026-03-06T05:29:11.1885706Z with:
Ansible Lint	Checkout code	2026-03-06T05:29:11.1886156Z   repository: LocalT0aster/DevOps-Core-S26
Ansible Lint	Checkout code	2026-03-06T05:29:11.1886842Z   token: ***
Ansible Lint	Checkout code	2026-03-06T05:29:11.1887231Z   ssh-strict: true
Ansible Lint	Checkout code	2026-03-06T05:29:11.1887635Z   ssh-user: git
Ansible Lint	Checkout code	2026-03-06T05:29:11.1888031Z   persist-credentials: true
Ansible Lint	Checkout code	2026-03-06T05:29:11.1888477Z   clean: true
Ansible Lint	Checkout code	2026-03-06T05:29:11.1888878Z   sparse-checkout-cone-mode: true
Ansible Lint	Checkout code	2026-03-06T05:29:11.1889348Z   fetch-depth: 1
Ansible Lint	Checkout code	2026-03-06T05:29:11.1889753Z   fetch-tags: false
Ansible Lint	Checkout code	2026-03-06T05:29:11.1890154Z   show-progress: true
Ansible Lint	Checkout code	2026-03-06T05:29:11.1890571Z   lfs: false
Ansible Lint	Checkout code	2026-03-06T05:29:11.1890938Z   submodules: false
Ansible Lint	Checkout code	2026-03-06T05:29:11.1891331Z   set-safe-directory: true
Ansible Lint	Checkout code	2026-03-06T05:29:11.1891962Z env:
Ansible Lint	Checkout code	2026-03-06T05:29:11.1892352Z   ANSIBLE_DIRECTORY: ansible
Ansible Lint	Checkout code	2026-03-06T05:29:11.1892850Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Ansible Lint	Checkout code	2026-03-06T05:29:11.1893371Z   DEPLOY_TAGS: app_deploy
Ansible Lint	Checkout code	2026-03-06T05:29:11.1893792Z ##[endgroup]
Ansible Lint	Checkout code	2026-03-06T05:29:11.2964777Z Syncing repository: LocalT0aster/DevOps-Core-S26
Ansible Lint	Checkout code	2026-03-06T05:29:11.2967010Z ##[group]Getting Git version info
Ansible Lint	Checkout code	2026-03-06T05:29:11.2967786Z Working directory is '/home/runner/work/DevOps-Core-S26/DevOps-Core-S26'
Ansible Lint	Checkout code	2026-03-06T05:29:11.2968817Z [command]/usr/bin/git version
Ansible Lint	Checkout code	2026-03-06T05:29:11.3042020Z git version 2.53.0
Ansible Lint	Checkout code	2026-03-06T05:29:11.3067759Z ##[endgroup]
Ansible Lint	Checkout code	2026-03-06T05:29:11.3081932Z Temporarily overriding HOME='/home/runner/work/_temp/890e68c6-2607-4793-b4c9-d348425e2444' before making global git config changes
Ansible Lint	Checkout code	2026-03-06T05:29:11.3094172Z Adding repository directory to the temporary git global config as a safe directory
Ansible Lint	Checkout code	2026-03-06T05:29:11.3095606Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/DevOps-Core-S26/DevOps-Core-S26
Ansible Lint	Checkout code	2026-03-06T05:29:11.3134382Z Deleting the contents of '/home/runner/work/DevOps-Core-S26/DevOps-Core-S26'
Ansible Lint	Checkout code	2026-03-06T05:29:11.3138290Z ##[group]Initializing the repository
Ansible Lint	Checkout code	2026-03-06T05:29:11.3142225Z [command]/usr/bin/git init /home/runner/work/DevOps-Core-S26/DevOps-Core-S26
Ansible Lint	Checkout code	2026-03-06T05:29:11.3230735Z hint: Using 'master' as the name for the initial branch. This default branch name
Ansible Lint	Checkout code	2026-03-06T05:29:11.3232149Z hint: will change to "main" in Git 3.0. To configure the initial branch name
Ansible Lint	Checkout code	2026-03-06T05:29:11.3233366Z hint: to use in all of your new repositories, which will suppress this warning,
Ansible Lint	Checkout code	2026-03-06T05:29:11.3234537Z hint: call:
Ansible Lint	Checkout code	2026-03-06T05:29:11.3235183Z hint:
Ansible Lint	Checkout code	2026-03-06T05:29:11.3236155Z hint: 	git config --global init.defaultBranch <name>
Ansible Lint	Checkout code	2026-03-06T05:29:11.3236776Z hint:
Ansible Lint	Checkout code	2026-03-06T05:29:11.3237351Z hint: Names commonly chosen instead of 'master' are 'main', 'trunk' and
Ansible Lint	Checkout code	2026-03-06T05:29:11.3238302Z hint: 'development'. The just-created branch can be renamed via this command:
Ansible Lint	Checkout code	2026-03-06T05:29:11.3239050Z hint:
Ansible Lint	Checkout code	2026-03-06T05:29:11.3239448Z hint: 	git branch -m <name>
Ansible Lint	Checkout code	2026-03-06T05:29:11.3240148Z hint:
Ansible Lint	Checkout code	2026-03-06T05:29:11.3240823Z hint: Disable this message with "git config set advice.defaultBranchName false"
Ansible Lint	Checkout code	2026-03-06T05:29:11.3242206Z Initialized empty Git repository in /home/runner/work/DevOps-Core-S26/DevOps-Core-S26/.git/
Ansible Lint	Checkout code	2026-03-06T05:29:11.3246185Z [command]/usr/bin/git remote add origin https://github.com/LocalT0aster/DevOps-Core-S26
Ansible Lint	Checkout code	2026-03-06T05:29:11.3279691Z ##[endgroup]
Ansible Lint	Checkout code	2026-03-06T05:29:11.3280429Z ##[group]Disabling automatic garbage collection
Ansible Lint	Checkout code	2026-03-06T05:29:11.3284110Z [command]/usr/bin/git config --local gc.auto 0
Ansible Lint	Checkout code	2026-03-06T05:29:11.3312715Z ##[endgroup]
Ansible Lint	Checkout code	2026-03-06T05:29:11.3313412Z ##[group]Setting up auth
Ansible Lint	Checkout code	2026-03-06T05:29:11.3319862Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
Ansible Lint	Checkout code	2026-03-06T05:29:11.3350673Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
Ansible Lint	Checkout code	2026-03-06T05:29:11.3675159Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
Ansible Lint	Checkout code	2026-03-06T05:29:11.3706457Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
Ansible Lint	Checkout code	2026-03-06T05:29:11.3938616Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
Ansible Lint	Checkout code	2026-03-06T05:29:11.3969877Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
Ansible Lint	Checkout code	2026-03-06T05:29:11.4214694Z [command]/usr/bin/git config --local http.https://github.com/.extraheader AUTHORIZATION: basic ***
Ansible Lint	Checkout code	2026-03-06T05:29:11.4250962Z ##[endgroup]
Ansible Lint	Checkout code	2026-03-06T05:29:11.4251733Z ##[group]Fetching the repository
Ansible Lint	Checkout code	2026-03-06T05:29:11.4259070Z [command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +2492c7d27ac02a50f12e2ca7f51bc1d7882b8489:refs/remotes/origin/lab06
Ansible Lint	Checkout code	2026-03-06T05:29:11.7606599Z From https://github.com/LocalT0aster/DevOps-Core-S26
Ansible Lint	Checkout code	2026-03-06T05:29:11.7607942Z  * [new ref]         2492c7d27ac02a50f12e2ca7f51bc1d7882b8489 -> origin/lab06
Ansible Lint	Checkout code	2026-03-06T05:29:11.7641114Z ##[endgroup]
Ansible Lint	Checkout code	2026-03-06T05:29:11.7641819Z ##[group]Determining the checkout info
Ansible Lint	Checkout code	2026-03-06T05:29:11.7644340Z ##[endgroup]
Ansible Lint	Checkout code	2026-03-06T05:29:11.7651042Z [command]/usr/bin/git sparse-checkout disable
Ansible Lint	Checkout code	2026-03-06T05:29:11.7694047Z [command]/usr/bin/git config --local --unset-all extensions.worktreeConfig
Ansible Lint	Checkout code	2026-03-06T05:29:11.7726044Z ##[group]Checking out the ref
Ansible Lint	Checkout code	2026-03-06T05:29:11.7730689Z [command]/usr/bin/git checkout --progress --force -B lab06 refs/remotes/origin/lab06
Ansible Lint	Checkout code	2026-03-06T05:29:11.7916810Z Switched to a new branch 'lab06'
Ansible Lint	Checkout code	2026-03-06T05:29:11.7920253Z branch 'lab06' set up to track 'origin/lab06'.
Ansible Lint	Checkout code	2026-03-06T05:29:11.7927351Z ##[endgroup]
Ansible Lint	Checkout code	2026-03-06T05:29:11.7961096Z [command]/usr/bin/git log -1 --format=%H
Ansible Lint	Checkout code	2026-03-06T05:29:11.7984326Z 2492c7d27ac02a50f12e2ca7f51bc1d7882b8489
Ansible Lint	Setup Ansible toolchain	﻿2026-03-06T05:29:11.8266011Z Prepare all required actions
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:11.8266740Z Getting action download info
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:11.9642088Z Download action repository 'actions/setup-python@v5' (SHA:a26af69be951a213d495a4c3e4e4022e16d87065)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.0926196Z Download action repository 'actions/cache@v4' (SHA:0057852bfaa89a56745cba8c7296529d2fc39830)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2754803Z ##[group]Run ./.github/actions/ansible-setup
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2756101Z with:
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2756875Z   python-version: 3.12
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2757772Z   working-directory: ansible
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2758919Z   python-requirements-path: ansible/requirements-ci.txt
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2760341Z   collection-requirements-path: ansible/requirements.yml
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2761526Z env:
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2762260Z   ANSIBLE_DIRECTORY: ansible
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2763240Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2764268Z   DEPLOY_TAGS: app_deploy
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2765123Z ##[endgroup]
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2953557Z ##[group]Run actions/setup-python@v5
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2954605Z with:
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2955561Z   python-version: 3.12
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2956433Z   check-latest: false
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2957494Z   token: ***
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2958279Z   update-environment: true
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2959180Z   allow-prereleases: false
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2960062Z   freethreaded: false
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2960864Z env:
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2961589Z   ANSIBLE_DIRECTORY: ansible
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2962544Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2963542Z   DEPLOY_TAGS: app_deploy
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.2964389Z ##[endgroup]
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.4642413Z ##[group]Installed versions
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.4726679Z Successfully set up CPython (3.12.12)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.4729711Z ##[endgroup]
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.5526985Z ##[group]Run actions/cache@v4
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.5527927Z with:
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.5528767Z   path: ~/.cache/pip
Ansible Lint	Setup Ansible toolchain	~/.ansible/collections
Ansible Lint	Setup Ansible toolchain	
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.5530434Z   key: Linux-py3.12-ansible-70fee6f2b98d7def1a2c43ddbf364d7b6b2648821ca185e0955c8d98e4cb9364
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.5532114Z   restore-keys: Linux-py3.12-ansible-
Ansible Lint	Setup Ansible toolchain	
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.5533131Z   enableCrossOsArchive: false
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.5534054Z   fail-on-cache-miss: false
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.5534903Z   lookup-only: false
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.5535979Z   save-always: false
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.5536767Z env:
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.5537478Z   ANSIBLE_DIRECTORY: ansible
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.5538412Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.5539397Z   DEPLOY_TAGS: app_deploy
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.5540456Z   pythonLocation: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.5541914Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.12.12/x64/lib/pkgconfig
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.5543343Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.5544669Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.5546641Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.5548045Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.12.12/x64/lib
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.5549177Z ##[endgroup]
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:12.8056849Z Cache hit for: Linux-py3.12-ansible-70fee6f2b98d7def1a2c43ddbf364d7b6b2648821ca185e0955c8d98e4cb9364
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.2661813Z Received 16876233 of 16876233 (100.0%), 45.1 MBs/sec
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.2662769Z Cache Size: ~16 MB (16876233 B)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.2695856Z [command]/usr/bin/tar -xf /home/runner/work/_temp/ed14daa5-3d21-447d-b84b-82030a283c55/cache.tzst -P -C /home/runner/work/DevOps-Core-S26/DevOps-Core-S26 --use-compress-program unzstd
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.3615615Z Cache restored successfully
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.3743008Z Cache restored from key: Linux-py3.12-ansible-70fee6f2b98d7def1a2c43ddbf364d7b6b2648821ca185e0955c8d98e4cb9364
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.3852777Z ##[group]Run set -euo pipefail
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.3853186Z [36;1mset -euo pipefail[0m
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.3853496Z [36;1mrm -rf "ansible/.venv-ci"[0m
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.3853828Z [36;1mpython -m venv "ansible/.venv-ci"[0m
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.3854470Z [36;1m. "ansible/.venv-ci/bin/activate"[0m
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.3854821Z [36;1mpython -m pip install --upgrade pip[0m
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.3855722Z [36;1mpython -m pip install -r "ansible/requirements-ci.txt"[0m
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.3912991Z shell: /usr/bin/bash --noprofile --norc -e -o pipefail {0}
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.3913612Z env:
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.3913856Z   ANSIBLE_DIRECTORY: ansible
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.3914173Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.3914488Z   DEPLOY_TAGS: app_deploy
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.3914830Z   pythonLocation: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.3915535Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.12.12/x64/lib/pkgconfig
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.3916011Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.3916433Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.3916855Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.3917310Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.12.12/x64/lib
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:13.3917678Z ##[endgroup]
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:17.4817418Z Requirement already satisfied: pip in ./ansible/.venv-ci/lib/python3.12/site-packages (25.0.1)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:17.5674329Z Collecting pip
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:17.5687767Z   Using cached pip-26.0.1-py3-none-any.whl.metadata (4.7 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:17.5720838Z Using cached pip-26.0.1-py3-none-any.whl (1.8 MB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:17.5891297Z Installing collected packages: pip
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:17.5893687Z   Attempting uninstall: pip
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:17.5915418Z     Found existing installation: pip 25.0.1
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:17.6291717Z     Uninstalling pip-25.0.1:
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:17.6349799Z       Successfully uninstalled pip-25.0.1
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:18.7331183Z Successfully installed pip-26.0.1
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.2368546Z Collecting ansible-core<2.20,>=2.16 (from -r ansible/requirements-ci.txt (line 1))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.2386317Z   Using cached ansible_core-2.19.7-py3-none-any.whl.metadata (7.7 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.2666691Z Collecting ansible-lint==26.3.0 (from -r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.2678442Z   Using cached ansible_lint-26.3.0-py3-none-any.whl.metadata (6.2 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.2841853Z Collecting ansible-compat>=25.8.2 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.2853515Z   Using cached ansible_compat-25.12.1-py3-none-any.whl.metadata (3.4 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.3324507Z Collecting black>=24.3.0 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.3340053Z   Using cached black-26.1.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (88 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.4392554Z Collecting cffi>=1.15.1 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.4410566Z   Using cached cffi-2.0.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (2.6 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.6020587Z Collecting cryptography>=37 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.6039889Z   Using cached cryptography-46.0.5-cp311-abi3-manylinux_2_34_x86_64.whl.metadata (5.7 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.6171492Z Collecting distro>=1.9.0 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.6182889Z   Using cached distro-1.9.0-py3-none-any.whl.metadata (6.8 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.6342972Z Collecting filelock>=3.8.2 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.6354454Z   Using cached filelock-3.25.0-py3-none-any.whl.metadata (2.0 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.6530994Z Collecting jsonschema>=4.10.0 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.6542552Z   Using cached jsonschema-4.26.0-py3-none-any.whl.metadata (7.6 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.6681268Z Collecting packaging>=22.0 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.6693036Z   Using cached packaging-26.0-py3-none-any.whl.metadata (3.3 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.6782352Z Collecting pathspec<1.1.0,>=1.0.3 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.6793421Z   Using cached pathspec-1.0.4-py3-none-any.whl.metadata (13 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.7114486Z Collecting pyyaml>=6.0.1 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.7127355Z   Using cached pyyaml-6.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.4 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.7288961Z Collecting referencing>=0.36.2 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.7300535Z   Using cached referencing-0.37.0-py3-none-any.whl.metadata (2.8 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.8438693Z Collecting ruamel-yaml>=0.18.11 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.8451054Z   Using cached ruamel_yaml-0.19.1-py3-none-any.whl.metadata (16 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.8808593Z Collecting ruamel-yaml-clib>=0.2.12 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.8822030Z   Using cached ruamel_yaml_clib-0.2.15-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (3.5 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.8919802Z Collecting subprocess-tee>=0.4.1 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.8931570Z   Using cached subprocess_tee-0.4.2-py3-none-any.whl.metadata (3.3 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.9056242Z Collecting wcmatch>=8.5.0 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.9067895Z   Using cached wcmatch-10.1-py3-none-any.whl.metadata (5.1 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.9186855Z Collecting yamllint>=1.38.0 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.9197893Z   Using cached yamllint-1.38.0-py3-none-any.whl.metadata (4.2 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.9318148Z Collecting jinja2>=3.1.0 (from ansible-core<2.20,>=2.16->-r ansible/requirements-ci.txt (line 1))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.9329139Z   Using cached jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.9434075Z Collecting resolvelib<2.0.0,>=0.5.3 (from ansible-core<2.20,>=2.16->-r ansible/requirements-ci.txt (line 1))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.9445494Z   Using cached resolvelib-1.2.1-py3-none-any.whl.metadata (3.7 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.9621498Z Collecting click>=8.0.0 (from black>=24.3.0->ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.9632716Z   Using cached click-8.3.1-py3-none-any.whl.metadata (2.6 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.9715932Z Collecting mypy-extensions>=0.4.3 (from black>=24.3.0->ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.9727321Z   Using cached mypy_extensions-1.1.0-py3-none-any.whl.metadata (1.1 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.9890085Z Collecting platformdirs>=2 (from black>=24.3.0->ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:19.9901303Z   Using cached platformdirs-4.9.4-py3-none-any.whl.metadata (4.7 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.0017127Z Collecting pytokens>=0.3.0 (from black>=24.3.0->ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.0028577Z   Using cached pytokens-0.4.1-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (3.8 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.0121729Z Collecting pycparser (from cffi>=1.15.1->ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.0132684Z   Using cached pycparser-3.0-py3-none-any.whl.metadata (8.2 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.0616368Z Collecting MarkupSafe>=2.0 (from jinja2>=3.1.0->ansible-core<2.20,>=2.16->-r ansible/requirements-ci.txt (line 1))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.0628729Z   Using cached markupsafe-3.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.7 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.0956111Z Collecting attrs>=22.2.0 (from jsonschema>=4.10.0->ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.0968028Z   Using cached attrs-25.4.0-py3-none-any.whl.metadata (10 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.1071916Z Collecting jsonschema-specifications>=2023.03.6 (from jsonschema>=4.10.0->ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.1087218Z   Using cached jsonschema_specifications-2025.9.1-py3-none-any.whl.metadata (2.9 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.3427391Z Collecting rpds-py>=0.25.0 (from jsonschema>=4.10.0->ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.3441048Z   Using cached rpds_py-0.30.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (4.1 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.3652689Z Collecting typing-extensions>=4.4.0 (from referencing>=0.36.2->ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.3664703Z   Using cached typing_extensions-4.15.0-py3-none-any.whl.metadata (3.3 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.3790215Z Collecting bracex>=2.1.1 (from wcmatch>=8.5.0->ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.3800941Z   Using cached bracex-2.6-py3-none-any.whl.metadata (3.6 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.3843568Z Using cached ansible_lint-26.3.0-py3-none-any.whl (330 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.3857264Z Using cached ansible_core-2.19.7-py3-none-any.whl (2.4 MB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.3886025Z Using cached pathspec-1.0.4-py3-none-any.whl (55 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.3897085Z Using cached resolvelib-1.2.1-py3-none-any.whl (18 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.3908164Z Using cached ansible_compat-25.12.1-py3-none-any.whl (27 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.3919566Z Using cached black-26.1.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (1.8 MB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.3943377Z Using cached cffi-2.0.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (219 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.3955512Z Using cached click-8.3.1-py3-none-any.whl (108 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.3967497Z Using cached cryptography-46.0.5-cp311-abi3-manylinux_2_34_x86_64.whl (4.5 MB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4010695Z Using cached distro-1.9.0-py3-none-any.whl (20 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4021518Z Using cached filelock-3.25.0-py3-none-any.whl (26 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4032600Z Using cached jinja2-3.1.6-py3-none-any.whl (134 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4044242Z Using cached jsonschema-4.26.0-py3-none-any.whl (90 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4055630Z Using cached attrs-25.4.0-py3-none-any.whl (67 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4067265Z Using cached jsonschema_specifications-2025.9.1-py3-none-any.whl (18 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4078725Z Using cached markupsafe-3.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (22 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4089307Z Using cached mypy_extensions-1.1.0-py3-none-any.whl (5.0 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4099989Z Using cached packaging-26.0-py3-none-any.whl (74 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4111364Z Using cached platformdirs-4.9.4-py3-none-any.whl (21 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4122788Z Using cached pytokens-0.4.1-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (269 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4135685Z Using cached pyyaml-6.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (807 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4152160Z Using cached referencing-0.37.0-py3-none-any.whl (26 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4163610Z Using cached rpds_py-0.30.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (394 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4177318Z Using cached ruamel_yaml-0.19.1-py3-none-any.whl (118 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4189476Z Using cached ruamel_yaml_clib-0.2.15-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (788 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4205121Z Using cached subprocess_tee-0.4.2-py3-none-any.whl (5.2 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4216469Z Using cached typing_extensions-4.15.0-py3-none-any.whl (44 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4227263Z Using cached wcmatch-10.1-py3-none-any.whl (39 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4238042Z Using cached bracex-2.6-py3-none-any.whl (11 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4248958Z Using cached yamllint-1.38.0-py3-none-any.whl (68 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.4260046Z Using cached pycparser-3.0-py3-none-any.whl (48 kB)
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:20.5136341Z Installing collected packages: typing-extensions, subprocess-tee, ruamel-yaml-clib, ruamel-yaml, rpds-py, resolvelib, pyyaml, pytokens, pycparser, platformdirs, pathspec, packaging, mypy-extensions, MarkupSafe, filelock, distro, click, bracex, attrs, yamllint, wcmatch, referencing, jinja2, cffi, black, jsonschema-specifications, cryptography, jsonschema, ansible-core, ansible-compat, ansible-lint
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:23.1752917Z 
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:23.1786289Z Successfully installed MarkupSafe-3.0.3 ansible-compat-25.12.1 ansible-core-2.19.7 ansible-lint-26.3.0 attrs-25.4.0 black-26.1.0 bracex-2.6 cffi-2.0.0 click-8.3.1 cryptography-46.0.5 distro-1.9.0 filelock-3.25.0 jinja2-3.1.6 jsonschema-4.26.0 jsonschema-specifications-2025.9.1 mypy-extensions-1.1.0 packaging-26.0 pathspec-1.0.4 platformdirs-4.9.4 pycparser-3.0 pytokens-0.4.1 pyyaml-6.0.3 referencing-0.37.0 resolvelib-1.2.1 rpds-py-0.30.0 ruamel-yaml-0.19.1 ruamel-yaml-clib-0.2.15 subprocess-tee-0.4.2 typing-extensions-4.15.0 wcmatch-10.1 yamllint-1.38.0
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:23.3132093Z ##[group]Run set -euo pipefail
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:23.3132406Z [36;1mset -euo pipefail[0m
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:23.3132646Z [36;1m. "ansible/.venv-ci/bin/activate"[0m
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:23.3133042Z [36;1mansible-galaxy collection install -r "ansible/requirements.yml"[0m
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:23.3182494Z shell: /usr/bin/bash --noprofile --norc -e -o pipefail {0}
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:23.3182814Z env:
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:23.3182995Z   ANSIBLE_DIRECTORY: ansible
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:23.3183248Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:23.3183513Z   DEPLOY_TAGS: app_deploy
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:23.3183785Z   pythonLocation: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:23.3184216Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.12.12/x64/lib/pkgconfig
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:23.3184628Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:23.3185008Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:23.3185717Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:23.3186089Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.12.12/x64/lib
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:23.3186397Z ##[endgroup]
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:24.0929765Z Starting galaxy collection install process
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:24.0931533Z Nothing to do. All requested collections are already installed. If you want to reinstall them, consider using `--force`.
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:24.1336095Z ##[group]Run echo "/home/runner/work/DevOps-Core-S26/DevOps-Core-S26/ansible/.venv-ci/bin" >> "$GITHUB_PATH"
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:24.1336846Z [36;1mecho "/home/runner/work/DevOps-Core-S26/DevOps-Core-S26/ansible/.venv-ci/bin" >> "$GITHUB_PATH"[0m
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:24.1385886Z shell: /usr/bin/bash --noprofile --norc -e -o pipefail {0}
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:24.1386212Z env:
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:24.1386392Z   ANSIBLE_DIRECTORY: ansible
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:24.1386668Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:24.1386930Z   DEPLOY_TAGS: app_deploy
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:24.1387207Z   pythonLocation: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:24.1387607Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.12.12/x64/lib/pkgconfig
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:24.1388033Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:24.1388398Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:24.1388756Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:24.1389121Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.12.12/x64/lib
Ansible Lint	Setup Ansible toolchain	2026-03-06T05:29:24.1389428Z ##[endgroup]
Ansible Lint	Run lint and syntax checks	﻿2026-03-06T05:29:24.1511346Z Prepare all required actions
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1552577Z ##[group]Run ./.github/actions/ansible-lint
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1552839Z with:
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1553022Z   ansible-directory: ansible
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1553378Z   vault-password: ***
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1553613Z   playbook-glob: playbooks/*.yml
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1553834Z env:
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1554006Z   ANSIBLE_DIRECTORY: ansible
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1554240Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1554495Z   DEPLOY_TAGS: app_deploy
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1554766Z   pythonLocation: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1555562Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.12.12/x64/lib/pkgconfig
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1555969Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1556338Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1556697Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1557060Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.12.12/x64/lib
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1557393Z ##[endgroup]
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1572559Z ##[group]Run set -euo pipefail
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1572828Z [36;1mset -euo pipefail[0m
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1573053Z [36;1mumask 077[0m
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1573263Z [36;1mcleanup() {[0m
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1573461Z [36;1m  rm -f .vault_pass[0m
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1573674Z [36;1m}[0m
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1573857Z [36;1mtrap cleanup EXIT[0m
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1574064Z [36;1m[0m
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1574274Z [36;1mprintf '%s\n' "$VAULT_PASSWORD" > .vault_pass[0m
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1574564Z [36;1m[0m
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1574750Z [36;1mansible-lint $PLAYBOOK_GLOB[0m
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1575099Z [36;1mansible-playbook playbooks/provision.yml --syntax-check[0m
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1575667Z [36;1mansible-playbook playbooks/deploy.yml --syntax-check[0m
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1576063Z [36;1mansible-playbook playbooks/site.yml --syntax-check[0m
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1619676Z shell: /usr/bin/bash --noprofile --norc -e -o pipefail {0}
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1620023Z env:
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1620202Z   ANSIBLE_DIRECTORY: ansible
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1620452Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1620726Z   DEPLOY_TAGS: app_deploy
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1621008Z   pythonLocation: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1621412Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.12.12/x64/lib/pkgconfig
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1621812Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1622192Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1622568Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.12/x64
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1622936Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.12.12/x64/lib
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1623292Z   VAULT_PASSWORD: ***
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1623509Z   PLAYBOOK_GLOB: playbooks/*.yml
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:24.1623738Z ##[endgroup]
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:29.8477378Z 
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:30.0769311Z Passed: 0 failure(s), 0 warning(s) in 9 files processed of 9 encountered. Profile 'production' was required, and it passed.
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:30.6324210Z 
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:30.6324827Z playbook: playbooks/provision.yml
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:31.1404326Z 
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:31.1405013Z playbook: playbooks/deploy.yml
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:31.6590152Z 
Ansible Lint	Run lint and syntax checks	2026-03-06T05:29:31.6590785Z playbook: playbooks/site.yml
Ansible Lint	Post Setup Ansible toolchain	﻿2026-03-06T05:29:31.7061977Z Post job cleanup.
Ansible Lint	Post Setup Ansible toolchain	2026-03-06T05:29:31.7645652Z Post job cleanup.
Ansible Lint	Post Setup Ansible toolchain	2026-03-06T05:29:31.8932691Z Cache hit occurred on the primary key Linux-py3.12-ansible-70fee6f2b98d7def1a2c43ddbf364d7b6b2648821ca185e0955c8d98e4cb9364, not saving cache.
Ansible Lint	Post Setup Ansible toolchain	2026-03-06T05:29:31.9026958Z Post job cleanup.
Ansible Lint	Post Checkout code	﻿2026-03-06T05:29:32.0691853Z Post job cleanup.
Ansible Lint	Post Checkout code	2026-03-06T05:29:32.1650325Z [command]/usr/bin/git version
Ansible Lint	Post Checkout code	2026-03-06T05:29:32.1687355Z git version 2.53.0
Ansible Lint	Post Checkout code	2026-03-06T05:29:32.1730032Z Temporarily overriding HOME='/home/runner/work/_temp/6c20ae22-94d6-4e20-a088-1bc5b65e29e6' before making global git config changes
Ansible Lint	Post Checkout code	2026-03-06T05:29:32.1731346Z Adding repository directory to the temporary git global config as a safe directory
Ansible Lint	Post Checkout code	2026-03-06T05:29:32.1744172Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/DevOps-Core-S26/DevOps-Core-S26
Ansible Lint	Post Checkout code	2026-03-06T05:29:32.1779165Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
Ansible Lint	Post Checkout code	2026-03-06T05:29:32.1812297Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
Ansible Lint	Post Checkout code	2026-03-06T05:29:32.2056254Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
Ansible Lint	Post Checkout code	2026-03-06T05:29:32.2077494Z http.https://github.com/.extraheader
Ansible Lint	Post Checkout code	2026-03-06T05:29:32.2089800Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
Ansible Lint	Post Checkout code	2026-03-06T05:29:32.2121225Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
Ansible Lint	Post Checkout code	2026-03-06T05:29:32.2357989Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
Ansible Lint	Post Checkout code	2026-03-06T05:29:32.2390371Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
Ansible Lint	Complete job	﻿2026-03-06T05:29:32.2730379Z Cleaning up orphan processes
Deploy Application	Set up job	﻿2026-03-06T05:29:57.6492178Z Current runner version: '2.332.0'
Deploy Application	Set up job	2026-03-06T05:29:57.6500080Z Runner name: 'github-runner-s26'
Deploy Application	Set up job	2026-03-06T05:29:57.6501133Z Runner group name: 'Default'
Deploy Application	Set up job	2026-03-06T05:29:57.6502174Z Machine name: 'github-runner-s26'
Deploy Application	Set up job	2026-03-06T05:29:57.6505769Z ##[group]GITHUB_TOKEN Permissions
Deploy Application	Set up job	2026-03-06T05:29:57.6508764Z Contents: read
Deploy Application	Set up job	2026-03-06T05:29:57.6509511Z Metadata: read
Deploy Application	Set up job	2026-03-06T05:29:57.6510335Z ##[endgroup]
Deploy Application	Set up job	2026-03-06T05:29:57.6513654Z Secret source: Actions
Deploy Application	Set up job	2026-03-06T05:29:57.6514727Z Prepare workflow directory
Deploy Application	Set up job	2026-03-06T05:29:57.6992670Z Prepare all required actions
Deploy Application	Set up job	2026-03-06T05:29:57.7029327Z Getting action download info
Deploy Application	Set up job	2026-03-06T05:29:58.7100830Z Download action repository 'actions/checkout@v4' (SHA:34e114876b0b11c390a56381ad16ebd13914f8d5)
Deploy Application	Set up job	2026-03-06T05:29:59.9331090Z Download action repository 'actions/upload-artifact@v4' (SHA:ea165f8d65b6e75b540449e92b4886f43607fa02)
Deploy Application	Set up job	2026-03-06T05:30:04.4739595Z Complete job name: Deploy Application
Deploy Application	Checkout code	﻿2026-03-06T05:30:04.5258726Z ##[group]Run actions/checkout@v4
Deploy Application	Checkout code	2026-03-06T05:30:04.5259351Z with:
Deploy Application	Checkout code	2026-03-06T05:30:04.5259658Z   repository: LocalT0aster/DevOps-Core-S26
Deploy Application	Checkout code	2026-03-06T05:30:04.5260233Z   token: ***
Deploy Application	Checkout code	2026-03-06T05:30:04.5260506Z   ssh-strict: true
Deploy Application	Checkout code	2026-03-06T05:30:04.5260779Z   ssh-user: git
Deploy Application	Checkout code	2026-03-06T05:30:04.5261051Z   persist-credentials: true
Deploy Application	Checkout code	2026-03-06T05:30:04.5261350Z   clean: true
Deploy Application	Checkout code	2026-03-06T05:30:04.5261712Z   sparse-checkout-cone-mode: true
Deploy Application	Checkout code	2026-03-06T05:30:04.5283182Z   fetch-depth: 1
Deploy Application	Checkout code	2026-03-06T05:30:04.5283514Z   fetch-tags: false
Deploy Application	Checkout code	2026-03-06T05:30:04.5283905Z   show-progress: true
Deploy Application	Checkout code	2026-03-06T05:30:04.5284216Z   lfs: false
Deploy Application	Checkout code	2026-03-06T05:30:04.5284495Z   submodules: false
Deploy Application	Checkout code	2026-03-06T05:30:04.5284768Z   set-safe-directory: true
Deploy Application	Checkout code	2026-03-06T05:30:04.5285558Z env:
Deploy Application	Checkout code	2026-03-06T05:30:04.5285829Z   ANSIBLE_DIRECTORY: ansible
Deploy Application	Checkout code	2026-03-06T05:30:04.5286151Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Deploy Application	Checkout code	2026-03-06T05:30:04.5286485Z   DEPLOY_TAGS: app_deploy
Deploy Application	Checkout code	2026-03-06T05:30:04.5286765Z ##[endgroup]
Deploy Application	Checkout code	2026-03-06T05:30:04.6162086Z Syncing repository: LocalT0aster/DevOps-Core-S26
Deploy Application	Checkout code	2026-03-06T05:30:04.6172832Z ##[group]Getting Git version info
Deploy Application	Checkout code	2026-03-06T05:30:04.6173515Z Working directory is '/opt/actions-runner/_work/DevOps-Core-S26/DevOps-Core-S26'
Deploy Application	Checkout code	2026-03-06T05:30:04.6174360Z [command]/usr/bin/git version
Deploy Application	Checkout code	2026-03-06T05:30:04.6174679Z git version 2.52.0
Deploy Application	Checkout code	2026-03-06T05:30:04.6189251Z ##[endgroup]
Deploy Application	Checkout code	2026-03-06T05:30:04.6201711Z Temporarily overriding HOME='/opt/actions-runner/_work/_temp/02e2583d-1f43-4511-ab95-a17dab0dc139' before making global git config changes
Deploy Application	Checkout code	2026-03-06T05:30:04.6202668Z Adding repository directory to the temporary git global config as a safe directory
Deploy Application	Checkout code	2026-03-06T05:30:04.6226851Z [command]/usr/bin/git config --global --add safe.directory /opt/actions-runner/_work/DevOps-Core-S26/DevOps-Core-S26
Deploy Application	Checkout code	2026-03-06T05:30:04.6268709Z [command]/usr/bin/git config --local --get remote.origin.url
Deploy Application	Checkout code	2026-03-06T05:30:04.6289926Z https://github.com/LocalT0aster/DevOps-Core-S26
Deploy Application	Checkout code	2026-03-06T05:30:04.6302713Z ##[group]Removing previously created refs, to avoid conflicts
Deploy Application	Checkout code	2026-03-06T05:30:04.6306437Z [command]/usr/bin/git rev-parse --symbolic-full-name --verify --quiet HEAD
Deploy Application	Checkout code	2026-03-06T05:30:04.6335472Z refs/heads/lab06
Deploy Application	Checkout code	2026-03-06T05:30:04.6360933Z [command]/usr/bin/git checkout --detach
Deploy Application	Checkout code	2026-03-06T05:30:04.6361427Z HEAD is now at a55c6b2 fix: rebuild ansible ci venv on each run
Deploy Application	Checkout code	2026-03-06T05:30:04.6399727Z [command]/usr/bin/git branch --delete --force lab06
Deploy Application	Checkout code	2026-03-06T05:30:04.6419714Z Deleted branch lab06 (was a55c6b2).
Deploy Application	Checkout code	2026-03-06T05:30:04.6444500Z ##[endgroup]
Deploy Application	Checkout code	2026-03-06T05:30:04.6447185Z [command]/usr/bin/git submodule status
Deploy Application	Checkout code	2026-03-06T05:30:04.6599060Z ##[group]Cleaning the repository
Deploy Application	Checkout code	2026-03-06T05:30:04.6599701Z [command]/usr/bin/git clean -ffdx
Deploy Application	Checkout code	2026-03-06T05:30:04.7382400Z Removing ansible/.venv-ci/
Deploy Application	Checkout code	2026-03-06T05:30:04.7399074Z [command]/usr/bin/git reset --hard HEAD
Deploy Application	Checkout code	2026-03-06T05:30:04.7435602Z HEAD is now at a55c6b2 fix: rebuild ansible ci venv on each run
Deploy Application	Checkout code	2026-03-06T05:30:04.7439527Z ##[endgroup]
Deploy Application	Checkout code	2026-03-06T05:30:04.7441304Z ##[group]Disabling automatic garbage collection
Deploy Application	Checkout code	2026-03-06T05:30:04.7446972Z [command]/usr/bin/git config --local gc.auto 0
Deploy Application	Checkout code	2026-03-06T05:30:04.7478554Z ##[endgroup]
Deploy Application	Checkout code	2026-03-06T05:30:04.7479110Z ##[group]Setting up auth
Deploy Application	Checkout code	2026-03-06T05:30:04.7486602Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
Deploy Application	Checkout code	2026-03-06T05:30:04.7524555Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
Deploy Application	Checkout code	2026-03-06T05:30:04.7696597Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
Deploy Application	Checkout code	2026-03-06T05:30:04.7718808Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
Deploy Application	Checkout code	2026-03-06T05:30:05.1868602Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
Deploy Application	Checkout code	2026-03-06T05:30:05.1870199Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
Deploy Application	Checkout code	2026-03-06T05:30:05.1871124Z [command]/usr/bin/git config --local http.https://github.com/.extraheader AUTHORIZATION: basic ***
Deploy Application	Checkout code	2026-03-06T05:30:05.1871927Z ##[endgroup]
Deploy Application	Checkout code	2026-03-06T05:30:05.1872274Z ##[group]Fetching the repository
Deploy Application	Checkout code	2026-03-06T05:30:05.1872929Z [command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +2492c7d27ac02a50f12e2ca7f51bc1d7882b8489:refs/remotes/origin/lab06
Deploy Application	Checkout code	2026-03-06T05:30:05.4238858Z From https://github.com/LocalT0aster/DevOps-Core-S26
Deploy Application	Checkout code	2026-03-06T05:30:05.4240195Z  + a55c6b2...2492c7d 2492c7d27ac02a50f12e2ca7f51bc1d7882b8489 -> origin/lab06  (forced update)
Deploy Application	Checkout code	2026-03-06T05:30:05.4253108Z ##[endgroup]
Deploy Application	Checkout code	2026-03-06T05:30:05.4253515Z ##[group]Determining the checkout info
Deploy Application	Checkout code	2026-03-06T05:30:05.4253862Z ##[endgroup]
Deploy Application	Checkout code	2026-03-06T05:30:05.4254090Z [command]/usr/bin/git sparse-checkout disable
Deploy Application	Checkout code	2026-03-06T05:30:05.4319076Z [command]/usr/bin/git config --local --unset-all extensions.worktreeConfig
Deploy Application	Checkout code	2026-03-06T05:30:05.4355659Z ##[group]Checking out the ref
Deploy Application	Checkout code	2026-03-06T05:30:05.4357258Z [command]/usr/bin/git checkout --progress --force -B lab06 refs/remotes/origin/lab06
Deploy Application	Checkout code	2026-03-06T05:30:05.4395770Z Warning: you are leaving 1 commit behind, not connected to
Deploy Application	Checkout code	2026-03-06T05:30:05.4397071Z any of your branches:
Deploy Application	Checkout code	2026-03-06T05:30:05.4397250Z 
Deploy Application	Checkout code	2026-03-06T05:30:05.4397372Z   a55c6b2 fix: rebuild ansible ci venv on each run
Deploy Application	Checkout code	2026-03-06T05:30:05.4397551Z 
Deploy Application	Checkout code	2026-03-06T05:30:05.4397727Z If you want to keep it by creating a new branch, this may be a good time
Deploy Application	Checkout code	2026-03-06T05:30:05.4398006Z to do so with:
Deploy Application	Checkout code	2026-03-06T05:30:05.4398107Z 
Deploy Application	Checkout code	2026-03-06T05:30:05.4398222Z  git branch <new-branch-name> a55c6b2
Deploy Application	Checkout code	2026-03-06T05:30:05.4398368Z 
Deploy Application	Checkout code	2026-03-06T05:30:05.4401993Z Switched to a new branch 'lab06'
Deploy Application	Checkout code	2026-03-06T05:30:05.4406524Z branch 'lab06' set up to track 'origin/lab06'.
Deploy Application	Checkout code	2026-03-06T05:30:05.4409674Z ##[endgroup]
Deploy Application	Checkout code	2026-03-06T05:30:05.4436197Z [command]/usr/bin/git log -1 --format=%H
Deploy Application	Checkout code	2026-03-06T05:30:05.4451707Z 2492c7d27ac02a50f12e2ca7f51bc1d7882b8489
Deploy Application	Setup Ansible toolchain	﻿2026-03-06T05:30:05.4663275Z Prepare all required actions
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:05.4663720Z Getting action download info
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:05.7487960Z Download action repository 'actions/setup-python@v5' (SHA:a26af69be951a213d495a4c3e4e4022e16d87065)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:09.0415725Z Download action repository 'actions/cache@v4' (SHA:0057852bfaa89a56745cba8c7296529d2fc39830)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5880420Z ##[group]Run ./.github/actions/ansible-setup
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5880698Z with:
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5880863Z   python-version: 3.12
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5881059Z   working-directory: ansible
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5881319Z   python-requirements-path: ansible/requirements-ci.txt
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5881672Z   collection-requirements-path: ansible/requirements.yml
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5881948Z env:
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5882110Z   ANSIBLE_DIRECTORY: ansible
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5882411Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5882818Z   DEPLOY_TAGS: app_deploy
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5883002Z ##[endgroup]
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5991311Z ##[group]Run actions/setup-python@v5
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5991626Z with:
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5991785Z   python-version: 3.12
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5991981Z   check-latest: false
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5992382Z   token: ***
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5992626Z   update-environment: true
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5992839Z   allow-prereleases: false
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5993026Z   freethreaded: false
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5993367Z env:
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5993524Z   ANSIBLE_DIRECTORY: ansible
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5993726Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5993962Z   DEPLOY_TAGS: app_deploy
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.5994142Z ##[endgroup]
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7393979Z ##[group]Installed versions
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7434733Z Successfully set up CPython (3.12.13)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7436487Z ##[endgroup]
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7957480Z ##[group]Run actions/cache@v4
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7957724Z with:
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7957975Z   path: ~/.cache/pip
Deploy Application	Setup Ansible toolchain	~/.ansible/collections
Deploy Application	Setup Ansible toolchain	
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7958375Z   key: Linux-py3.12-ansible-70fee6f2b98d7def1a2c43ddbf364d7b6b2648821ca185e0955c8d98e4cb9364
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7958770Z   restore-keys: Linux-py3.12-ansible-
Deploy Application	Setup Ansible toolchain	
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7959012Z   enableCrossOsArchive: false
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7959210Z   fail-on-cache-miss: false
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7959399Z   lookup-only: false
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7959567Z   save-always: false
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7959726Z env:
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7959881Z   ANSIBLE_DIRECTORY: ansible
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7960079Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7960298Z   DEPLOY_TAGS: app_deploy
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7960561Z   pythonLocation: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7960944Z   PKG_CONFIG_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib/pkgconfig
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7961317Z   Python_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7961663Z   Python2_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7962001Z   Python3_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7962559Z   LD_LIBRARY_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:13.7963084Z ##[endgroup]
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:14.4043248Z Cache hit for: Linux-py3.12-ansible-70fee6f2b98d7def1a2c43ddbf364d7b6b2648821ca185e0955c8d98e4cb9364
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:16.4773003Z Received 0 of 16876233 (0.0%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:17.4766920Z Received 0 of 16876233 (0.0%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:18.4769115Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:19.4773453Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:20.4771646Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:21.4765071Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:22.4774139Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:23.4776252Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:24.4785122Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:25.4782607Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:26.4783331Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:27.4786680Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:28.4791776Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:29.4805527Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:30.4799815Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:31.4800143Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:32.4799538Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:33.4800713Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:34.4799954Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:35.4798905Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:36.4805551Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:37.4820057Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:38.4819188Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:39.4827866Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:40.4828823Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:41.4833593Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:42.4832544Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:43.4837095Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:44.4843083Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:45.4846837Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:46.4855272Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:47.4858765Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:48.4860108Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:49.4862180Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:50.4867065Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:51.4866433Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:52.4864504Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:53.4860951Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:54.4862233Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:55.4862078Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:56.4862231Z Received 99017 of 16876233 (0.6%), 0.0 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:57.4862363Z Received 4293321 of 16876233 (25.4%), 0.1 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:58.4866137Z Received 4293321 of 16876233 (25.4%), 0.1 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:30:59.4877504Z Received 8487625 of 16876233 (50.3%), 0.2 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:00.4885835Z Received 8487625 of 16876233 (50.3%), 0.2 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:01.4890920Z Received 8487625 of 16876233 (50.3%), 0.2 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:02.4895700Z Received 8487625 of 16876233 (50.3%), 0.2 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:03.4901206Z Received 8487625 of 16876233 (50.3%), 0.2 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3205436Z Received 16876233 of 16876233 (100.0%), 0.3 MBs/sec
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3206066Z Cache Size: ~16 MB (16876233 B)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3225913Z [command]/usr/bin/tar -xf /opt/actions-runner/_work/_temp/2ef53ebd-2583-4392-acbe-fba664f93a07/cache.tzst -P -C /opt/actions-runner/_work/DevOps-Core-S26/DevOps-Core-S26 --use-compress-program unzstd
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3692804Z Cache restored successfully
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3761111Z Cache restored from key: Linux-py3.12-ansible-70fee6f2b98d7def1a2c43ddbf364d7b6b2648821ca185e0955c8d98e4cb9364
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3836550Z ##[group]Run set -euo pipefail
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3836883Z [36;1mset -euo pipefail[0m
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3837088Z [36;1mrm -rf "ansible/.venv-ci"[0m
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3837324Z [36;1mpython -m venv "ansible/.venv-ci"[0m
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3837570Z [36;1m. "ansible/.venv-ci/bin/activate"[0m
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3837812Z [36;1mpython -m pip install --upgrade pip[0m
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3838110Z [36;1mpython -m pip install -r "ansible/requirements-ci.txt"[0m
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3850274Z shell: /usr/bin/bash --noprofile --norc -e -o pipefail {0}
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3850741Z env:
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3850906Z   ANSIBLE_DIRECTORY: ansible
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3851125Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3851360Z   DEPLOY_TAGS: app_deploy
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3851632Z   pythonLocation: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3852014Z   PKG_CONFIG_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib/pkgconfig
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3852397Z   Python_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3852748Z   Python2_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3853097Z   Python3_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3853450Z   LD_LIBRARY_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:04.3853731Z ##[endgroup]
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:06.5334681Z Requirement already satisfied: pip in ./ansible/.venv-ci/lib/python3.12/site-packages (25.0.1)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:13.9460353Z Collecting pip
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:13.9471527Z   Using cached pip-26.0.1-py3-none-any.whl.metadata (4.7 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:13.9495739Z Using cached pip-26.0.1-py3-none-any.whl (1.8 MB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:13.9631733Z Installing collected packages: pip
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:13.9633426Z   Attempting uninstall: pip
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:13.9651606Z     Found existing installation: pip 25.0.1
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:13.9891716Z     Uninstalling pip-25.0.1:
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:13.9931126Z       Successfully uninstalled pip-25.0.1
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:14.6728555Z Successfully installed pip-26.0.1
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:15.2284637Z Collecting ansible-core<2.20,>=2.16 (from -r ansible/requirements-ci.txt (line 1))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:15.2295418Z   Using cached ansible_core-2.19.7-py3-none-any.whl.metadata (7.7 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:15.3078820Z Collecting ansible-lint==26.3.0 (from -r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:15.3088678Z   Using cached ansible_lint-26.3.0-py3-none-any.whl.metadata (6.2 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:15.3781496Z Collecting ansible-compat>=25.8.2 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:15.3790856Z   Using cached ansible_compat-25.12.1-py3-none-any.whl.metadata (3.4 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:15.4707132Z Collecting black>=24.3.0 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:15.4716630Z   Using cached black-26.1.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (88 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:15.6128224Z Collecting cffi>=1.15.1 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:15.6137764Z   Using cached cffi-2.0.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (2.6 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:15.7927015Z Collecting cryptography>=37 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:15.7937012Z   Using cached cryptography-46.0.5-cp311-abi3-manylinux_2_34_x86_64.whl.metadata (5.7 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:15.8671128Z Collecting distro>=1.9.0 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:15.8682256Z   Using cached distro-1.9.0-py3-none-any.whl.metadata (6.8 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:15.9373489Z Collecting filelock>=3.8.2 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:15.9386611Z   Using cached filelock-3.25.0-py3-none-any.whl.metadata (2.0 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.0109744Z Collecting jsonschema>=4.10.0 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.0120324Z   Using cached jsonschema-4.26.0-py3-none-any.whl.metadata (7.6 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.0792137Z Collecting packaging>=22.0 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.0801561Z   Using cached packaging-26.0-py3-none-any.whl.metadata (3.3 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.1437771Z Collecting pathspec<1.1.0,>=1.0.3 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.1452500Z   Using cached pathspec-1.0.4-py3-none-any.whl.metadata (13 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.2274470Z Collecting pyyaml>=6.0.1 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.2288415Z   Using cached pyyaml-6.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.4 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.2980758Z Collecting referencing>=0.36.2 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.2990421Z   Using cached referencing-0.37.0-py3-none-any.whl.metadata (2.8 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.4413848Z Collecting ruamel-yaml>=0.18.11 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.4431007Z   Using cached ruamel_yaml-0.19.1-py3-none-any.whl.metadata (16 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.5318734Z Collecting ruamel-yaml-clib>=0.2.12 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.5330098Z   Using cached ruamel_yaml_clib-0.2.15-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (3.5 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.5966352Z Collecting subprocess-tee>=0.4.1 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.5975349Z   Using cached subprocess_tee-0.4.2-py3-none-any.whl.metadata (3.3 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.6638567Z Collecting wcmatch>=8.5.0 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.6651187Z   Using cached wcmatch-10.1-py3-none-any.whl.metadata (5.1 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.7312397Z Collecting yamllint>=1.38.0 (from ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.7323026Z   Using cached yamllint-1.38.0-py3-none-any.whl.metadata (4.2 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.7987117Z Collecting jinja2>=3.1.0 (from ansible-core<2.20,>=2.16->-r ansible/requirements-ci.txt (line 1))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.7997263Z   Using cached jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.8639164Z Collecting resolvelib<2.0.0,>=0.5.3 (from ansible-core<2.20,>=2.16->-r ansible/requirements-ci.txt (line 1))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.8651084Z   Using cached resolvelib-1.2.1-py3-none-any.whl.metadata (3.7 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.9362504Z Collecting click>=8.0.0 (from black>=24.3.0->ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:16.9375445Z   Using cached click-8.3.1-py3-none-any.whl.metadata (2.6 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.0012448Z Collecting mypy-extensions>=0.4.3 (from black>=24.3.0->ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.0024237Z   Using cached mypy_extensions-1.1.0-py3-none-any.whl.metadata (1.1 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.0715338Z Collecting platformdirs>=2 (from black>=24.3.0->ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.0726463Z   Using cached platformdirs-4.9.4-py3-none-any.whl.metadata (4.7 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.1416270Z Collecting pytokens>=0.3.0 (from black>=24.3.0->ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.1425142Z   Using cached pytokens-0.4.1-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (3.8 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.2067636Z Collecting pycparser (from cffi>=1.15.1->ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.2082912Z   Using cached pycparser-3.0-py3-none-any.whl.metadata (8.2 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.3010526Z Collecting MarkupSafe>=2.0 (from jinja2>=3.1.0->ansible-core<2.20,>=2.16->-r ansible/requirements-ci.txt (line 1))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.3019786Z   Using cached markupsafe-3.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.7 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.4000818Z Collecting attrs>=22.2.0 (from jsonschema>=4.10.0->ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.4016296Z   Using cached attrs-25.4.0-py3-none-any.whl.metadata (10 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.4695332Z Collecting jsonschema-specifications>=2023.03.6 (from jsonschema>=4.10.0->ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.4707000Z   Using cached jsonschema_specifications-2025.9.1-py3-none-any.whl.metadata (2.9 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.7147396Z Collecting rpds-py>=0.25.0 (from jsonschema>=4.10.0->ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.7156027Z   Using cached rpds_py-0.30.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (4.1 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.7938498Z Collecting typing-extensions>=4.4.0 (from referencing>=0.36.2->ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.7949097Z   Using cached typing_extensions-4.15.0-py3-none-any.whl.metadata (3.3 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8610682Z Collecting bracex>=2.1.1 (from wcmatch>=8.5.0->ansible-lint==26.3.0->-r ansible/requirements-ci.txt (line 2))
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8620246Z   Using cached bracex-2.6-py3-none-any.whl.metadata (3.6 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8657240Z Using cached ansible_lint-26.3.0-py3-none-any.whl (330 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8667064Z Using cached ansible_core-2.19.7-py3-none-any.whl (2.4 MB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8682968Z Using cached pathspec-1.0.4-py3-none-any.whl (55 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8690638Z Using cached resolvelib-1.2.1-py3-none-any.whl (18 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8698234Z Using cached ansible_compat-25.12.1-py3-none-any.whl (27 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8705759Z Using cached black-26.1.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (1.8 MB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8718422Z Using cached cffi-2.0.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (219 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8726345Z Using cached click-8.3.1-py3-none-any.whl (108 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8735000Z Using cached cryptography-46.0.5-cp311-abi3-manylinux_2_34_x86_64.whl (4.5 MB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8755686Z Using cached distro-1.9.0-py3-none-any.whl (20 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8763372Z Using cached filelock-3.25.0-py3-none-any.whl (26 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8770674Z Using cached jinja2-3.1.6-py3-none-any.whl (134 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8778285Z Using cached jsonschema-4.26.0-py3-none-any.whl (90 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8786395Z Using cached attrs-25.4.0-py3-none-any.whl (67 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8793893Z Using cached jsonschema_specifications-2025.9.1-py3-none-any.whl (18 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8801335Z Using cached markupsafe-3.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (22 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8810007Z Using cached mypy_extensions-1.1.0-py3-none-any.whl (5.0 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8818082Z Using cached packaging-26.0-py3-none-any.whl (74 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8827093Z Using cached platformdirs-4.9.4-py3-none-any.whl (21 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8835125Z Using cached pytokens-0.4.1-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (269 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8843675Z Using cached pyyaml-6.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (807 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8853576Z Using cached referencing-0.37.0-py3-none-any.whl (26 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8861708Z Using cached rpds_py-0.30.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (394 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8870267Z Using cached ruamel_yaml-0.19.1-py3-none-any.whl (118 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8879101Z Using cached ruamel_yaml_clib-0.2.15-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (788 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8888596Z Using cached subprocess_tee-0.4.2-py3-none-any.whl (5.2 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8897105Z Using cached typing_extensions-4.15.0-py3-none-any.whl (44 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8905400Z Using cached wcmatch-10.1-py3-none-any.whl (39 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8912148Z Using cached bracex-2.6-py3-none-any.whl (11 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8920436Z Using cached yamllint-1.38.0-py3-none-any.whl (68 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.8929741Z Using cached pycparser-3.0-py3-none-any.whl (48 kB)
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:17.9681888Z Installing collected packages: typing-extensions, subprocess-tee, ruamel-yaml-clib, ruamel-yaml, rpds-py, resolvelib, pyyaml, pytokens, pycparser, platformdirs, pathspec, packaging, mypy-extensions, MarkupSafe, filelock, distro, click, bracex, attrs, yamllint, wcmatch, referencing, jinja2, cffi, black, jsonschema-specifications, cryptography, jsonschema, ansible-core, ansible-compat, ansible-lint
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.4801930Z 
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.4827204Z Successfully installed MarkupSafe-3.0.3 ansible-compat-25.12.1 ansible-core-2.19.7 ansible-lint-26.3.0 attrs-25.4.0 black-26.1.0 bracex-2.6 cffi-2.0.0 click-8.3.1 cryptography-46.0.5 distro-1.9.0 filelock-3.25.0 jinja2-3.1.6 jsonschema-4.26.0 jsonschema-specifications-2025.9.1 mypy-extensions-1.1.0 packaging-26.0 pathspec-1.0.4 platformdirs-4.9.4 pycparser-3.0 pytokens-0.4.1 pyyaml-6.0.3 referencing-0.37.0 resolvelib-1.2.1 rpds-py-0.30.0 ruamel-yaml-0.19.1 ruamel-yaml-clib-0.2.15 subprocess-tee-0.4.2 typing-extensions-4.15.0 wcmatch-10.1 yamllint-1.38.0
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.7108789Z ##[group]Run set -euo pipefail
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.7109088Z [36;1mset -euo pipefail[0m
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.7109301Z [36;1m. "ansible/.venv-ci/bin/activate"[0m
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.7109613Z [36;1mansible-galaxy collection install -r "ansible/requirements.yml"[0m
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.7118701Z shell: /usr/bin/bash --noprofile --norc -e -o pipefail {0}
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.7118978Z env:
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.7119140Z   ANSIBLE_DIRECTORY: ansible
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.7119362Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.7119585Z   DEPLOY_TAGS: app_deploy
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.7119866Z   pythonLocation: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.7120262Z   PKG_CONFIG_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib/pkgconfig
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.7120665Z   Python_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.7121032Z   Python2_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.7121412Z   Python3_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.7121795Z   LD_LIBRARY_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.7122083Z ##[endgroup]
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.8582727Z [WARNING]: Deprecation warnings can be disabled by setting `deprecation_warnings=False` in ansible.cfg.
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.8585490Z [DEPRECATION WARNING]: DEFAULT_MANAGED_STR option. Reason: The `ansible_managed` variable can be set just like any other variable, or a different variable can be used.
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.8586598Z Alternatives: Set the `ansible_managed` variable, or use any custom variable in templates. This feature will be removed from ansible-core version 2.23.
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:20.8587575Z 
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:21.0412152Z Starting galaxy collection install process
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:21.0413773Z Nothing to do. All requested collections are already installed. If you want to reinstall them, consider using `--force`.
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:21.1165007Z ##[group]Run echo "/opt/actions-runner/_work/DevOps-Core-S26/DevOps-Core-S26/ansible/.venv-ci/bin" >> "$GITHUB_PATH"
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:21.1165671Z [36;1mecho "/opt/actions-runner/_work/DevOps-Core-S26/DevOps-Core-S26/ansible/.venv-ci/bin" >> "$GITHUB_PATH"[0m
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:21.1174955Z shell: /usr/bin/bash --noprofile --norc -e -o pipefail {0}
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:21.1175220Z env:
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:21.1175388Z   ANSIBLE_DIRECTORY: ansible
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:21.1175598Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:21.1175823Z   DEPLOY_TAGS: app_deploy
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:21.1176090Z   pythonLocation: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:21.1176475Z   PKG_CONFIG_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib/pkgconfig
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:21.1176862Z   Python_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:21.1177206Z   Python2_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:21.1177576Z   Python3_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:21.1177923Z   LD_LIBRARY_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib
Deploy Application	Setup Ansible toolchain	2026-03-06T05:31:21.1178380Z ##[endgroup]
Deploy Application	Resolve target host from inventory	﻿2026-03-06T05:31:21.1279754Z ##[group]Run set -euo pipefail
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1280229Z [36;1mset -euo pipefail[0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1280543Z [36;1mtarget_host="$([0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1280903Z [36;1m  awk '[0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1281137Z [36;1m    /^[[:space:]]*#/ { next }[0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1281415Z [36;1m    /^\[/ { next }[0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1281695Z [36;1m    NF {[0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1281992Z [36;1m      for (i = 1; i <= NF; i++) {[0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1282367Z [36;1m        if ($i ~ /^ansible_host=/) {[0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1282691Z [36;1m          split($i, value, "=")[0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1283073Z [36;1m          print value[2][0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1283403Z [36;1m          exit[0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1283692Z [36;1m        }[0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1284191Z [36;1m      }[0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1284449Z [36;1m    }[0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1284725Z [36;1m  ' inventory/hosts.ini[0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1285173Z [36;1m)"[0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1285419Z [36;1m[0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1285729Z [36;1mif [ -z "$target_host" ]; then[0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1286258Z [36;1m  echo "Could not determine ansible_host from inventory/hosts.ini" >&2[0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1286775Z [36;1m  exit 1[0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1287030Z [36;1mfi[0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1287277Z [36;1m[0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1287612Z [36;1mecho "TARGET_VM_HOST=$target_host" >> "$GITHUB_ENV"[0m
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1304058Z shell: /usr/bin/bash -e {0}
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1304401Z env:
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1304663Z   ANSIBLE_DIRECTORY: ansible
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1305177Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1305563Z   DEPLOY_TAGS: app_deploy
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1305969Z   pythonLocation: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1306624Z   PKG_CONFIG_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib/pkgconfig
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1307275Z   Python_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1307883Z   Python2_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1308559Z   Python3_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1309167Z   LD_LIBRARY_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib
Deploy Application	Resolve target host from inventory	2026-03-06T05:31:21.1309639Z ##[endgroup]
Deploy Application	Configure SSH access to the target VM	﻿2026-03-06T05:31:21.1398964Z Prepare all required actions
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1425869Z ##[group]Run ./.github/actions/ansible-ssh-setup
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1426139Z with:
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1427741Z   ssh-private-key: ***
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1427946Z   known-host: 192.168.121.50
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1428487Z   ssh-key-path: ~/.ssh/vagrant
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1428672Z env:
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1428876Z   ANSIBLE_DIRECTORY: ansible
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1429141Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1429488Z   DEPLOY_TAGS: app_deploy
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1430020Z   pythonLocation: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1430557Z   PKG_CONFIG_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib/pkgconfig
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1431104Z   Python_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1431573Z   Python2_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1432190Z   Python3_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1432833Z   LD_LIBRARY_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1433368Z   TARGET_VM_HOST: 192.168.121.50
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1433635Z ##[endgroup]
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1450702Z ##[group]Run set -euo pipefail
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1451087Z [36;1mset -euo pipefail[0m
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1451359Z [36;1m[0m
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1451627Z [36;1mkey_path="${SSH_KEY_PATH/#\~/$HOME}"[0m
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1451990Z [36;1m[0m
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1452214Z [36;1minstall -d -m 700 "$HOME/.ssh"[0m
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1452546Z [36;1minstall -d -m 700 "$(dirname "$key_path")"[0m
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1452831Z [36;1mprintf '%s\n' "$SSH_PRIVATE_KEY" > "$key_path"[0m
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1453085Z [36;1mchmod 600 "$key_path"[0m
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1453270Z [36;1m[0m
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1453450Z [36;1mtouch "$HOME/.ssh/known_hosts"[0m
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1453777Z [36;1mchmod 600 "$HOME/.ssh/known_hosts"[0m
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1453991Z [36;1m[0m
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1454160Z [36;1mif [ -n "$KNOWN_HOST" ]; then[0m
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1454476Z [36;1m  ssh-keyscan -H "$KNOWN_HOST" >> "$HOME/.ssh/known_hosts" 2>/dev/null || true[0m
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1454781Z [36;1mfi[0m
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1464672Z shell: /usr/bin/bash --noprofile --norc -e -o pipefail {0}
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1465104Z env:
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1465271Z   ANSIBLE_DIRECTORY: ansible
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1465655Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1465883Z   DEPLOY_TAGS: app_deploy
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1466159Z   pythonLocation: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1466572Z   PKG_CONFIG_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib/pkgconfig
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1466981Z   Python_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1467375Z   Python2_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1467736Z   Python3_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1468184Z   LD_LIBRARY_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1468502Z   TARGET_VM_HOST: 192.168.121.50
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1470330Z   SSH_PRIVATE_KEY: ***
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1470552Z   SSH_KEY_PATH: ~/.ssh/vagrant
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1470761Z   KNOWN_HOST: 192.168.121.50
Deploy Application	Configure SSH access to the target VM	2026-03-06T05:31:21.1470958Z ##[endgroup]
Deploy Application	Prepare vault password file	﻿2026-03-06T05:31:21.3636008Z ##[group]Run set -euo pipefail
Deploy Application	Prepare vault password file	2026-03-06T05:31:21.3636331Z [36;1mset -euo pipefail[0m
Deploy Application	Prepare vault password file	2026-03-06T05:31:21.3636526Z [36;1mumask 077[0m
Deploy Application	Prepare vault password file	2026-03-06T05:31:21.3636742Z [36;1mprintf '%s\n' "$VAULT_PASSWORD" > .vault_pass[0m
Deploy Application	Prepare vault password file	2026-03-06T05:31:21.3647110Z shell: /usr/bin/bash -e {0}
Deploy Application	Prepare vault password file	2026-03-06T05:31:21.3647418Z env:
Deploy Application	Prepare vault password file	2026-03-06T05:31:21.3647583Z   ANSIBLE_DIRECTORY: ansible
Deploy Application	Prepare vault password file	2026-03-06T05:31:21.3647796Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Deploy Application	Prepare vault password file	2026-03-06T05:31:21.3648097Z   DEPLOY_TAGS: app_deploy
Deploy Application	Prepare vault password file	2026-03-06T05:31:21.3648379Z   pythonLocation: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Prepare vault password file	2026-03-06T05:31:21.3648795Z   PKG_CONFIG_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib/pkgconfig
Deploy Application	Prepare vault password file	2026-03-06T05:31:21.3649207Z   Python_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Prepare vault password file	2026-03-06T05:31:21.3649583Z   Python2_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Prepare vault password file	2026-03-06T05:31:21.3650192Z   Python3_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Prepare vault password file	2026-03-06T05:31:21.3650901Z   LD_LIBRARY_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib
Deploy Application	Prepare vault password file	2026-03-06T05:31:21.3651195Z   TARGET_VM_HOST: 192.168.121.50
Deploy Application	Prepare vault password file	2026-03-06T05:31:21.3651681Z   VAULT_PASSWORD: ***
Deploy Application	Prepare vault password file	2026-03-06T05:31:21.3651864Z ##[endgroup]
Deploy Application	Verify target connectivity	﻿2026-03-06T05:31:21.3715635Z ##[group]Run ansible webservers -m ansible.builtin.ping
Deploy Application	Verify target connectivity	2026-03-06T05:31:21.3716023Z [36;1mansible webservers -m ansible.builtin.ping[0m
Deploy Application	Verify target connectivity	2026-03-06T05:31:21.3725398Z shell: /usr/bin/bash -e {0}
Deploy Application	Verify target connectivity	2026-03-06T05:31:21.3725623Z env:
Deploy Application	Verify target connectivity	2026-03-06T05:31:21.3725787Z   ANSIBLE_DIRECTORY: ansible
Deploy Application	Verify target connectivity	2026-03-06T05:31:21.3726022Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Deploy Application	Verify target connectivity	2026-03-06T05:31:21.3726262Z   DEPLOY_TAGS: app_deploy
Deploy Application	Verify target connectivity	2026-03-06T05:31:21.3726550Z   pythonLocation: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Verify target connectivity	2026-03-06T05:31:21.3726964Z   PKG_CONFIG_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib/pkgconfig
Deploy Application	Verify target connectivity	2026-03-06T05:31:21.3727372Z   Python_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Verify target connectivity	2026-03-06T05:31:21.3727847Z   Python2_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Verify target connectivity	2026-03-06T05:31:21.3728334Z   Python3_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Verify target connectivity	2026-03-06T05:31:21.3728701Z   LD_LIBRARY_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib
Deploy Application	Verify target connectivity	2026-03-06T05:31:21.3729032Z   TARGET_VM_HOST: 192.168.121.50
Deploy Application	Verify target connectivity	2026-03-06T05:31:21.3729236Z ##[endgroup]
Deploy Application	Verify target connectivity	2026-03-06T05:31:22.7085708Z vagrant | SUCCESS => {
Deploy Application	Verify target connectivity	2026-03-06T05:31:22.7086542Z     "changed": false,
Deploy Application	Verify target connectivity	2026-03-06T05:31:22.7086737Z     "ping": "pong"
Deploy Application	Verify target connectivity	2026-03-06T05:31:22.7086919Z }
Deploy Application	Deploy web application	﻿2026-03-06T05:31:22.7740839Z Prepare all required actions
Deploy Application	Deploy web application	2026-03-06T05:31:22.7772377Z ##[group]Run ./.github/actions/ansible-deploy
Deploy Application	Deploy web application	2026-03-06T05:31:22.7772622Z with:
Deploy Application	Deploy web application	2026-03-06T05:31:22.7772795Z   ansible-directory: ansible
Deploy Application	Deploy web application	2026-03-06T05:31:22.7773016Z   playbook-path: playbooks/deploy.yml
Deploy Application	Deploy web application	2026-03-06T05:31:22.7773339Z   vault-password: ***
Deploy Application	Deploy web application	2026-03-06T05:31:22.7773529Z   tags: app_deploy
Deploy Application	Deploy web application	2026-03-06T05:31:22.7773717Z   inventory-path: inventory/hosts.ini
Deploy Application	Deploy web application	2026-03-06T05:31:22.7774033Z env:
Deploy Application	Deploy web application	2026-03-06T05:31:22.7774189Z   ANSIBLE_DIRECTORY: ansible
Deploy Application	Deploy web application	2026-03-06T05:31:22.7774391Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Deploy Application	Deploy web application	2026-03-06T05:31:22.7774667Z   DEPLOY_TAGS: app_deploy
Deploy Application	Deploy web application	2026-03-06T05:31:22.7775068Z   pythonLocation: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Deploy web application	2026-03-06T05:31:22.7775475Z   PKG_CONFIG_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib/pkgconfig
Deploy Application	Deploy web application	2026-03-06T05:31:22.7775860Z   Python_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Deploy web application	2026-03-06T05:31:22.7776208Z   Python2_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Deploy web application	2026-03-06T05:31:22.7776600Z   Python3_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Deploy web application	2026-03-06T05:31:22.7776974Z   LD_LIBRARY_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib
Deploy Application	Deploy web application	2026-03-06T05:31:22.7777285Z   TARGET_VM_HOST: 192.168.121.50
Deploy Application	Deploy web application	2026-03-06T05:31:22.7777521Z ##[endgroup]
Deploy Application	Deploy web application	2026-03-06T05:31:22.7789074Z ##[group]Run set -euo pipefail
Deploy Application	Deploy web application	2026-03-06T05:31:22.7789339Z [36;1mset -euo pipefail[0m
Deploy Application	Deploy web application	2026-03-06T05:31:22.7789542Z [36;1mumask 077[0m
Deploy Application	Deploy web application	2026-03-06T05:31:22.7789713Z [36;1m[0m
Deploy Application	Deploy web application	2026-03-06T05:31:22.7789906Z [36;1mlog_path="${RUNNER_TEMP}/ansible-deploy.log"[0m
Deploy Application	Deploy web application	2026-03-06T05:31:22.7790139Z [36;1m[0m
Deploy Application	Deploy web application	2026-03-06T05:31:22.7790294Z [36;1mcleanup() {[0m
Deploy Application	Deploy web application	2026-03-06T05:31:22.7790472Z [36;1m  rm -f .vault_pass[0m
Deploy Application	Deploy web application	2026-03-06T05:31:22.7790651Z [36;1m}[0m
Deploy Application	Deploy web application	2026-03-06T05:31:22.7790808Z [36;1mtrap cleanup EXIT[0m
Deploy Application	Deploy web application	2026-03-06T05:31:22.7790990Z [36;1m[0m
Deploy Application	Deploy web application	2026-03-06T05:31:22.7791180Z [36;1mprintf '%s\n' "$VAULT_PASSWORD" > .vault_pass[0m
Deploy Application	Deploy web application	2026-03-06T05:31:22.7791419Z [36;1m[0m
Deploy Application	Deploy web application	2026-03-06T05:31:22.7791726Z [36;1mansible-playbook "$PLAYBOOK_PATH" -i "$INVENTORY_PATH" --tags "$PLAYBOOK_TAGS" | tee "$log_path"[0m
Deploy Application	Deploy web application	2026-03-06T05:31:22.7792091Z [36;1m[0m
Deploy Application	Deploy web application	2026-03-06T05:31:22.7792278Z [36;1mecho "log-path=$log_path" >> "$GITHUB_OUTPUT"[0m
Deploy Application	Deploy web application	2026-03-06T05:31:22.7802395Z shell: /usr/bin/bash --noprofile --norc -e -o pipefail {0}
Deploy Application	Deploy web application	2026-03-06T05:31:22.7802669Z env:
Deploy Application	Deploy web application	2026-03-06T05:31:22.7802840Z   ANSIBLE_DIRECTORY: ansible
Deploy Application	Deploy web application	2026-03-06T05:31:22.7803059Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Deploy Application	Deploy web application	2026-03-06T05:31:22.7803284Z   DEPLOY_TAGS: app_deploy
Deploy Application	Deploy web application	2026-03-06T05:31:22.7803560Z   pythonLocation: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Deploy web application	2026-03-06T05:31:22.7803946Z   PKG_CONFIG_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib/pkgconfig
Deploy Application	Deploy web application	2026-03-06T05:31:22.7804328Z   Python_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Deploy web application	2026-03-06T05:31:22.7804676Z   Python2_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Deploy web application	2026-03-06T05:31:22.7805109Z   Python3_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Deploy web application	2026-03-06T05:31:22.7805452Z   LD_LIBRARY_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib
Deploy Application	Deploy web application	2026-03-06T05:31:22.7805733Z   TARGET_VM_HOST: 192.168.121.50
Deploy Application	Deploy web application	2026-03-06T05:31:22.7806020Z   VAULT_PASSWORD: ***
Deploy Application	Deploy web application	2026-03-06T05:31:22.7806213Z   PLAYBOOK_PATH: playbooks/deploy.yml
Deploy Application	Deploy web application	2026-03-06T05:31:22.7806433Z   INVENTORY_PATH: inventory/hosts.ini
Deploy Application	Deploy web application	2026-03-06T05:31:22.7806651Z   PLAYBOOK_TAGS: app_deploy
Deploy Application	Deploy web application	2026-03-06T05:31:22.7806832Z ##[endgroup]
Deploy Application	Deploy web application	2026-03-06T05:31:23.1853694Z 
Deploy Application	Deploy web application	2026-03-06T05:31:23.1855725Z PLAY [Deploy application] ******************************************************
Deploy Application	Deploy web application	2026-03-06T05:31:23.1870137Z 
Deploy Application	Deploy web application	2026-03-06T05:31:23.1871854Z TASK [Gathering Facts] *********************************************************
Deploy Application	Deploy web application	2026-03-06T05:31:24.1988353Z ok: [vagrant]
Deploy Application	Deploy web application	2026-03-06T05:31:24.1991083Z 
Deploy Application	Deploy web application	2026-03-06T05:31:24.1991421Z TASK [Run web app role] ********************************************************
Deploy Application	Deploy web application	2026-03-06T05:31:24.2774549Z included: web_app for vagrant
Deploy Application	Deploy web application	2026-03-06T05:31:24.2777912Z 
Deploy Application	Deploy web application	2026-03-06T05:31:24.2778295Z TASK [docker : Load docker role defaults] **************************************
Deploy Application	Deploy web application	2026-03-06T05:31:24.3006960Z ok: [vagrant]
Deploy Application	Deploy web application	2026-03-06T05:31:24.3007239Z 
Deploy Application	Deploy web application	2026-03-06T05:31:24.3007555Z TASK [docker : Install Docker prerequisites] ***********************************
Deploy Application	Deploy web application	2026-03-06T05:31:37.6684351Z ok: [vagrant]
Deploy Application	Deploy web application	2026-03-06T05:31:37.6685233Z 
Deploy Application	Deploy web application	2026-03-06T05:31:37.6685698Z TASK [docker : Ensure Docker keyring directory exists] *************************
Deploy Application	Deploy web application	2026-03-06T05:31:38.0194162Z ok: [vagrant]
Deploy Application	Deploy web application	2026-03-06T05:31:38.0195223Z 
Deploy Application	Deploy web application	2026-03-06T05:31:38.0195503Z TASK [docker : Add Docker GPG key] *********************************************
Deploy Application	Deploy web application	2026-03-06T05:31:38.6477382Z ok: [vagrant]
Deploy Application	Deploy web application	2026-03-06T05:31:38.6478060Z 
Deploy Application	Deploy web application	2026-03-06T05:31:38.6478249Z TASK [docker : Add Docker apt repository] **************************************
Deploy Application	Deploy web application	2026-03-06T05:31:39.0961629Z ok: [vagrant]
Deploy Application	Deploy web application	2026-03-06T05:31:39.0962379Z 
Deploy Application	Deploy web application	2026-03-06T05:31:39.0962593Z TASK [docker : Install Docker engine packages] *********************************
Deploy Application	Deploy web application	2026-03-06T05:31:39.9038774Z ok: [vagrant]
Deploy Application	Deploy web application	2026-03-06T05:31:39.9039596Z 
Deploy Application	Deploy web application	2026-03-06T05:31:39.9039935Z TASK [docker : Install Docker Python SDK package] ******************************
Deploy Application	Deploy web application	2026-03-06T05:31:40.7113465Z ok: [vagrant]
Deploy Application	Deploy web application	2026-03-06T05:31:40.7114301Z 
Deploy Application	Deploy web application	2026-03-06T05:31:40.7114984Z TASK [docker : Mark Docker service as ready] ***********************************
Deploy Application	Deploy web application	2026-03-06T05:31:40.7248008Z ok: [vagrant]
Deploy Application	Deploy web application	2026-03-06T05:31:40.7248187Z 
Deploy Application	Deploy web application	2026-03-06T05:31:40.7248370Z TASK [docker : Ensure Docker service is enabled and running] *******************
Deploy Application	Deploy web application	2026-03-06T05:31:41.2950461Z ok: [vagrant]
Deploy Application	Deploy web application	2026-03-06T05:31:41.2951270Z 
Deploy Application	Deploy web application	2026-03-06T05:31:41.2951998Z TASK [docker : Record Docker installation block completion] ********************
Deploy Application	Deploy web application	2026-03-06T05:31:41.6671862Z ok: [vagrant]
Deploy Application	Deploy web application	2026-03-06T05:31:41.6672474Z 
Deploy Application	Deploy web application	2026-03-06T05:31:41.6672884Z TASK [docker : Add deployment user to docker group] ****************************
Deploy Application	Deploy web application	2026-03-06T05:31:42.1253486Z ok: [vagrant]
Deploy Application	Deploy web application	2026-03-06T05:31:42.1253807Z 
Deploy Application	Deploy web application	2026-03-06T05:31:42.1254165Z TASK [docker : Record Docker configuration block completion] *******************
Deploy Application	Deploy web application	2026-03-06T05:31:42.4014420Z ok: [vagrant]
Deploy Application	Deploy web application	2026-03-06T05:31:42.4015201Z 
Deploy Application	Deploy web application	2026-03-06T05:31:42.4015690Z TASK [web_app : Include web app wipe tasks] ************************************
Deploy Application	Deploy web application	2026-03-06T05:31:42.4227650Z included: /opt/actions-runner/_work/DevOps-Core-S26/DevOps-Core-S26/ansible/roles/web_app/tasks/wipe.yml for vagrant
Deploy Application	Deploy web application	2026-03-06T05:31:42.4229296Z 
Deploy Application	Deploy web application	2026-03-06T05:31:42.4230444Z TASK [web_app : Log in to Docker Hub when credentials are available] ***********
Deploy Application	Deploy web application	2026-03-06T05:31:43.0978245Z ok: [vagrant]
Deploy Application	Deploy web application	2026-03-06T05:31:43.0985222Z 
Deploy Application	Deploy web application	2026-03-06T05:31:43.0986015Z TASK [web_app : Ensure Compose project directory exists] ***********************
Deploy Application	Deploy web application	2026-03-06T05:31:43.3761498Z ok: [vagrant]
Deploy Application	Deploy web application	2026-03-06T05:31:43.3761774Z 
Deploy Application	Deploy web application	2026-03-06T05:31:43.3762026Z TASK [web_app : Check for legacy standalone container] *************************
Deploy Application	Deploy web application	2026-03-06T05:31:44.0326329Z ok: [vagrant]
Deploy Application	Deploy web application	2026-03-06T05:31:44.0326547Z 
Deploy Application	Deploy web application	2026-03-06T05:31:44.0326808Z TASK [web_app : Remove legacy standalone container before Compose migration] ***
Deploy Application	Deploy web application	2026-03-06T05:31:44.0522208Z skipping: [vagrant]
Deploy Application	Deploy web application	2026-03-06T05:31:44.0522462Z 
Deploy Application	Deploy web application	2026-03-06T05:31:44.0522727Z TASK [web_app : Template Docker Compose configuration] *************************
Deploy Application	Deploy web application	2026-03-06T05:31:44.6914512Z ok: [vagrant]
Deploy Application	Deploy web application	2026-03-06T05:31:44.6915400Z 
Deploy Application	Deploy web application	2026-03-06T05:31:44.6915611Z TASK [web_app : Deploy application stack with Docker Compose] ******************
Deploy Application	Deploy web application	2026-03-06T05:31:47.5675136Z ok: [vagrant]
Deploy Application	Deploy web application	2026-03-06T05:31:47.5675772Z 
Deploy Application	Deploy web application	2026-03-06T05:31:47.5675983Z TASK [web_app : Wait for application port] *************************************
Deploy Application	Deploy web application	2026-03-06T05:31:48.8916776Z ok: [vagrant -> localhost]
Deploy Application	Deploy web application	2026-03-06T05:31:48.8917460Z 
Deploy Application	Deploy web application	2026-03-06T05:31:48.8917655Z TASK [web_app : Verify application health endpoint] ****************************
Deploy Application	Deploy web application	2026-03-06T05:31:49.3035774Z ok: [vagrant -> localhost]
Deploy Application	Deploy web application	2026-03-06T05:31:49.3035978Z 
Deploy Application	Deploy web application	2026-03-06T05:31:49.3036114Z PLAY RECAP *********************************************************************
Deploy Application	Deploy web application	2026-03-06T05:31:49.3036827Z vagrant                    : ok=22   changed=0    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0   
Deploy Application	Deploy web application	2026-03-06T05:31:49.3037103Z 
Deploy Application	Upload deployment log	﻿2026-03-06T05:31:49.3876767Z ##[group]Run actions/upload-artifact@v4
Deploy Application	Upload deployment log	2026-03-06T05:31:49.3877027Z with:
Deploy Application	Upload deployment log	2026-03-06T05:31:49.3877263Z   name: ansible-deploy-log
Deploy Application	Upload deployment log	2026-03-06T05:31:49.3877536Z   path: /opt/actions-runner/_work/_temp/ansible-deploy.log
Deploy Application	Upload deployment log	2026-03-06T05:31:49.3878027Z   if-no-files-found: warn
Deploy Application	Upload deployment log	2026-03-06T05:31:49.3878218Z   compression-level: 6
Deploy Application	Upload deployment log	2026-03-06T05:31:49.3878406Z   overwrite: false
Deploy Application	Upload deployment log	2026-03-06T05:31:49.3878581Z   include-hidden-files: false
Deploy Application	Upload deployment log	2026-03-06T05:31:49.3878774Z env:
Deploy Application	Upload deployment log	2026-03-06T05:31:49.3878941Z   ANSIBLE_DIRECTORY: ansible
Deploy Application	Upload deployment log	2026-03-06T05:31:49.3879148Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Deploy Application	Upload deployment log	2026-03-06T05:31:49.3879366Z   DEPLOY_TAGS: app_deploy
Deploy Application	Upload deployment log	2026-03-06T05:31:49.3879620Z   pythonLocation: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Upload deployment log	2026-03-06T05:31:49.3879995Z   PKG_CONFIG_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib/pkgconfig
Deploy Application	Upload deployment log	2026-03-06T05:31:49.3880380Z   Python_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Upload deployment log	2026-03-06T05:31:49.3880717Z   Python2_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Upload deployment log	2026-03-06T05:31:49.3881090Z   Python3_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Upload deployment log	2026-03-06T05:31:49.3881522Z   LD_LIBRARY_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib
Deploy Application	Upload deployment log	2026-03-06T05:31:49.3881932Z   TARGET_VM_HOST: 192.168.121.50
Deploy Application	Upload deployment log	2026-03-06T05:31:49.3882178Z ##[endgroup]
Deploy Application	Upload deployment log	2026-03-06T05:31:49.5697737Z With the provided path, there will be 1 file uploaded
Deploy Application	Upload deployment log	2026-03-06T05:31:49.5700524Z Artifact name is valid!
Deploy Application	Upload deployment log	2026-03-06T05:31:49.5701410Z Root directory input is valid!
Deploy Application	Upload deployment log	2026-03-06T05:31:50.0726944Z Beginning upload of artifact content to blob storage
Deploy Application	Upload deployment log	2026-03-06T05:31:51.2153751Z Uploaded bytes 808
Deploy Application	Upload deployment log	2026-03-06T05:31:51.4759396Z Finished uploading artifact content to blob storage!
Deploy Application	Upload deployment log	2026-03-06T05:31:51.4765601Z SHA256 digest of uploaded artifact zip is f81eaa1099002b69ff9e2cbf817f9266dd7ccfa0569af8cc9456757ad35a79e2
Deploy Application	Upload deployment log	2026-03-06T05:31:51.4766682Z Finalizing artifact upload
Deploy Application	Upload deployment log	2026-03-06T05:31:51.7819447Z Artifact ansible-deploy-log.zip successfully finalized. Artifact ID 5792366004
Deploy Application	Upload deployment log	2026-03-06T05:31:51.7820077Z Artifact ansible-deploy-log has been successfully uploaded! Final size is 808 bytes. Artifact ID is 5792366004
Deploy Application	Upload deployment log	2026-03-06T05:31:51.7825632Z Artifact download URL: https://github.com/LocalT0aster/DevOps-Core-S26/actions/runs/22750506418/artifacts/5792366004
Deploy Application	Verify application health	﻿2026-03-06T05:31:51.7906094Z Prepare all required actions
Deploy Application	Verify application health	2026-03-06T05:31:51.7945544Z ##[group]Run ./.github/actions/http-healthcheck
Deploy Application	Verify application health	2026-03-06T05:31:51.7945786Z with:
Deploy Application	Verify application health	2026-03-06T05:31:51.7946000Z   url: http://192.168.121.50:5000/health
Deploy Application	Verify application health	2026-03-06T05:31:51.7946378Z   retries: 10
Deploy Application	Verify application health	2026-03-06T05:31:51.7946541Z   delay-seconds: 3
Deploy Application	Verify application health	2026-03-06T05:31:51.7946722Z   jq-filter: .status == "healthy"
Deploy Application	Verify application health	2026-03-06T05:31:51.7946918Z env:
Deploy Application	Verify application health	2026-03-06T05:31:51.7947078Z   ANSIBLE_DIRECTORY: ansible
Deploy Application	Verify application health	2026-03-06T05:31:51.7947283Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Deploy Application	Verify application health	2026-03-06T05:31:51.7947503Z   DEPLOY_TAGS: app_deploy
Deploy Application	Verify application health	2026-03-06T05:31:51.7947798Z   pythonLocation: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Verify application health	2026-03-06T05:31:51.7948210Z   PKG_CONFIG_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib/pkgconfig
Deploy Application	Verify application health	2026-03-06T05:31:51.7948588Z   Python_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Verify application health	2026-03-06T05:31:51.7948946Z   Python2_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Verify application health	2026-03-06T05:31:51.7949312Z   Python3_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Verify application health	2026-03-06T05:31:51.7949683Z   LD_LIBRARY_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib
Deploy Application	Verify application health	2026-03-06T05:31:51.7949992Z   TARGET_VM_HOST: 192.168.121.50
Deploy Application	Verify application health	2026-03-06T05:31:51.7950188Z ##[endgroup]
Deploy Application	Verify application health	2026-03-06T05:31:51.7961664Z ##[group]Run set -euo pipefail
Deploy Application	Verify application health	2026-03-06T05:31:51.7961940Z [36;1mset -euo pipefail[0m
Deploy Application	Verify application health	2026-03-06T05:31:51.7962141Z [36;1m[0m
Deploy Application	Verify application health	2026-03-06T05:31:51.7962297Z [36;1mresponse=""[0m
Deploy Application	Verify application health	2026-03-06T05:31:51.7962468Z [36;1m[0m
Deploy Application	Verify application health	2026-03-06T05:31:51.7962651Z [36;1mfor attempt in $(seq 1 "$RETRIES"); do[0m
Deploy Application	Verify application health	2026-03-06T05:31:51.7962922Z [36;1m  if response="$(curl -fsSL "$URL")"; then[0m
Deploy Application	Verify application health	2026-03-06T05:31:51.7963152Z [36;1m    break[0m
Deploy Application	Verify application health	2026-03-06T05:31:51.7963325Z [36;1m  fi[0m
Deploy Application	Verify application health	2026-03-06T05:31:51.7963477Z [36;1m[0m
Deploy Application	Verify application health	2026-03-06T05:31:51.7963665Z [36;1m  if [ "$attempt" -eq "$RETRIES" ]; then[0m
Deploy Application	Verify application health	2026-03-06T05:31:51.7964155Z [36;1m    echo "Health check failed after $RETRIES attempts: $URL" >&2[0m
Deploy Application	Verify application health	2026-03-06T05:31:51.7964541Z [36;1m    exit 1[0m
Deploy Application	Verify application health	2026-03-06T05:31:51.7964803Z [36;1m  fi[0m
Deploy Application	Verify application health	2026-03-06T05:31:51.7965062Z [36;1m[0m
Deploy Application	Verify application health	2026-03-06T05:31:51.7965263Z [36;1m  sleep "$DELAY_SECONDS"[0m
Deploy Application	Verify application health	2026-03-06T05:31:51.7965467Z [36;1mdone[0m
Deploy Application	Verify application health	2026-03-06T05:31:51.7965619Z [36;1m[0m
Deploy Application	Verify application health	2026-03-06T05:31:51.7965778Z [36;1mecho "$response" | jq .[0m
Deploy Application	Verify application health	2026-03-06T05:31:51.7966048Z [36;1mecho "$response" | jq -e "$JQ_FILTER" >/dev/null[0m
Deploy Application	Verify application health	2026-03-06T05:31:51.7975984Z shell: /usr/bin/bash --noprofile --norc -e -o pipefail {0}
Deploy Application	Verify application health	2026-03-06T05:31:51.7976317Z env:
Deploy Application	Verify application health	2026-03-06T05:31:51.7976490Z   ANSIBLE_DIRECTORY: ansible
Deploy Application	Verify application health	2026-03-06T05:31:51.7976706Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Deploy Application	Verify application health	2026-03-06T05:31:51.7977112Z   DEPLOY_TAGS: app_deploy
Deploy Application	Verify application health	2026-03-06T05:31:51.7977471Z   pythonLocation: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Verify application health	2026-03-06T05:31:51.7977899Z   PKG_CONFIG_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib/pkgconfig
Deploy Application	Verify application health	2026-03-06T05:31:51.7978322Z   Python_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Verify application health	2026-03-06T05:31:51.7978707Z   Python2_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Verify application health	2026-03-06T05:31:51.7979071Z   Python3_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Verify application health	2026-03-06T05:31:51.7979436Z   LD_LIBRARY_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib
Deploy Application	Verify application health	2026-03-06T05:31:51.7979733Z   TARGET_VM_HOST: 192.168.121.50
Deploy Application	Verify application health	2026-03-06T05:31:51.7979968Z   URL: http://192.168.121.50:5000/health
Deploy Application	Verify application health	2026-03-06T05:31:51.7980186Z   RETRIES: 10
Deploy Application	Verify application health	2026-03-06T05:31:51.7980346Z   DELAY_SECONDS: 3
Deploy Application	Verify application health	2026-03-06T05:31:51.7980525Z   JQ_FILTER: .status == "healthy"
Deploy Application	Verify application health	2026-03-06T05:31:51.7980725Z ##[endgroup]
Deploy Application	Verify application health	2026-03-06T05:31:51.8117339Z {
Deploy Application	Verify application health	2026-03-06T05:31:51.8118416Z   "status": "healthy",
Deploy Application	Verify application health	2026-03-06T05:31:51.8119624Z   "timestamp": "2026-03-06T05:31:51.856613+00:00",
Deploy Application	Verify application health	2026-03-06T05:31:51.8125582Z   "uptime_seconds": 7603
Deploy Application	Verify application health	2026-03-06T05:31:51.8126569Z }
Deploy Application	Remove vault password file	﻿2026-03-06T05:31:51.8173310Z ##[group]Run rm -f .vault_pass
Deploy Application	Remove vault password file	2026-03-06T05:31:51.8173612Z [36;1mrm -f .vault_pass[0m
Deploy Application	Remove vault password file	2026-03-06T05:31:51.8183658Z shell: /usr/bin/bash -e {0}
Deploy Application	Remove vault password file	2026-03-06T05:31:51.8183890Z env:
Deploy Application	Remove vault password file	2026-03-06T05:31:51.8184060Z   ANSIBLE_DIRECTORY: ansible
Deploy Application	Remove vault password file	2026-03-06T05:31:51.8184297Z   DEPLOY_PLAYBOOK: playbooks/deploy.yml
Deploy Application	Remove vault password file	2026-03-06T05:31:51.8184526Z   DEPLOY_TAGS: app_deploy
Deploy Application	Remove vault password file	2026-03-06T05:31:51.8184815Z   pythonLocation: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Remove vault password file	2026-03-06T05:31:51.8185349Z   PKG_CONFIG_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib/pkgconfig
Deploy Application	Remove vault password file	2026-03-06T05:31:51.8185769Z   Python_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Remove vault password file	2026-03-06T05:31:51.8186221Z   Python2_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Remove vault password file	2026-03-06T05:31:51.8186587Z   Python3_ROOT_DIR: /opt/actions-runner/_work/_tool/Python/3.12.13/x64
Deploy Application	Remove vault password file	2026-03-06T05:31:51.8186969Z   LD_LIBRARY_PATH: /opt/actions-runner/_work/_tool/Python/3.12.13/x64/lib
Deploy Application	Remove vault password file	2026-03-06T05:31:51.8187298Z   TARGET_VM_HOST: 192.168.121.50
Deploy Application	Remove vault password file	2026-03-06T05:31:51.8187521Z ##[endgroup]
Deploy Application	Post Setup Ansible toolchain	﻿2026-03-06T05:31:51.8272725Z Post job cleanup.
Deploy Application	Post Setup Ansible toolchain	2026-03-06T05:31:51.8758473Z Post job cleanup.
Deploy Application	Post Setup Ansible toolchain	2026-03-06T05:31:51.9913680Z Cache hit occurred on the primary key Linux-py3.12-ansible-70fee6f2b98d7def1a2c43ddbf364d7b6b2648821ca185e0955c8d98e4cb9364, not saving cache.
Deploy Application	Post Setup Ansible toolchain	2026-03-06T05:31:51.9977690Z Post job cleanup.
Deploy Application	Post Checkout code	﻿2026-03-06T05:31:52.1550112Z Post job cleanup.
Deploy Application	Post Checkout code	2026-03-06T05:31:52.2320436Z [command]/usr/bin/git version
Deploy Application	Post Checkout code	2026-03-06T05:31:52.2355214Z git version 2.52.0
Deploy Application	Post Checkout code	2026-03-06T05:31:52.2385866Z Temporarily overriding HOME='/opt/actions-runner/_work/_temp/92425419-0a79-44b9-9641-d9e6f2b4f52e' before making global git config changes
Deploy Application	Post Checkout code	2026-03-06T05:31:52.2453359Z Adding repository directory to the temporary git global config as a safe directory
Deploy Application	Post Checkout code	2026-03-06T05:31:52.2456877Z [command]/usr/bin/git config --global --add safe.directory /opt/actions-runner/_work/DevOps-Core-S26/DevOps-Core-S26
Deploy Application	Post Checkout code	2026-03-06T05:31:52.2458061Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
Deploy Application	Post Checkout code	2026-03-06T05:31:52.2475428Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
Deploy Application	Post Checkout code	2026-03-06T05:31:52.2676524Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
Deploy Application	Post Checkout code	2026-03-06T05:31:52.2696268Z http.https://github.com/.extraheader
Deploy Application	Post Checkout code	2026-03-06T05:31:52.2704496Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
Deploy Application	Post Checkout code	2026-03-06T05:31:52.2731261Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
Deploy Application	Post Checkout code	2026-03-06T05:31:52.2879233Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
Deploy Application	Post Checkout code	2026-03-06T05:31:52.2903772Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
Deploy Application	Complete job	﻿2026-03-06T05:31:52.3147748Z Cleaning up orphan processes
```

</details>


### Validation Status

- The local Ansible side is already validated: `ansible-lint` passes, and the playbooks used by the workflow pass syntax checks.
- `vagrant validate` for the isolated runner VM passes.
- The GitHub Actions workflow completed successfully in run `22750506418`.
- The `Ansible Lint` and `Deploy Application` jobs both completed successfully.
- The deploy job resolved the target host from inventory, prepared `.vault_pass`, verified SSH connectivity with `ansible ping`, deployed the playbook, uploaded the deployment log artifact, checked `/health`, and removed `.vault_pass` afterwards.
- Two workflow defects were found and fixed during testing: stale self-hosted runner virtualenv caching and creating `.vault_pass` too late for the connectivity check.
- Pull requests from external forks are intentionally excluded from the secret-backed lint path, because vault decryption requires repository secrets.
- The workflow now has successful GitHub-side evidence, not just local validation.

### Research Answers

1. **What are the security implications of storing SSH keys in GitHub Secrets?**
   - The main benefit is that the key is not committed to the repository, but it is still high-value material. Anyone who can modify a trusted workflow on the default branch can potentially exfiltrate it. The practical controls are branch protection, restricted workflow write access, least-privilege keys, and avoiding self-hosted execution on untrusted pull requests.

2. **How would you implement a staging → production deployment pipeline?**
   - I would split deployment into at least two environments, each with separate inventories, secrets, and GitHub environments. The workflow would deploy automatically to staging, run verification, and only then allow a protected manual approval gate for production.

3. **What would you add to make rollbacks possible?**
   - I would pin image tags to immutable versions instead of `latest`, persist the previously deployed tag, and add a rollback workflow input that redeploys the last known good version. For stronger rollback guarantees, I would also archive the exact Compose template and deployment metadata as workflow artifacts.

4. **How does self-hosted runner improve security compared to GitHub-hosted?**
   - In this lab's setup, the runner stays inside the local private network and can reach the VM directly without exposing SSH to the public internet. That reduces credential sprawl and keeps deployment traffic local. The tradeoff is that a self-hosted runner is persistent, so its trust boundary must be managed more carefully than GitHub-hosted ephemeral runners.

## Task 5: Documentation

This file now serves as the complete lab report for Lab 6.

### Final Status

- Task 1 blocks and tags are implemented and validated.
- Task 2 Docker Compose deployment is implemented, idempotent, and verified on the VM.
- Task 3 wipe logic is implemented and tested across the required scenarios.
- Task 4 GitHub Actions CI/CD is implemented and validated with successful workflow run `22750506418`.
- Supporting raw evidence files collected during the lab include `task1.log`, `task3.log`, and `task4.log`.

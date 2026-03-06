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

```text
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

```text
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

```text
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

```text
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

```text
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

```text
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

```text
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

```text
vagrant@devops-core-s26:~$ docker ps -a
CONTAINER ID   IMAGE                               COMMAND                  CREATED          STATUS          PORTS                                         NAMES
bc1ac63a19d3   localt0aster/devops-app-py:latest   "sh -c 'gunicorn --b…"   13 seconds ago   Up 12 seconds   0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp   devops-app
```

</details>

<details>
<summary><code>docker compose -f /opt/devops-app-py/docker-compose.yml ps</code></summary>

```text
vagrant@devops-core-s26:~$ docker compose -f /opt/devops-app-py/docker-compose.yml ps
NAME         IMAGE                               COMMAND                  SERVICE         CREATED              STATUS              PORTS
devops-app   localt0aster/devops-app-py:latest   "sh -c 'gunicorn --b…"   devops-app-py   About a minute ago   Up About a minute   0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp
```

</details>

<details>
<summary><code>curl -fSsL 127.0.0.1:5000/health | jq</code></summary>

```text
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

## Task 3: Wipe Logic (pending)

## Task 4: CI/CD (pending)

## Task 5: Documentation

This file is the lab documentation and will be extended as the remaining tasks are completed.

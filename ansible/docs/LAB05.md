# LAB05 - Ansible Fundamentals

## 1. Architecture Overview

- Ansible version: `ansible [core 2.20.0]`
- Target VM OS/version: Ubuntu `24.04`
- Project layout:

```text
ansible/
├── inventory/hosts.ini
├── roles/
│   ├── common/
│   │   ├── tasks/common_tasks.yml
│   │   └── defaults/common_defaults.yml
│   ├── docker/
│   │   ├── tasks/docker_tasks.yml
│   │   ├── defaults/docker_defaults.yml
│   │   └── handlers/docker_handlers.yml
│   └── app_deploy/
│       ├── tasks/app_deploy_tasks.yml
│       ├── defaults/app_deploy_defaults.yml
│       └── handlers/app_deploy_handlers.yml
├── playbooks/
│   ├── provision.yml
│   ├── deploy.yml
│   └── site.yml
├── group_vars/all.yml  # encrypted with Ansible Vault
├── ansible.cfg
└── docs/LAB05.md
```

- Why roles instead of monolithic playbooks:
  - Roles isolate concern-specific logic (base OS, Docker, app deploy).
  - Reuse is easier across hosts/projects with role defaults.
  - Testing and maintenance are simpler because responsibilities are separated.
  - `include_role` with `tasks_from/defaults_from/handlers_from` keeps file names descriptive.

## 2. Roles Documentation

### `common`

- Purpose: Baseline host configuration (APT cache, common tools, timezone).
- Key variables:
  - `common_packages`
  - `common_manage_timezone`
  - `common_timezone`
- Handlers: none.
- Dependencies: none.

### `docker`

- Purpose: Install Docker CE from official Docker repository and prepare host for Docker Ansible modules.
- Key variables:
  - `docker_packages`
  - `docker_user`
  - `docker_install_python_sdk`
- Handlers:
  - `restart docker`
- Dependencies:
  - Requires Ubuntu host and internet access.

### `app_deploy`

- Purpose: Authenticate to Docker Hub, pull image, replace container when needed, and verify app health.
- Key variables:
  - `dockerhub_username`
  - `dockerhub_password` (vaulted)
  - `docker_image`, `docker_image_tag`
  - `app_container_name`, `app_port`
- Handlers:
  - `restart app container`
- Dependencies:
  - Docker engine installed/running on target host.

## 3. Idempotency Demonstration

<details>
<summary>First run (`provision.yml`)</summary>
</details>

```
$ ansible-playbook playbooks/provision.yml

PLAY [Provision web servers] ****************************************************************************

TASK [Gathering Facts] **********************************************************************************
ok: [vagrant]

TASK [Run common role tasks/defaults] *******************************************************************
included: common for vagrant

TASK [common : Update apt cache] ************************************************************************
changed: [vagrant]

TASK [common : Install common packages] *****************************************************************
ok: [vagrant]

TASK [common : Set /etc/timezone] ***********************************************************************
ok: [vagrant]

TASK [common : Point /etc/localtime to selected timezone] ***********************************************
ok: [vagrant]

TASK [Run docker role tasks/defaults/handlers] **********************************************************
included: docker for vagrant

TASK [docker : Install Docker prerequisites] ************************************************************
changed: [vagrant]

TASK [docker : Ensure Docker keyring directory exists] **************************************************
ok: [vagrant]

TASK [docker : Add Docker GPG key] **********************************************************************
changed: [vagrant]

TASK [docker : Add Docker apt repository] ***************************************************************
changed: [vagrant]

TASK [docker : Install Docker engine packages] **********************************************************
changed: [vagrant]

TASK [docker : Install Docker Python SDK package] *******************************************************
ok: [vagrant]

TASK [docker : Ensure Docker service is enabled and running] ********************************************
ok: [vagrant]

TASK [docker : Add deployment user to docker group] *****************************************************
changed: [vagrant]

RUNNING HANDLER [docker : restart docker] ***************************************************************
changed: [vagrant]

PLAY RECAP **********************************************************************************************
vagrant                    : ok=16   changed=7    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

<details>
<summary>Second run (`provision.yml`)</summary>

```
$ ansible-playbook playbooks/provision.yml

PLAY [Provision web servers] ***********************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************
ok: [vagrant]

TASK [Run common role tasks/defaults] **************************************************************************************************
included: common for vagrant

TASK [common : Update apt cache] *******************************************************************************************************
ok: [vagrant]

TASK [common : Install common packages] ************************************************************************************************
ok: [vagrant]

TASK [common : Set /etc/timezone] ******************************************************************************************************
ok: [vagrant]

TASK [common : Point /etc/localtime to selected timezone] ******************************************************************************
ok: [vagrant]

TASK [Run docker role tasks/defaults/handlers] *****************************************************************************************
included: docker for vagrant

TASK [docker : Install Docker prerequisites] *******************************************************************************************
ok: [vagrant]

TASK [docker : Ensure Docker keyring directory exists] *********************************************************************************
ok: [vagrant]

TASK [docker : Add Docker GPG key] *****************************************************************************************************
ok: [vagrant]

TASK [docker : Add Docker apt repository] **********************************************************************************************
ok: [vagrant]

TASK [docker : Install Docker engine packages] *****************************************************************************************
ok: [vagrant]

TASK [docker : Install Docker Python SDK package] **************************************************************************************
ok: [vagrant]

TASK [docker : Ensure Docker service is enabled and running] ***************************************************************************
ok: [vagrant]

TASK [docker : Add deployment user to docker group] ************************************************************************************
ok: [vagrant]

PLAY RECAP *****************************************************************************************************************************
vagrant                    : ok=15   changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

</details>

### Analysis

- First run: package/repository/service tasks report `changed`.
- Second run: all `ok` with `changed=0`.
- Idempotency is achieved by declarative module states (`state: present`, `state: started`, etc.).

## 4. Ansible Vault Usage

- Secrets are stored in `group_vars/all.yml`.
- File is encrypted with:

```bash
ansible-vault encrypt group_vars/all.yml
```

- Why Vault matters:
  - Protects credentials in VCS.
  - Prevents accidental secret leakage in plaintext config files.

## 5. Deployment Verification

<details>
<summary>Deploy output</summary>

```
$ ansible-playbook playbooks/deploy.yml

PLAY [Deploy application] *************************************************************************

TASK [Gathering Facts] ****************************************************************************
ok: [vagrant]

TASK [Run app deploy role tasks/defaults/handlers] ************************************************
included: app_deploy for vagrant

TASK [app_deploy : Resolve Docker Hub auth secret] ************************************************
ok: [vagrant]

TASK [app_deploy : Validate required Docker Hub credentials] **************************************
ok: [vagrant] => {
    "changed": false,
    "msg": "All assertions passed"
}

TASK [app_deploy : Log in to Docker Hub] **********************************************************
ok: [vagrant]

TASK [app_deploy : Pull application image] ********************************************************
ok: [vagrant]

TASK [app_deploy : Check whether application container already exists] ****************************
ok: [vagrant]

TASK [app_deploy : Stop existing container before replacement] ************************************
skipping: [vagrant]

TASK [app_deploy : Remove old container before replacement] ***************************************
skipping: [vagrant]

TASK [app_deploy : Run application container] *****************************************************
ok: [vagrant]

TASK [app_deploy : Wait for application port] *****************************************************
ok: [vagrant -> localhost]

TASK [app_deploy : Verify application health endpoint] ********************************************
ok: [vagrant -> localhost]

PLAY RECAP ****************************************************************************************
vagrant                    : ok=10   changed=0    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0
```

</details>


<details>
<summary>Container status</summary>


```
$ ansible webservers -a "docker ps"
vagrant | CHANGED | rc=0 >>
CONTAINER ID   IMAGE                               COMMAND                  CREATED         STATUS         PORTS                    NAMES
6051f50e3f87   localt0aster/devops-app-py:latest   "gunicorn --bind 0.0…"   8 minutes ago   Up 8 minutes   0.0.0.0:5000->5000/tcp   devops-app
```

</details>

### Health checks

```bash
$ curl -fSsL 192.168.121.50:5000/health | jq
{
  "status": "healthy",
  "timestamp": "2026-03-05T20:55:15.731873+00:00",
  "uptime_seconds": 816
}
```

## 6. Key Decisions

- Why use roles instead of plain playbooks?
  - Roles reduce duplication and keep each domain-focused (OS, Docker, app).

- How do roles improve reusability?
  - Defaults/handlers/tasks are reusable by attaching the same role to new host groups.

- What makes a task idempotent?
  - The task declares target state and changes only when current state differs.

- How do handlers improve efficiency?
  - Handlers execute only when notified by changed tasks, so restarts are conditional.

- Why is Ansible Vault necessary?
  - It allows storing sensitive values in the repository without exposing plaintext secrets.

## 7. Challenges

- Initial deploy attempt failed with 404 on `/health`.
- Root cause: container command ran `src.flask_instance:app` (routes not imported there).
- Fix: override container command to `src.main:app`, and run delegated health checks with `become: false` while using inventory host (`ansible_host`).
- After fix, deploy rerun completed with `failed=0` and healthy status.

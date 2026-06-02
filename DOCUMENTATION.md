# Jenkins CI/CD Pipeline — Lab Documentation

**Author:** Tom Simmonds  
**Date:** June 2026  
**Organisation:** Qualitest  

---

## 1. Overview

This document outlines the setup and implementation of a Jenkins CI/CD pipeline
built as part of the DevOps Level 4 Apprenticeship lab programme.

The pipeline demonstrates:
- Jenkins running inside a Docker container on a Windows 11 VM via WSL2
- A scripted Groovy pipeline pulling from GitHub
- A shared library in a separate repository containing reusable pipeline steps
- Automated build, test, and deploy stages for a Python calculator application

**Repositories:**
- Pipeline: https://github.com/tom-simmonds/jenkins-pipeline
- Shared Library: https://github.com/tom-simmonds/jenkins-shared-library

---

## 2. Environment Setup

### Virtual Machine
- OS: Windows 11
- Allocated by Qualitest for DevOps lab purposes
- Managed by CyberArk for privileged access

### WSL2 Installation
WSL2 (Windows Subsystem for Linux) provides a native Linux environment
on Windows, allowing Docker Engine and other Linux tools to run without
a separate VM.

**Command used:**
```powershell
wsl --install
```

**Blockers encountered:**
- Admin rights required — resolved by raising IT support ticket
- Nested virtualisation not enabled on the VM — resolved by IT enabling
  it at the hypervisor level

---

## 3. Docker Setup

### Why Docker Engine over Docker Desktop
Docker Desktop requires a paid commercial licence for organisations over
a certain size. Docker Engine is fully open source and free. Running
Docker Engine natively inside WSL2/Ubuntu is also closer to how Docker
runs in real production environments — Linux, command line, no GUI layer.

### Installation
Docker Engine was installed from Docker's official apt repository rather
than Ubuntu's default repository, which holds an outdated version.

**Key commands:**
```bash
# Add Docker's GPG key for package verification
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg \
--dearmor -o /etc/apt/keyrings/docker.gpg

# Add Docker's official repository
echo "deb [arch=$(dpkg --print-architecture) \
signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io \
docker-buildx-plugin docker-compose-plugin
```

### Custom Dockerfile
The base `jenkins/jenkins:lts` image does not include Python3.
Rather than installing it manually into a running container — which
is not reproducible and would be lost if the container was rebuilt —
a custom Dockerfile was created to bake Python3 into the image.

```dockerfile
FROM jenkins/jenkins:lts
USER root
RUN apt-get update && apt-get install -y python3
USER jenkins
```

**Why switch back to USER jenkins?**  
Running applications as root is a security risk. If Jenkins were
compromised, an attacker would gain root access to the container.
Running as the jenkins user applies the principle of least privilege —
Jenkins only has the permissions it needs, nothing more.

---

## 4. Jenkins Setup

### Why Jenkins in Docker
Running Jenkins as a Docker container rather than installing it directly
on Ubuntu provides:
- **Isolation** — Jenkins is contained, cannot affect the host system
- **Portability** — the same docker run command works on any machine
- **Resilience** — if the container breaks, spin up a new one instantly
- **Clean removal** — docker rm removes Jenkins completely, no leftover files

### Running the Container
```bash
docker run -d \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  --name jenkins \
  jenkins-custom
```

| Flag | Purpose |
|------|---------|
| `-d` | Detached mode — runs in background |
| `-p 8080:8080` | Maps Jenkins UI port to host |
| `-p 50000:50000` | Maps agent communication port |
| `-v jenkins_home:/var/jenkins_home` | Persistent volume for Jenkins data |
| `--name jenkins` | Names container for easy reference |

### Persistent Volume
The `-v jenkins_home:/var/jenkins_home` flag creates a Docker volume.
All Jenkins data — jobs, plugins, credentials, build history — is stored
here. The volume persists independently of the container, meaning Jenkins
configuration survives container restarts and rebuilds.

---

## 5. Pipeline Repository

### Repository Structure

jenkins-pipeline/
├── Jenkinsfile
├── Dockerfile
├── app.py
├── test_app.py
└── README.md

### Application — app.py
A basic Python calculator supporting addition, subtraction,
multiplication, and division. Input validation raises a ValueError
for unsupported operators.

### Test Suite — test_app.py
Tests each arithmetic operation and validates that invalid operators
are correctly rejected. Uses Python's assert statement — if any
assertion fails, the pipeline fails.

### Jenkinsfile
```groovy
@Library('jenkins-shared-library') _

node {
    stage('Checkout') {
        checkout scm
    }

    buildPython()
}
```

`checkout scm` pulls the repository that triggered the pipeline.
`buildPython()` calls the shared library step which runs Build,
Test, and Deploy stages.

### Problems Encountered

**python3 not found (exit code 127)**  
The base Jenkins image does not include Python3. Resolved by creating
a custom Dockerfile with Python3 installed.

**EOFError on python3 app.py**  
The calculator's main() function uses input() to accept user input.
Jenkins pipelines are non-interactive — there is no terminal to
accept input. Resolved by calling calculate() directly in the Build
stage rather than running main():
```bash
python3 -c "from app import calculate; print(calculate(10, 5, '+'))"
```

---

## 6. Shared Library

### What is a Shared Library
A Jenkins shared library is a separate Git repository containing
reusable Groovy functions that any pipeline can import. Rather than
duplicating pipeline logic across multiple Jenkinsfiles, common steps
are extracted into the library and called by name.

This enforces the DRY principle — Don't Repeat Yourself. One place
to maintain, all pipelines benefit from updates automatically.

### Repository Structure

jenkins-shared-library/
├── vars/
│   └── buildPython.groovy
└── README.md

Files in `vars/` become callable pipeline steps. The filename
determines the step name — `buildPython.groovy` is called as
`buildPython()` in any Jenkinsfile that imports the library.

### buildPython.groovy
```groovy
def call() {
    stage('Build') {
        sh 'python3 -c "from app import calculate; print(calculate(10, 5, \'+\'))"'
    }
    stage('Test') {
        sh 'python3 test_app.py'
    }
    stage('Deploy') {
        sh 'echo "Deployment successful - application is ready"'
    }
}
```

The function is named `call()` because Jenkins specifically looks for
this function when a shared library step is invoked. It is the entry
point of the step, equivalent to main() in Python.

### Registering the Library in Jenkins
Manage Jenkins → System → Global Trusted Pipeline Libraries → Add

| Field | Value |
|-------|-------|
| Name | jenkins-shared-library |
| Default version | main |
| SCM | Git |
| Repository URL | https://github.com/ImQthulhu/jenkins-shared-library |

### Before and After

**Before shared library — Jenkinsfile contained all logic:**
```groovy
node {
    stage('Checkout') { checkout scm }
    stage('Build') { sh 'python3 -c "..."' }
    stage('Test') { sh 'python3 test_app.py' }
    stage('Deploy') { sh 'echo "Deployment successful"' }
}
```

**After shared library — Jenkinsfile delegates to library:**
```groovy
@Library('jenkins-shared-library') _

node {
    stage('Checkout') { checkout scm }
    buildPython()
}
```

---

## 7. Pipeline Execution

[Add screenshot of successful build here]  
[Add screenshot of stage view here]  
[Add screenshot of console output here]

### Console Output Summary
Jenkins performs the following on each build:
1. Fetches Jenkinsfile from `jenkins-pipeline` repository
2. Loads `jenkins-shared-library` from separate repository
3. Executes Checkout — clones the pipeline repository
4. Executes Build — runs calculate() and prints result
5. Executes Test — runs full test suite, all tests pass
6. Executes Deploy — confirms deployment

---

## 8. Known Improvements

- **Python3 install** — initially installed manually via docker exec
  before the Dockerfile approach was implemented. Manual installs
  inside containers are not reproducible and should always be avoided
  in favour of baking dependencies into the image.
- **Jenkins master running builds** — builds currently run on the
  Jenkins master node. Best practice is to use separate agent nodes
  for builds, keeping the master free for orchestration only.
- **Deploy stage** — currently echoes a success message. A real
  deployment would push to a staging environment or trigger a
  container deployment.
- **No environment variables** — hardcoded values in the pipeline
  could be replaced with Jenkins environment variables or credentials
  for configurability and security.

---

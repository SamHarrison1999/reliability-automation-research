# Ansible boundary

Ansible is recorded as a possible environment-automation tool, not as a required
runtime dependency of the Phase 2 fit probe. The current playbook is a harmless
local syntax-check scaffold. It does not provision Kubernetes, Docker, a
telemetry backend or a participant environment.

The playbook becomes meaningful only after Phase 3 defines which environment
state must be controlled and which steps belong in the experimental reset
contract. Until then, Kubernetes manifests and the existing runner remain the
authoritative fit-probe deployment boundary.

Validate it with:

```bash
ansible-playbook --syntax-check -i ansible/inventory/local.yml ansible/site.yml
ansible-lint ansible/site.yml
```

The repository validator uses an absolute config-relative inventory path via
`%(here)s`, so it behaves consistently regardless of the caller's working
directory. Ansible syntax and lint execution is authoritative on Linux/CI.
Native Windows controllers are not supported by `ansible-core`; on Windows the
quality validator explicitly skips only Ansible execution and still validates
the playbook YAML and Kubernetes boundaries. This is intentional because
native Windows Ansible can fail while importing POSIX-only modules before it
parses the playbook.

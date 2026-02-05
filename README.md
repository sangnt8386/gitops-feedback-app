# GitOps Feedback App (Modular Monolith)

This repository now contains a Python modular monolith implementation of the
translated Cold Turkey service logic. The code is split into bounded modules
under `src/gitops_feedback_app` with a CLI entrypoint.

## Structure

- `gitops_feedback_app.crypto`: 3DES encryption helper.
- `gitops_feedback_app.ini_file`: INI reader/writer.
- `gitops_feedback_app.service`: core service loop and configuration.
- `gitops_feedback_app.windows_service`: optional Windows service installer.
- `gitops_feedback_app.cli`: CLI runner.

## Running locally

```bash
python -m gitops_feedback_app --settings-path ./ct_settings.ini --hosts-path ./hosts
```

On Windows, omit `--hosts-path` to use the system hosts file by default.

## Dependencies

- `pycryptodome` for `Crypto.Cipher.DES3`.
- `pywin32` for Windows service installation (Windows only).

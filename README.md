## Continuous Integration

GitHub Actions runs the automated test suite on pushes and pull requests
targeting `main` or `master`.

The workflow:
- Checks out the repository.
- Sets up Python 3.12.
- Installs dependencies from `requirements.txt`.
- Runs the complete pytest suite.

A failed test run causes the workflow to fail, providing an early warning
before changes are merged.

## Current Limitations

- Use-case registrations are stored in memory and reset when the application restarts.
- Release audit history uses a local JSONL file rather than a managed database.
- Human approval is not yet connected to authenticated reviewer identities.
- Evaluation uses a small synthetic dataset and a deterministic baseline.
- Deployment policy checks permission; it does not deploy a model or application.
- Request metrics are in-memory and are not shared across multiple application workers.
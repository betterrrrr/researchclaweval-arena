Thanks for the pull request. Please confirm:

- [ ] `bash scripts/check-release.sh` passes locally (or CI did)
- [ ] `scripts/allowlist.txt` updated for any added files
- [ ] No credentials, dataset files, run artifacts, or absolute machine paths
- [ ] `bash -n` / `py_compile` clean for touched shell / python files
- [ ] Contract changes are mirrored in `docs/rules.md` where they touch rules
# Tests

Run every deterministic/local regression:

```bash
python tests/run_all.py
```

Run the optional checks that may invoke installed agent CLIs/models:

```bash
python tests/run_all.py --live
```

The local suite is split by responsibility rather than one large workflow harness:

- `test_discovery_projectdoc.py` - repository discovery and PROJECT.md refresh.
- `test_adapters.py` - native launch plans and external skill/config wiring.
- `test_native_commands.py` - setup/run/doctor/refresh/config repository-write-free behavior.
- `test_reflect.py` - transcript parsing, digesting, and the no-history path.
- `test_gitguard.py` - Claude git guard.
- `test_install_accelerator.py` - explicit install/refresh/tool switching/conflicts.
- `test_embacc_external.py` - external project identity and skills-only core cache.
- `test_embacc_selfupdate.py` - self-update dispatch/error handling.
- `test_embacc_cli.py` - public command surface, dispatch, and wheel bundle when build tools are installed.
- `test_pi_safety.py` - Pi safety extension.

`test_opencode_safety.py` and `test_claude_safety.py` are live-only.

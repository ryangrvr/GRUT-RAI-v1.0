#!/usr/bin/env python3
"""Q2 FROZEN ENTRYPOINT.  One command, no choices.

    python3 q2_run.py --config q2_config.json

Runs, in order: (1) the primary stochastic instrument, (2) the Q2-C1..C10 control battery,
(3) the independent auditor.  Every methodological decision is frozen in the config and in
program/gates/Q2_STOCHASTIC_EXECUTION_PREREG.md; this script accepts no other arguments and
makes no scientific adjudication.  Exit code is the AUDITOR's (0 = AUDIT_OK / AUDIT_WARN,
1 = AUDIT_FAIL), never a verdict about the physics.
"""
import os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))


def main(argv):
    cfg = "q2_config.json"
    if "--config" in argv:
        i = argv.index("--config")
        if i + 1 >= len(argv):
            raise SystemExit("usage: q2_run.py --config <file>")
        cfg = argv[i + 1]
    extra = [a for a in argv[1:] if a not in ("--config", cfg)]
    if extra:
        raise SystemExit(f"q2_run.py takes ONLY --config; refusing unknown args: {extra}\n"
                         "(the design is frozen; nothing here is tunable at run time)")
    cfg_path = cfg if os.path.isabs(cfg) else os.path.join(HERE, cfg)
    if not os.path.exists(cfg_path):
        raise SystemExit(f"config not found: {cfg_path}")

    stages = [("primary instrument", ["q2_stochastic_sy.py", cfg_path]),
              ("control battery",    ["q2_controls.py", cfg_path]),
              ("independent audit",  ["q2_audit.py"])]
    t0 = time.time()
    rc = 0
    for name, cmd in stages:
        print(f"\n=== Q2 STAGE: {name} ===", flush=True)
        r = subprocess.run([sys.executable] + [os.path.join(HERE, cmd[0])] + cmd[1:],
                           cwd=HERE)
        if name == "independent audit":
            rc = r.returncode
        elif r.returncode != 0:
            print(f"[q2-run] stage '{name}' exited {r.returncode}; continuing to the audit "
                  f"so the failure is recorded rather than hidden.")
    print(f"\n[q2-run] all stages finished in {time.time()-t0:.0f}s. "
          f"Auditor exit={rc}. Scientific adjudication is NOT performed by this package.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

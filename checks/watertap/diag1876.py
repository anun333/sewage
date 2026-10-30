#!/usr/bin/env python3
"""diag1876.py - IDAES's numerical diagnostics on the BSM2 electroNP (no bio-P) flowsheet.

  python diag1876.py

watertap-org/watertap#1876. On Intel Windows runners the closing solve ends with its
equations met but dual infeasibility and complementarity large: iterates pressed against
variable bounds. This builds and solves the flowsheet as its main() does (a failed solve is
reported, not raised) and prints IDAES's DiagnosticsToolbox reports on the solution or the
last iterate: variables at or near their bounds, constraints with large residuals, and the
numerical-issues summary. Prints the CPU first.
"""
import platform
import subprocess
import sys


def cpu():
    if sys.platform == "win32":
        return subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Processor).Name"],
                              capture_output=True, text=True).stdout.strip()
    for line in open("/proc/cpuinfo"):
        if line.startswith("model name"):
            return line.split(":", 1)[1].strip()
    return platform.processor()


def main():
    print("cpu:", cpu(), "| platform:", platform.platform(), "| python:", sys.version.split()[0], flush=True)
    import watertap.flowsheets.electroNP.BSM2_electroNP_no_bioP as fs
    from idaes.core.util.model_diagnostics import DiagnosticsToolbox
    m = fs.build_flowsheet(has_electroNP=True)
    fs.set_operating_conditions(m)
    fs.set_scaling(m)
    for mx in m.fs.mixers:
        mx.pressure_equality_constraints[0.0, 2].deactivate()
    m.fs.MX3.pressure_equality_constraints[0.0, 2].deactivate()
    m.fs.MX3.pressure_equality_constraints[0.0, 3].deactivate()
    fs.initialize_system(m, has_electroNP=True)
    for mx in m.fs.mixers:
        mx.pressure_equality_constraints[0.0, 2].deactivate()
    m.fs.MX3.pressure_equality_constraints[0.0, 2].deactivate()
    m.fs.MX3.pressure_equality_constraints[0.0, 3].deactivate()
    try:
        fs.solve(m)
        print("\nCLOSING SOLVE: ok", flush=True)
    except Exception as e:
        print("\nCLOSING SOLVE: %s: %s" % (type(e).__name__, str(e)[:120]), flush=True)
    dt = DiagnosticsToolbox(m)
    print("\n=== variables at or near bounds", flush=True)
    dt.display_variables_near_bounds()
    print("\n=== constraints with large residuals", flush=True)
    dt.display_constraints_with_large_residuals()
    print("\n=== numerical issues", flush=True)
    dt.report_numerical_issues()


if __name__ == "__main__":
    main()

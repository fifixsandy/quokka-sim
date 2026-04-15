#!/usr/bin/env python3
import sys
import quokka_sharp as qk
import argparse
import tempfile
import time
import os
import resource

ERRORS_FILE = "quokka_errors.log"

def simulate_qasm(qasm_path, use_computational_basis=False):
    circuit = qk.encoding.QASMparser(qasm_path, translate_ccx=True)
    cnf = qk.encoding.QASM2CNF(circuit, computational_basis=use_computational_basis)
    cnf.leftProjectAllZero()
    cnf.add_measurement({0: 0})

    with tempfile.NamedTemporaryFile(delete=False, suffix=".cnf") as tmp_cnf:
        cnf.write_to_file(tmp_cnf.name)
        cnf_path = tmp_cnf.name

    start_time = time.perf_counter()
    qk.Simulate(cnf)
    end_time = time.perf_counter()

    usage = resource.getrusage(resource.RUSAGE_SELF)
    peak_mem_kb = usage.ru_maxrss

    os.remove(cnf_path)

    print(f"Time: {end_time - start_time:.6f}\nPeak memory usage: {peak_mem_kb:.2f}")


def main():
    parser = argparse.ArgumentParser(description="Simulate a QASM circuit with Quokka-Sharp.")
    parser.add_argument("qasm_file", help="Path to the input QASM file")
    parser.add_argument("--computational_basis", action="store_true", help="Use computational basis encoding")
    args = parser.parse_args()

    if not os.path.exists(args.qasm_file):
        raise FileNotFoundError(f"File not found: {args.qasm_file}")

    simulate_qasm(args.qasm_file, use_computational_basis=args.computational_basis)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        qasm_file = sys.argv[1] if len(sys.argv) > 1 else "unknown"
        with open(ERRORS_FILE, "a") as err_file:
            err_file.write(f"{qasm_file}: {e}\n")
        print(f"Error occurred: {e}", file=sys.stdout)
        sys.exit(1)
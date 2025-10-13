#!/usr/bin/env python3
import quokka_sharp as qk
import argparse
import tempfile
import time
import os
import resource


def simulate_qasm(qasm_path):

    circuit = qk.encoding.QASMparser(qasm_path, translate_ccx=True)
    cnf = qk.encoding.QASM2CNF(circuit, computational_basis=False)
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
    args = parser.parse_args()

    if not os.path.exists(args.qasm_file):
        raise FileNotFoundError(f"File not found: {args.qasm_file}")

    simulate_qasm(args.qasm_file)


if __name__ == "__main__":
    main()

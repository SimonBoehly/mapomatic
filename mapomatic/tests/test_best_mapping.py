# This code is part of Mapomatic.
#
# (C) Copyright IBM 2022.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
"""Test best mappings"""

import pytest
from qiskit import transpile, QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.test.mock import FakeBelem, FakeQuito, FakeLima

import mapomatic as mm


def test_best_mapping_ghz_state_full_device_multiple_qregs():
    """Test best mappings with multiple registers"""
    qr_a = QuantumRegister(2)
    qr_b = QuantumRegister(3)
    qc = QuantumCircuit(qr_a, qr_b)
    qc.h(qr_a[0])
    qc.cx(qr_a[0], qr_a[1])
    qc.cx(qr_a[0], qr_b[0])
    qc.cx(qr_a[0], qr_b[1])
    qc.cx(qr_a[0], qr_b[2])
    qc.measure_all()
    trans_qc = transpile(qc, FakeLima(), seed_transpiler=102442)
    backends = [FakeBelem(), FakeQuito(), FakeLima()]
    res = mm.best_overall_layout(trans_qc, backends, successors=True)
    expected_res = [
        ([0, 1, 2, 3, 4], 'fake_lima', 0.324),
        ([0, 1, 2, 3, 4], 'fake_belem', 0.335),
        ([2, 1, 0, 3, 4], 'fake_quito', 0.550)
    ]
    for index, expected in enumerate(expected_res):
        assert res[index][0] == expected[0]
        assert res[index][1] == expected[1]
        assert res[index][2] == pytest.approx(expected[2], 0.01)


def test_best_mapping_ghz_state_deflate_multiple_registers():
    """Test best mappings with multiple registers with deflate"""
    qr_a = QuantumRegister(2)
    qr_b = QuantumRegister(2)
    cr_a = ClassicalRegister(2)
    cr_b = ClassicalRegister(2)
    qc = QuantumCircuit(qr_a, qr_b, cr_a, cr_b)
    qc.h(qr_a[0])
    qc.cx(qr_a[0], qr_a[1])
    qc.cx(qr_a[0], qr_b[0])
    qc.cx(qr_a[0], qr_b[1])
    qc.measure(qr_a, cr_b)
    qc.measure(qr_b, cr_a)
    trans_qc = transpile(qc, FakeLima(), seed_transpiler=102442)
    small_circ = mm.deflate_circuit(trans_qc)
    backends = [FakeBelem(), FakeQuito(), FakeLima()]
    res = mm.best_overall_layout(small_circ, backends, successors=True)
    expected_res = [
        ([3, 1, 0, 2], 'fake_lima', 0.161),
        ([0, 1, 3, 2], 'fake_belem', 0.207),
        ([3, 1, 2, 0], 'fake_quito', 0.350)
    ]
    for index, expected in enumerate(expected_res):
        assert res[index][0] == expected[0]
        assert res[index][1] == expected[1]
        assert res[index][2] == pytest.approx(expected[2], 0.01)

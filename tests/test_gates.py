
import c2qa
import numpy
import qiskit
import random


def count_nonzero(statevector):
    """Re-implement numpy.count_nonzero using numpy.isclose()."""
    nonzero = len(statevector)
    for state in statevector:
        if numpy.isclose(state, 0):
            nonzero -= 1
    
    return nonzero


def create_conditional(num_qumodes: int = 2, num_qubits_per_mode: int = 2):
    qmr = c2qa.QumodeRegister(num_qumodes, num_qubits_per_mode)
    qr = qiskit.QuantumRegister(2)
    circuit = c2qa.CVCircuit(qmr, qr)
    
    for qumode in range(num_qumodes):
        circuit.cv_initialize(0, qmr[qumode])
    
    circuit.initialize([0, 1], qr[1])  # qr[0] will init to zero

    return circuit, qmr, qr


def create_unconditional(num_qumodes: int = 2, num_qubits_per_mode: int = 2):
    qmr = c2qa.QumodeRegister(num_qumodes, num_qubits_per_mode)
    circuit = c2qa.CVCircuit(qmr)
    for qumode in range(num_qumodes):
        circuit.cv_initialize(0, qmr[qumode])

    return circuit, qmr


def execute_circuit(circuit: c2qa.CVCircuit):
    backend = qiskit.Aer.get_backend('statevector_simulator')
    job = qiskit.execute(circuit, backend)
    result = job.result()

    return result


def assert_changed(result, circuit: c2qa.CVCircuit):
    assert result.success
    state = result.get_statevector(circuit)
    print(circuit.draw("text"))
    print(state)

    # TODO - better understand what the state vector results should be
    assert count_nonzero(state) > 1


def assert_unchanged(result, circuit: c2qa.CVCircuit):
    assert result.success
    state = result.get_statevector(circuit)
    print(circuit.draw("text"))
    print(state)

    # TODO - better understand what the state vector results should be
    assert count_nonzero(state) == 1


def test_no_gates():
    circuit, qmr = create_unconditional()
    result = execute_circuit(circuit)
    assert_unchanged(result, circuit)    


def test_beamsplitter_once():
    circuit, qmr = create_unconditional()

    phi = random.random()
    circuit.cv_bs(phi, qmr[0], qmr[1])

    result = execute_circuit(circuit)
    assert_changed(result, circuit)


def test_beamsplitter_twice():
    circuit, qmr = create_unconditional()

    phi = random.random()
    circuit.cv_bs(phi, qmr[0], qmr[1])
    circuit.cv_bs(-phi, qmr[0], qmr[1])

    result = execute_circuit(circuit)
    assert_unchanged(result, circuit)


def test_conditonal_displacement():
    circuit, qmr, qr = create_conditional()

    alpha = random.random()
    beta = random.random()
    circuit.cv_cnd_d(alpha, -beta, qr[0], qmr[0], qmr[1])
    circuit.cv_cnd_d(-alpha, beta, qr[0], qmr[0], qmr[1])

    circuit.cv_cnd_d(alpha, -beta, qr[1], qmr[0], qmr[1])
    circuit.cv_cnd_d(-alpha, beta, qr[1], qmr[0], qmr[1])

    result = execute_circuit(circuit)
    assert_unchanged(result, circuit)


def test_conditonal_squeezing():
    circuit, qmr, qr = create_conditional()

    alpha = random.random()
    beta = random.random()
    circuit.cv_cnd_s(alpha, -beta, qr[0], qmr[0], qmr[1])
    circuit.cv_cnd_s(-alpha, beta, qr[0], qmr[0], qmr[1])

    circuit.cv_cnd_s(alpha, -beta, qr[1], qmr[0], qmr[1])
    circuit.cv_cnd_s(-alpha, beta, qr[1], qmr[0], qmr[1])

    result = execute_circuit(circuit)
    assert_unchanged(result, circuit)


def test_displacement_once():
    circuit, qmr = create_unconditional()

    alpha = random.random()
    circuit.cv_d(alpha, qmr[0])

    result = execute_circuit(circuit)
    assert_changed(result, circuit)


def test_displacement_twice():
    circuit, qmr = create_unconditional()

    alpha = random.random()
    circuit.cv_d(alpha, qmr[0])
    circuit.cv_d(-alpha, qmr[0])

    result = execute_circuit(circuit)
    assert_unchanged(result, circuit)


def test_rotation_once():
    circuit, qmr = create_unconditional()

    phi = random.random()
    circuit.cv_r(phi, qmr[0])

    result = execute_circuit(circuit)
    assert_changed(result, circuit)


def test_rotation_twice():
    circuit, qmr = create_unconditional()

    phi = random.random()
    circuit.cv_r(phi, qmr[0])
    circuit.cv_r(-phi, qmr[0])

    result = execute_circuit(circuit)
    assert_unchanged(result, circuit)


def test_squeezing_once():
    circuit, qmr = create_unconditional()

    z = random.random()
    circuit.cv_s(z, qmr[0])

    result = execute_circuit(circuit)
    assert_changed(result, circuit)


def test_squeezing_twice():
    circuit, qmr = create_unconditional()

    z = random.random()
    circuit.cv_s(z, qmr[0])
    circuit.cv_s(-z, qmr[0])

    result = execute_circuit(circuit)
    assert_unchanged(result, circuit)


def test_two_mode_squeezing_once():
    circuit, qmr = create_unconditional()

    z = random.random()
    circuit.cv_s2(z, qmr[0], qmr[1])

    result = execute_circuit(circuit)
    assert_changed(result, circuit)


def test_two_mode_squeezing_twice():
    circuit, qmr = create_unconditional()

    z = random.random()
    circuit.cv_s2(z, qmr[0], qmr[1])
    circuit.cv_s2(-z, qmr[0], qmr[1])

    result = execute_circuit(circuit)
    assert_unchanged(result, circuit)


def test_gates():
    """ Verify that we can use the gates, not that they are actually working. """

    # ===== Constants =====

    n_qubits_per_mode = 3
    n_qumodes = 2
    n_qubits = 3
    n_cbits = 6

    alpha = 1
    beta = -1
    phi = numpy.pi/2
    z_a = 1
    z_b = -1

    circuit, qmr, qr = create_conditional()

    # Basic Gaussian Operations on a Resonator
    circuit.cv_bs(phi, qmr[0], qmr[1])
    circuit.cv_d(alpha, qmr[0])
    circuit.cv_r(phi, qmr[0])
    circuit.cv_s(z_a, qmr[0])
    circuit.cv_s2(z_a, qmr[0], qmr[1])

    # Hybrid qubit-cavity gates
    circuit.cv_cnd_d(alpha, beta, qr[0], qmr[0], qmr[1])
    circuit.cv_cnd_s(z_a, z_b, qr[0], qmr[0], qmr[1])

    result = execute_circuit(circuit)

    assert result.success

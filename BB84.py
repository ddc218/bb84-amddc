from utilities import *

class QuantumChannel:

    # Initializer for new objects
    def __init__(self):
        pass

    # send: Function for Alice to send Bob exclusively a list of qubits. The Alice's list of qubits is added into the Bob's list of qubits under the Bob class variable qubit_list
    """
    self: required to access class data
    sender: String variable that can either be Alice or Bob. If it's Alice the receiver must be Bob and vice versa.
    receiver: String variable that can either be Alice or Bob. If it's Alice the receiver must be Bob and vice versa.
    receiverObj: The variable that represents the class of the Bob.
    msg: A list of qubits. 
    """
    def send(self, sender, receiver, receiverObj, msg):
        if sender == "Alice" and receiver == "Bob":
            receiverObj.setQubitList(msg)

# Creating the Classical Channel Class
class ClassicalChannel:

    # Initializer for new objects
    def __init__(self):
        pass

    # send: Function for Bob to send a basis list to Alice or Alice to send a suitability list to Bob. Both the basis list and suitability list are stored in the respective receiver's class in variables
    """
    self: required to access class data
    sender: String variable that can either be Alice or Bob. If it's Alice the receiver must be Bob and vice versa.
    receiver: String variable that can either be Alice or Bob. If it's Alice the receiver must be Bob and vice versa.
    receiverObj: The variable that represents the receiver's class, either Alice or Bob.
    msg: Can either be a basis list or suitability list. 
    """
    def send(self, sender, receiver, receiverObj, msg):
        if sender == "Bob" and receiver == "Alice":
            receiverObj.setBasisList(msg)
        elif sender == "Alice" and receiver == "Bob":
            receiverObj.setSuitableList(msg)

# Creating Alice's class
class Alice:

    # Initializer for new objects
    def __init__(self):

        # Class variables
        self.generated_qubits = [] # Storage variable for the qubits Alice generates
        self.isSuitableList = [] # Storage variable for the suitability of the _____ that Alice generates
        self.bobsBasisList = [] # Variable to store Bob's basis list that will eventually be sent to her
        self.translatedQubitList = [] # List to store English terms of each of Alice's qubits so that it can appear in chat

    # (helper function) generate_qubit_at_random: Alice creates a new single qubit with the previously defined kets
    """
    self: required to access class data
    """
    def generate_qubit_at_random(self):
        random_number = randint(0,3) # Generates a random of 4 different options
        self.translatedQubitList.append(random_number)

        # First set of brackets: the possible qubit (0(0), 1(1), plus(2), minus(3))
        # Second set of brackets: the chosen qubit as corresponding to the number ID assigned to each possible qubit above
        return [ket0, ket1, ket_plus, ket_minus][random_number]
    
    # generate_n_qubits_at_random: Sets the generated_qubits variable of the class to a list of n qubits by using generate_qubit_at_random n times
    """
    self: required to access class data
    n: number of qubits to be generated
    """
    def generate_n_qubits_at_random(self, n):
        self.generated_qubits = [self.generate_qubit_at_random() for _ in range(n)]
    
    # (helper function) prob_meas: Measures the probability of the given qubit corresponding to the given basis. Returns the probability of measuring in the correct basis
    # The success rate of measuring a qubit depends on the qubit and the basis
    """
    self: required to access class data
    qubit: The qubit that will be compared to the basis. It is a quantum object type.
    basis: A single letter string either "c" or "h" corresponding to the basis (computational & hadamard)
    """
    def prob_meas(self, qubit, basis):
        if basis == "c":
            return abs(bra0 * qubit)**2, abs(bra1 * qubit)**2 # the abs(bra_ * qubit) ** 2 is the formula for probability
        if basis == "h":
            return abs(bra_plus * qubit)**2, abs(bra_minus * qubit)**2# the abs(bra_ * qubit) ** 2 is the formula for probability
        
    # (helper function) basis_checker: Returns True if the qubit is correct, False if otherwise. Return "Unknown basis" as failsafe.
    """
    self: required to access class data
    prob_tupal: Comes from Alice function prob_meas. Two values equaling 1 that determine the probabilty of a qubit corresponding to a basis 
    """
    def basis_checker(self, prob_tupal):
        # prob_a will be the first probability, prob_b will be the second. prob_a + prob_b = 1
        prob_a, prob_b = prob_tupal

        # If the probability of either prob_a or prob_b is 100% (in this case 0.99 since it isn't ever exactly 1), we know that the qubit is correct and return True
        if prob_a > 0.99 and prob_b < 0.99:
            return True
        if prob_a < 0.99 and prob_b > 0.99:
            return True
        
        # If the probability is not a 100% guarantee, we don't know for sure that the qubit is correct and return False
        if 0.5 > prob_a > -0.5 or 0.5 > prob_b > -0.5:
            return False
        
        # Failsafe
        return "Unknown basis."
    
    # isSuitable: Measures the probabilities of the qubits within generated_qubits to the basis within bobsBasisList. Returns a list of probabilities that compare each qubit to each base
    """
    self: required to access class data
    """
    def isSuitable(self):
        correctList = []

        for i in range(len(self.generated_qubits)):
            print(self.bobsBasisList[i])
            correctList.append(self.basis_checker(self.prob_meas(self.generated_qubits[i], self.bobsBasisList[i])))
        
        # Also set the Alice variable isSuitableList to correctList for future use
        self.isSuitableList = correctList
        return correctList
    
    # setBasisList: sets the basisList given to this class' bobsBasisList variable.
    """
    self: required to access class data
    basisList: List of basis generated outside the class
    """
    def setBasisList(self, basisList):
        self.bobsBasisList = basisList


class Bob:
    def __init__(self):
        self.final_key = None
        self.generated_basis = []
        self.qubit_list = []
        self.suitableList = []
        self.measured_qubits = []

    def generate_basis_at_random(self):
        return 'c' if randint(0,1) == 0 else 'h'

    def generate_n_basis(self, n):
        self.generated_basis = [self.generate_basis_at_random() for _ in range(n)]

    def measure_n_qubits(self):
        return [self.quantum_meas(self.prob_meas(self.qubit_list[i], self.generated_basis[i]), self.generated_basis[i])
                for i in range(len(self.qubit_list))]

    def quantum_meas(self, prob_tupal, basis):
        prob_a, prob_b = prob_tupal
        outcome = [ket0, ket1] if basis == "c" else [ket_plus, ket_minus]
        return choices(outcome, weights=[prob_a, prob_b], k=1)[0]

    def prob_meas(self, qubit, basis):
        if basis == "c":
            return abs(bra0 * qubit)**2, abs(bra1 * qubit)**2
        if basis == "h":
            return abs(bra_plus * qubit)**2, abs(bra_minus * qubit)**2

    def map_qubit_to_key(self, qubit):
        if qubit in [ket0, ket_plus]:
            return 0
        elif qubit in [ket1, ket_minus]:
            return 1

    def decryptKey(self):
        keyString = ""
        keptQubits = [self.qubit_list[i] for i in range(len(self.suitableList)) if self.suitableList[i]]
        for qubit in keptQubits:
            keyString += str(self.map_qubit_to_key(qubit))
        return keyString

    def setQubitList(self, qubitList):
        self.qubit_list = qubitList

    def setSuitableList(self, suitableList):
        self.suitableList = suitableList

class BB84:
    def __init__(self):
        self.bobObject = Bob()
        self.aliceObject = Alice()
        self.qcObject = QuantumChannel()
        self.ccObject = ClassicalChannel()


        
from utilities import *
from BB84 import BB84
import base64
# CLASSES

# Creating the Quantum Channel Class


# Not class-specific functions:
cmap = cm.get_cmap('Reds')
colors = [cmap(t) for t in np.linspace(0.3, 0.9, 2)]


def animate_bloch_transition(init_state, final_state):
    """Return initial and final Bloch sphere states as PNG buffers."""
    init_img = render_bloch_state(init_state, colors[0])
    final_img = render_bloch_state(final_state, colors[1])
    return init_img, final_img

# App Stuff
    

    



######################################
## UI/App Begins Here
######################################

# Info needs to persist between button presses


# Sidebar
st.title("BB84 Quantum Key Distribution")
st.sidebar.header("Variable Panel")


sim_mode = st.sidebar.radio("Simulation Mode", ["Manual", "Auto"])



alice_basis_mode = st.sidebar.radio("Alice's Qubit Basis", ["Random", "Computational Only", "Hadamard Only"])
bob_basis_mode = st.sidebar.radio("Bob's Measurement Basis", ["Random", "Computational Only", "Hadamard Only"])



def BB84_round(num_qubits = 1):
    '''
    Simulate one round of BB84. This is where the actual protocol gets run
    '''

    # Initialize System
    experiment = BB84()

    # Alice's Qubit Generation
    if alice_basis_mode == "Random":
        experiment.aliceObject.generate_n_qubits_at_random(num_qubits)
    elif alice_basis_mode == "Computational Only":
        
        for _ in range(num_qubits):

            comp_outcome = randint(0,1)

            if not comp_outcome:
                experiment.aliceObject.generated_qubits.append(ket0)
                experiment.aliceObject.translatedQubitList.append(0)
            else:
                experiment.aliceObject.generated_qubits.append(ket1)
                experiment.aliceObject.translatedQubitList.append(1)

    elif alice_basis_mode == "Hadamard Only":
        for _ in range(num_qubits):

            comp_outcome = randint(0,1)

            if not comp_outcome:
                experiment.aliceObject.generated_qubits.append(ket_plus)
                experiment.aliceObject.translatedQubitList.append(2)
            else:
                experiment.aliceObject.generated_qubits.append(ket_minus)
                experiment.aliceObject.translatedQubitList.append(3)





    experiment.qcObject.send("Alice", "Bob", experiment.bobObject, experiment.aliceObject.generated_qubits)

    # Bob's Basis Generation
    if bob_basis_mode == "Random":
        experiment.bobObject.generate_n_basis(num_qubits)
    elif bob_basis_mode == "Computational Only":
        experiment.bobObject.generated_basis = ['c'] * num_qubits
    elif bob_basis_mode == "Hadamard Only":
        experiment.bobObject.generated_basis = ['h'] * num_qubits




    # Classical Channel Exchange
    experiment.ccObject.send("Bob", "Alice", experiment.aliceObject, experiment.bobObject.generated_basis)
    experiment.aliceObject.isSuitable()
    experiment.ccObject.send("Alice", "Bob", experiment.bobObject, experiment.aliceObject.isSuitableList)

    return experiment



# Messaging
st.subheader("Protocol Log")

bottom_panel = st.empty()

# Create two columns: left for chat, right for Bloch sphere
# List of relative widths
chat_col, bloch_col = st.columns([1.45,1])

# Initialize placeholders
chat_area = chat_col.empty()
bloch_area_before = bloch_col.empty()
bloch_area_after = bloch_col.empty()

# Messaging

# Want message log to persist across user interactions


if "message_log" not in st.session_state:
    st.session_state.message_log = []
    st.session_state.partial_key = ''

if "pp_toggle" not in st.session_state:
    st.session_state.pp_toggle = "play"





# --- Mode Handling and Reset Logic ---

# Initialize previous mode if not present
if "prev_mode" not in st.session_state:
    st.session_state.prev_mode = sim_mode

# Detect mode switch and reset state if changed
if sim_mode != st.session_state.prev_mode:
    st.session_state.prev_mode = sim_mode

    # Clear all session-based protocol state
    keys_to_reset = [
        "message_log", "partial_key", "experiment",
        "current_qubit", "running"
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

    # Optional: also clear UI placeholders
    st.session_state.prev_mode = sim_mode
    st.rerun()


if sim_mode == "Auto":

    # Sidebar controls
    num_qubits = st.sidebar.slider("Number of Qubits", 1, 100, 10)
    speed = st.sidebar.slider("Simulation Speed (rounds/sec)", 0.1, 1.0, 0.5)

    # Initialize persistent state
    if "current_qubit" not in st.session_state:
        st.session_state.current_qubit = 0
    if "running" not in st.session_state:
        st.session_state.running = False
    if "experiment" not in st.session_state:
        st.session_state.experiment = None

    # Play/pause button
    if st.sidebar.button("Play/Pause"):
        st.session_state.running = not st.session_state.running
        # Reset run if toggled to play again after finishing
        if st.session_state.running and st.session_state.current_qubit >= num_qubits:
            st.session_state.current_qubit = 0
            st.session_state.partial_key = ""
            st.session_state.message_log = []
            st.session_state.experiment = None

    # Initialize experiment if not yet created
    if st.session_state.experiment is None:
        st.session_state.experiment = BB84_round(num_qubits=num_qubits)

    experiment = st.session_state.experiment

    # Placeholders for dynamic content
    chat_placeholder = chat_area.container()
    video_placeholder = chat_col.empty()
    bloch_before_placeholder = bloch_area_before.empty()
    bloch_after_placeholder = bloch_area_after.empty()

    # Run the simulation frame-by-frame
    if st.session_state.running and st.session_state.current_qubit < num_qubits:

        i = st.session_state.current_qubit

        # Identify qubit type
        qubit_code = experiment.aliceObject.translatedQubitList[i]
        qubit_labels = {0: "|H⟩", 1: "|V⟩", 2: "|+45⟩", 3: "|−45⟩"}
        qubit_type = qubit_labels.get(qubit_code, "?")

        st.session_state.message_log.append(("Alice", f"sent {qubit_type}"))

        # Bob measures
        basis = experiment.bobObject.generated_basis[i]
        qubit = experiment.bobObject.qubit_list[i]
        measured_qubit = experiment.bobObject.quantum_meas(
            experiment.bobObject.prob_meas(qubit, basis), basis
        )
        experiment.bobObject.measured_qubits.append(measured_qubit)
        basis_str = "Computational (H, V)" if basis == 'c' else "Hadamard (+45, -45)"
        st.session_state.message_log.append(("Bob", f"I measured in the {basis_str} basis."))

        # Bloch spheres
        init_img, final_img = animate_bloch_transition(qubit, measured_qubit)
        bloch_before_placeholder.image(init_img, caption="Bloch Sphere: Before Measurement")
        bloch_after_placeholder.image(final_img, caption="Bloch Sphere: After Measurement")

        # Alice replies
        is_corr = experiment.aliceObject.isSuitableList[i]
        result_msg = "SUITABLE" if is_corr else "INSUITABLE"
        st.session_state.message_log.append(("Alice", f"{result_msg}."))

        # Determine and display video
        video_file = f'{get_filename_label(qubit)}_{get_filename_label(measured_qubit)}_{basis}.mp4'
        with open(video_file, "rb") as f:
            video_bytes = f.read()
            video_base64 = base64.b64encode(video_bytes).decode()

        video_html = f"""
            <video width="100%" autoplay muted playsinline>
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
            </video>
        """
        video_placeholder.markdown(video_html, unsafe_allow_html=True)

        # Update chat
        with chat_placeholder:
            render_chat(st.session_state.message_log)

        # Update partial key
        if is_corr:
            bit = str(experiment.bobObject.map_qubit_to_key(measured_qubit))
            st.session_state.partial_key += bit

        bottom_panel.markdown(f"**Final Key (Binary):** `{st.session_state.partial_key}`")

        # Move to next qubit and rerun after delay
        st.session_state.current_qubit += 1
        time.sleep(1 / speed)
        st.rerun()

    elif st.session_state.current_qubit >= num_qubits:
        st.success("Simulation complete!")
        st.session_state.running = False




# if sim_mode == "Auto":

#     # Sidebar controls
#     num_qubits = st.sidebar.slider("Number of Qubits", 1, 100, 10)
#     speed = st.sidebar.slider("Simulation Speed (rounds/sec)", 0.1, 1.0, 0.5)

#     # Initialize persistent state
#     if "current_qubit" not in st.session_state:
#         st.session_state.current_qubit = 0
#     if "running" not in st.session_state:
#         st.session_state.running = False
#     if "experiment" not in st.session_state:
#         st.session_state.experiment = None

#     # Play/pause button
#     if st.sidebar.button("Play/Pause"):
#         st.session_state.running = not st.session_state.running
#         # Reset run if toggled to play again after finishing
#         if st.session_state.running and st.session_state.current_qubit >= num_qubits:
#             st.session_state.current_qubit = 0
#             st.session_state.partial_key = ""
#             st.session_state.message_log = []
#             st.session_state.experiment = None

#     # Initialize experiment if not yet created
#     if st.session_state.experiment is None:
#         st.session_state.experiment = BB84_round(num_qubits=num_qubits)

#     experiment = st.session_state.experiment

#     # Placeholders for dynamic content
#     chat_placeholder = chat_area.container()
#     video_placeholder = chat_col.empty()
#     bloch_before_placeholder = bloch_area_before.empty()
#     bloch_after_placeholder = bloch_area_after.empty()

#     # Determine which frame to show
#     # (If paused, keep showing the current frame)
#     i = min(st.session_state.current_qubit, num_qubits - 1)

#     # --- Always display current state (even if paused) ---
#     if st.session_state.current_qubit > 0:
#         qubit = experiment.bobObject.qubit_list[i]
#         measured_qubit = (
#             experiment.bobObject.measured_qubits[i]
#             if len(experiment.bobObject.measured_qubits) > i
#             else qubit
#         )

#         basis = experiment.bobObject.generated_basis[i]

#         init_img, final_img = animate_bloch_transition(qubit, measured_qubit)
#         bloch_before_placeholder.image(init_img, caption="Bloch Sphere: Before Measurement")
#         bloch_after_placeholder.image(final_img, caption="Bloch Sphere: After Measurement")

#         # Determine and display video
#         video_file = f'{get_filename_label(qubit)}_{get_filename_label(measured_qubit)}_{basis}.mp4'
#         with open(video_file, "rb") as f:
#             video_bytes = f.read()
#             video_base64 = base64.b64encode(video_bytes).decode()
#         video_html = f"""
#             <video width="100%" autoplay muted playsinline>
#                 <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
#             </video>
#         """
#         video_placeholder.markdown(video_html, unsafe_allow_html=True)

#         # Render chat and key info
#         with chat_placeholder:
#             render_chat(st.session_state.message_log)
#         bottom_panel.markdown(f"**Final Key (Binary):** `{st.session_state.partial_key}`")

#     # --- Advance only if running ---
#     if st.session_state.running and st.session_state.current_qubit < num_qubits:
#         i = st.session_state.current_qubit

#         # Identify qubit type
#         qubit_code = experiment.aliceObject.translatedQubitList[i]
#         qubit_labels = {0: "|H⟩", 1: "|V⟩", 2: "|+45⟩", 3: "|−45⟩"}
#         qubit_type = qubit_labels.get(qubit_code, "?")

#         st.session_state.message_log.append(("Alice", f"sent {qubit_type}"))

#         # Bob measures
#         basis = experiment.bobObject.generated_basis[i]
#         qubit = experiment.bobObject.qubit_list[i]
#         measured_qubit = experiment.bobObject.quantum_meas(
#             experiment.bobObject.prob_meas(qubit, basis), basis
#         )
#         experiment.bobObject.measured_qubits.append(measured_qubit)
#         basis_str = "Computational (H, V)" if basis == 'c' else "Hadamard (+45, -45)"
#         st.session_state.message_log.append(("Bob", f"I measured in the {basis_str} basis."))

#         # Alice replies
#         is_corr = experiment.aliceObject.isSuitableList[i]
#         result_msg = "SUITABLE" if is_corr else "INSUITABLE"
#         st.session_state.message_log.append(("Alice", f"{result_msg}."))

#         # Update partial key
#         if is_corr:
#             bit = str(experiment.bobObject.map_qubit_to_key(measured_qubit))
#             st.session_state.partial_key += bit

#         # Move to next qubit and rerun after delay
#         st.session_state.current_qubit += 1
#         time.sleep(1 / speed)
#         st.rerun()

#     elif st.session_state.current_qubit >= num_qubits:
#         st.success("Simulation complete!")
#         st.session_state.running = False




if sim_mode == "Manual":


    if st.sidebar.button("Step"):
        experiment = BB84_round(num_qubits = 1)

        i = 0 # Only working with one qubit at a time


        if experiment.aliceObject.translatedQubitList[i] == 0:
            qubit_type =  "|H⟩"

        if experiment.aliceObject.translatedQubitList[i] == 1:
            qubit_type =  "|V⟩"
        
        if experiment.aliceObject.translatedQubitList[i] == 2:
            qubit_type =  "|+45⟩"

        if experiment.aliceObject.translatedQubitList[i] == 3:
            qubit_type =  "|−45⟩"

        st.session_state.message_log.append(("Alice", f" sent {qubit_type}"))


        # Bob measures
        #simulate_typing(speed)
        basis = experiment.bobObject.generated_basis[i]
        qubit = experiment.bobObject.qubit_list[i]
        measured_qubit = experiment.bobObject.quantum_meas(
            experiment.bobObject.prob_meas(qubit, basis), basis
        )
        experiment.bobObject.measured_qubits.append(measured_qubit)
        basis_str = "COMPUTATIONAL (H, V)" if basis == 'c' else "HADAMARD (+45, -45)"

        # Update Bloch sphere panel
        init_img, final_img = animate_bloch_transition(qubit, measured_qubit)
        bloch_area_before.image(init_img, caption="Bloch Sphere: Before Measurement")
        bloch_area_after.image(final_img, caption="Bloch Sphere: After Measurement")



        # Bob responds (text only)
        st.session_state.message_log.append(("Bob", f"I measured in the {basis_str} basis."))

        # Alice replies with suitability
        is_corr = experiment.aliceObject.isSuitableList[i]
        result_msg = "SUITABLE" if is_corr else "INSUITABLE"
        st.session_state.message_log.append(("Alice", f"{result_msg}."))

        video_file = f'{get_filename_label(qubit)}_{get_filename_label(measured_qubit)}_{basis}.mp4'
        
        with chat_area.container():

            render_chat(st.session_state.message_log)

            
            with open(video_file, "rb") as f:
                video_bytes = f.read()
                video_base64 = base64.b64encode(video_bytes).decode()

            video_html = f"""
            <video width="100%" autoplay muted playsinline>
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
            Your browser does not support the video tag.
            </video>
            """

            st.markdown(video_html, unsafe_allow_html=True)
            


        bobs_basis_partial = experiment.bobObject.generated_basis[:i+1]
        suitability_partial = experiment.aliceObject.isSuitableList[:i+1]

        # Build binary key from suitable qubits
        partial_key = ''.join([
            str(experiment.bobObject.map_qubit_to_key(experiment.bobObject.measured_qubits[j]))
            for j in range(i+1)
            if experiment.aliceObject.isSuitableList[j]
        ])

        st.session_state.partial_key += partial_key

        bottom_panel.markdown(f"**Binary Key:** `{st.session_state.partial_key}`")

        
    
    if len(st.session_state.message_log) != 0:
        if st.sidebar.button("Clear history"):

            st.session_state.message_log = []
            st.session_state.partial_key = ''

import streamlit as st
import matplotlib.pyplot as plt
import time
import numpy as np
from random import randint, choices
from math import sqrt
from qutip import *
from matplotlib import cm
import io
import streamlit.components.v1 as components
import matplotlib.animation as animation
from matplotlib.patches import Ellipse
import tempfile
from matplotlib.patches import Ellipse, Rectangle



# Defining basis states
ket0 = basis(2,0)
ket1 = basis(2,1)
bra0 = ket0.dag()
bra1 = ket1.dag()


# Defining the Hadamard Gate (H)
H = Qobj(1/sqrt(2) * np.array([[1, 1],
                               [1,-1]]))

# Creating the qubit superpositions (plus and minus)
# kets
ket_plus = H * ket0
ket_minus = H * ket1

#bras
bra_plus = ket_plus.dag()
bra_minus = ket_minus.dag()

def get_filename_label(qubit):
    if qubit == ket0:
        return "ket0"
    elif qubit == ket1:
        return "ket1"
    elif qubit == ket_plus:
        return "ket_plus"
    elif qubit == ket_minus:
        return "ket_minus"
    else:
        raise ValueError("Invalid qubit input")




def animate_quantum_channel(qubit_alice_sent, qubit_bob_measured, basis):

    fontsize = 15
    # Function to assign qubit labels
    def get_label(qubit):
        if qubit == ket0:
            return r'$|H\rangle$'
        elif qubit == ket1:
            return r'$|V\rangle$'
        elif qubit == ket_plus:
            return r'$|+45\rangle$'
        elif qubit == ket_minus:
            return r'$|-45\rangle$'
        else:
            raise ValueError("Invalid qubit input")



    # Assign labels
    label_alice = get_label(qubit_alice_sent)
    label_bob = get_label(qubit_bob_measured)


    if basis == 'h' and qubit_alice_sent in [ket0, ket1]:
        suitable = False

    elif basis == 'c' and qubit_alice_sent in [ket_plus, ket_minus]:
        suitable = False
    else:
        suitable = True
    


    # Plot setup
    fig, ax = plt.subplots(figsize=(6, 4), constrained_layout = True)

    extent_x = 6  # +/- extent_x
    extent_y = 4  # +/- extent_y


    ax.set_xlim(-extent_x, extent_x)
    ax.set_ylim(-extent_y, extent_y)


    ### Draw the landscape

    # PBS
    pbs_width = extent_x * 0.25
    pbs_height = pbs_width

    pbs = Rectangle(xy = (-pbs_width/2, -pbs_height/2), width = pbs_width, height = pbs_height, lw =2, ec = 'k')
    ax.add_patch(pbs)

    plt.plot([-pbs_width/2, pbs_width/2],[-pbs_height/2, pbs_height/2], c = 'k')
    ax.text(0, -pbs_height, r"PBS", ha="center", va="center", fontsize=fontsize)







    #HWP

    hwp_width = extent_x * 0.1
    hwp_height = pbs_height

    hwp = Rectangle(xy = (-extent_x * 0.75, -pbs_height/2), width = hwp_width, height = hwp_height, lw =2, ec = 'k')
    ax.add_patch(hwp)
    

    if basis == "h":
        ax.text(-extent_x * 0.75 + hwp_width/2, -pbs_height, r"HWP($\theta = \pi/8$)", ha="center", va="center", fontsize=fontsize, c = 'm')
    else:
        ax.text(-extent_x * 0.75 + hwp_width/2, -pbs_height, r"HWP($\theta = 0$)", ha="center", va="center", fontsize=fontsize, c = 'm')



    # Right detector:
    x_detector = extent_x * 0.75
    detector_width = pbs_height/3
    detector_height = pbs_height

    right_detector = Ellipse((x_detector, 0), detector_width, detector_height,
                ec='k', facecolor='none', lw=2)
    ax.plot([x_detector, extent_x], [detector_height/2, detector_height/2], lw=2, c='k')
    ax.plot([x_detector, extent_x], [-detector_height/2, -detector_height/2], lw=2, c='k')

    ax.add_patch(right_detector)

    ax.text((x_detector + extent_x)/2, -pbs_height, r"D0", ha="center", va="center", fontsize=fontsize)



    # Top detector:
    y_detector = extent_y * 0.75
    detector_width = pbs_height
    detector_height = pbs_height/3

    top_detector = Ellipse((0, y_detector), detector_width, detector_height,
                ec='k', facecolor='none', lw=2)
    ax.plot([-detector_width/2, -detector_width/2], [y_detector, extent_y], lw=2, c='k')
    ax.plot([detector_width/2, detector_width/2], [y_detector, extent_y], lw=2, c='k')

    ax.add_patch(top_detector)

    ax.text(pbs_width, (y_detector + extent_y)/2, r"D1", ha="center", va="center", fontsize=fontsize)


    # Path lines

    plt.plot([-extent_x, x_detector],[0,0], linestyle = "dotted", c = 'r')
    plt.plot([0,0], [0, y_detector], linestyle = 'dotted', c = 'r')





    # Animation specific stuff

    
    # Step 0: incident on the PBS

    x = np.linspace(-extent_x, 0, 50)
    y = np.zeros(len(x))

    
    

    if suitable:

        if qubit_alice_sent in [ket0, ket_plus]:


    
            #Go right
            rightward_x = np.linspace(0, x_detector, 50)
            rightward_y = np.zeros(len(rightward_x))

            x = np.concatenate((x, rightward_x),)
            y = np.concatenate((y, rightward_y),)
        else:

            # Go up

            upward_y = np.linspace(0, y_detector, 50)
            upward_x = np.zeros(len(upward_y))

            x = np.concatenate((x, upward_x),)
            y = np.concatenate((y, upward_y),)


    else:

        # Bad measurement, go both directions



        #Go right
        rightward_x = np.linspace(0, x_detector, 50)
        rightward_y = np.zeros(len(rightward_x))

        x = np.concatenate((x, rightward_x),)
        y = np.concatenate((y, rightward_y),)


        # Also, go up (using other scatter object)
        x_in = np.array([0] * 50)
        y_in = np.zeros(len(x_in)) 
         

        # Need to buffer front part of particle trajectory

        x_in = np.concatenate((x_in, np.zeros(len(y_in))),)
        y_in = np.concatenate((y_in, np.linspace(0, y_detector, 50)),)

    scatter = ax.scatter(x[0], y[0], c="red", s=50)
    if not suitable:
        insuitable_scatter = ax.scatter(x_in[0], y_in[0], c="red", s=50)


    # Both


    def update(frame):
        if frame < len(x) -1:
            scatter.set_offsets([x[frame], y[frame]])
            
            if not suitable:

                if frame > 49:
                    insuitable_scatter.set_visible(True)
                else:
                    insuitable_scatter.set_visible(False)


                insuitable_scatter.set_offsets([x_in[frame], y_in[frame]])

        else:
            pass
        pass


    # Just in case...
    ax.set_xticks([])
    ax.set_yticks([])

    ax.set_autoscale_on(False)

    ani = animation.FuncAnimation(fig, update, frames=len(x), interval=100)
    




    filename = f'{get_filename_label(qubit_alice_sent)}_{get_filename_label(qubit_bob_measured)}_{basis}.mp4'
    
    ani.save(filename, fps=60, writer='ffmpeg')

    return filename



def render_bloch_state(state, color):
    fig = plt.figure(figsize=(4, 4))

    # EDIT ///////////////////////////////////////////////////////////////////////////////
    b = Bloch(fig=fig)
    b = Bloch(fig=fig)
    b.xlabel = [r'$|+45\rangle$', r'$|-45\rangle$']
    b.ylabel = [r'', r'']
    b.zlabel = [r'$|H\rangle$', r'$|V\rangle$']
    b.vector_color = [color]
    b.add_states([state])
    b.render()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf


def render_chat(message_log, height=300):
    def _escape(s: str):
        return (s.replace("&", "&amp;")
                 .replace("<", "&lt;")
                 .replace(">", "&gt;")
                 .replace("\n", "<br/>"))

    # # last two Alice messages → highlight rules
    # alice_indices = [i for i, (s, _) in enumerate(message_log) if s == "Alice"]
    # highlight_indices = alice_indices[-2:] if len(alice_indices) >= 2 else alice_indices
    # latest_idx = len(message_log) - 1

    html = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <style>
          body {{ margin:0; background-color:#111; font-family: monospace; color:#ddd; }}
          #chat-box {{
            height: {height}px;
            overflow-y: auto;
            padding: 10px;
            box-sizing: border-box;
          }}
          .alice {{ color: #4CAF50; margin:2px 0; }}
          .bob   {{ color: #2196F3; margin:2px 0; }}
          .yellow {{ color: yellow; font-weight: bold; }}
          .red    {{ color: red; font-weight: bold; }}
          .bold   {{ font-weight: bold; }}
          hr {{ border:0; border-top:1px solid #444; margin:8px 0; }}
        </style>
      </head>
      <body>
        <div id="chat-box">
    """
    green, blue, red, white = "#4CAF50", "#2196F3", "#F2330F", "#FFFFFF"

    # Consider batches of 3 messages at a time

    
    

    for triplet_indx in range(int(len(message_log)/3)):
        

    
        suitability_msg = message_log[3*triplet_indx + 2][1]

        for indx in range(3):

            if indx == 2:
                if suitability_msg == "SUITABLE.":
                    color = green
                else:
                    color = red
            else:
                color = white


            sender = message_log[3*triplet_indx + indx][0]
            msg_html = message_log[3*triplet_indx + indx][1]

            

            # Bold the latest entry triplet to the log
            if triplet_indx == int(len(message_log)/3) - 1:
                style = "font-weight:bold;"
                if indx != 2:
                    color = blue

                if not indx:
                    html += f"<div style='color:{color}; margin:2px 0; {style} font-style: italic;'>{f'* {sender} {msg_html} *'}</div>"
                else:
                    html += f"<div style='color:{color}; margin:2px 0; {style} font-style: italic;'>{sender}:{msg_html}</div>"

            else:
                style = "font-weight:normal;"
                if not indx:
                    html += f"<div style='color:{color}; margin:2px 0; {style}'>{f'* {sender} {msg_html} *'}</div>"
                else:
                    html += f"<div style='color:{color}; margin:2px 0; {style}'>{sender}:{msg_html}</div>"

        
        
        partition = "----------------------------------------------------"
        html += f"<div style='color:{blue}; margin:2px 0; {style}'>{partition}</div>"

    # if sender == "Alice" and lower_msg.startswith("Basis was"):
    #         html += "<hr>"

    html += """
        </div>
        <script>
          const chatBox = document.getElementById('chat-box');
          function scrollToBottom() {
            chatBox.scrollTop = chatBox.scrollHeight;
          }
          scrollToBottom();
          const observer = new MutationObserver(scrollToBottom);
          observer.observe(chatBox, { childList: true, subtree: true });
        </script>
      </body>
    </html>
    """

    components.html(html, height=height + 20, scrolling=True)
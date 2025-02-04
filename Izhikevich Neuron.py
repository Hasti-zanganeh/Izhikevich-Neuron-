import os
import sys
import numpy as np
import matplotlib.pyplot as plt

################################################################################
# Plotting and data functions


def plot(s_in, s_out, I_t, v_t, u_t, sim_t, time):
    """
    Plot the neuron system.
    """
    fig = plt.figure(figsize=(10, 15))
    gs = fig.add_gridspec(5, 1)
    in_spikes = fig.add_subplot(gs[0, 0])
    src = fig.add_subplot(gs[1, 0])
    rec = fig.add_subplot(gs[2, 0])
    mp = fig.add_subplot(gs[3, 0])
    out_spikes = fig.add_subplot(gs[4, 0])

    in_spikes.set_title("Input Spikes", fontsize=16)
    in_spikes.set_xlabel("t", fontsize=12)
    in_spikes.set_xlim(1, sim_t)
    in_spikes.eventplot(np.where(s_in > 0)[0], colors="black")

    src.set_title("Synaptic Response Current", fontsize=16)
    src.set_ylabel("I(t)", fontsize=12)
    src.set_xlabel("t", fontsize=12)
    src.set_xlim(1, sim_t)
    src.plot(time, I_t)

    rec.set_title("Izhikevich Neuron Membrane Recovery", fontsize=16)
    rec.set_ylabel("u(t)", fontsize=12)
    rec.set_xlabel("t", fontsize=12)
    rec.set_xlim(1, sim_t)
    rec.plot(time, u_t)

    mp.set_title("Izhikevich Neuron Membrane Potential", fontsize=16)
    mp.set_ylabel("v(t)", fontsize=12)
    mp.set_xlabel("t", fontsize=12)
    mp.set_xlim(1, sim_t)
    mp.set_ylim(-80, 35)
    mp.plot(time, np.clip(v_t, -np.inf, 30.0))

    out_spikes.set_title("Output Spikes", fontsize=16)
    out_spikes.set_xlabel("t", fontsize=12)
    out_spikes.set_xlim(1, sim_t)
    out_spikes.eventplot(np.where(s_out > 0)[0], colors="black")

    fig.tight_layout()
    plt.show()


def to_csv(s_in, s_out, I_t, v_t, u_t, sim_t, time):
    """
    Dump all data to csv format.
    """
    i = 0
    with open('./history.csv', 'w') as outf:
        outf.write('index,time,s_in,I_t,u_t,v_t,s_out\n')
        for t in time:
            outf.write(
                f'{i},{t},{s_in[i]},{I_t[i]},{u_t[i]},{v_t[i]},{s_out[i]}\n')
            i += 1
################################################################################
# Spike functions


def poisson_spiketrains(sim_t_a_size, lam):
    """
    Generate a Poisson spike train.
    """
    pspiketrain = np.random.poisson(lam, size=(sim_t_a_size,))
    pspiketrain[pspiketrain != 0] = 1
    return pspiketrain


def spike_threshold(v, u, c, d, Vth):
    """
    Implement the spike thresholding function for the Izhikevich neuron model.

    See: https://www.izhikevich.org/publications/spikes.pdf
    """
    return v >= Vth


################################################################################
# Neuron Model


def Izh(u, v, dt, I, abcd):
    """
    Izhikevich neuron dynamics equations.

    See: https://www.izhikevich.org/publications/spikes.pdf
    """
    a, b, c, d = abcd
    dv = (0.04 * v ** 2 + 5 * v + 140 - u + I) * dt
    du = (a * (b * v - u)) * dt
    v += dv
    u += du
    return v, u


################################################################################
# Synaptic Response Current Functions


def theta(t, tf):
    """
    Unit step function a.k.a. heaviside step function.
    """
    return 1.0 if t >= tf else 0.0


def src(t, spikes, tau, w, v, E):
    """
    Integrate spikes into the synaptic response current.
    """
    total_current = 0
    for spike_time in spikes:
        delta = t - spike_time
        total_current += w * np.exp(-delta / tau)
    return total_current


################################################################################


def main():
    """
    Main driver function for running the single neuron simulation.
    """
    # Simulation Time in ms
    sim_t = 100
    dt = 1
    sim_t_array = np.arange(1, sim_t+1, dt)
    sim_t_a_size = len(sim_t_array)
    # Lambda for Poisson Spike trains
    lam = 0.1
    # Input and output spiketrains
    s_in = poisson_spiketrains(sim_t_a_size, lam)
    # Neuron History
    v_t = np.zeros(shape=(sim_t_a_size,))
    u_t = np.zeros(shape=(sim_t_a_size,))
    I_t = np.zeros(shape=(sim_t_a_size,))
    s_out = np.zeros(shape=(sim_t_a_size,))
    # Neuron Parameters
    # Izhikevich neuron parameters (a, b, c, d)
    a = 0.02
    b = 0.2
    c = -65
    d = 8
    # Synapse Parameters
    tau = 10  # time constant for synaptic response current
    w = 10  # weight of input synapse
    Vth = 30  # spike threshold for membrane potential
    E = 0  # reversal potential
    # Simulation over time
    for tidx, t in enumerate(sim_t_array):
        # Update synaptic response current
        I_t[tidx] = src(t, np.where(s_in[:tidx+1] > 0)[0], tau, w, v_t[tidx-1], E)
        print(I_t[tidx])
        # Update membrane potential and recovery variable
        v_t[tidx], u_t[tidx] = Izh(u_t[tidx-1], v_t[tidx-1], dt, I_t[tidx], (a, b, c, d))
        # Check for spike threshold
        if spike_threshold(v_t[tidx], u_t[tidx], c, d, Vth):
            s_out[tidx] = 1  # Output spike
            # Reset membrane potential and recovery variable after spike
            v_t[tidx] = c
            u_t[tidx] += d
    # Plot the results
    plot(s_in, s_out, I_t, v_t, u_t, sim_t, sim_t_array)
    # Dump history to history.csv file
    to_csv(s_in, s_out, I_t, v_t, u_t, sim_t, sim_t_array)


################################################################################
if __name__ == "__main__":
    main()
import packet_switching as ps

if __name__ == '__main__':
    sim_duration_hours = 1
    sim_duration_ms = sim_duration_hours * 3600000

    simulation = ps.PacketSwitchingSim(sim_duration_ms)
    # simulation.view_nodes()
    simulation.run_sim()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

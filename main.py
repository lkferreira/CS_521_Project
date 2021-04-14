import packet_switching as ps
import circuit_switching as cs

if __name__ == '__main__':
    # PACKET SWITCHING
    sim_duration_hours = 1
    sim_duration_ms = sim_duration_hours * 3600000

    simulation_ps = ps.PacketSwitchingSim(sim_duration_ms, mean_data_arrival_time=50, transmission_time=80)
    # simulation.view_nodes()
    simulation_ps.run_sim()
    print('\n' + '-'*60)


    # CIRCUIT SWITCHING
    sim_duration_hours = 1
    sim_duration_ms = sim_duration_hours * 3600000

    simulation_cs = cs.CircuitSwitchingSim(sim_duration_ms, mean_data_arrival_time=50, transmission_time=80)
    # simulation_cs.view_nodes()
    simulation_cs.run_sim()

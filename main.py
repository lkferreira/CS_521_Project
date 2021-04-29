import packet_switching as ps
import circuit_switching as cs

MEAN_ARRIVAL_TIME = [10, 25, 50, 75, 100]
TRANSMISSION_TIME = [10, 25, 50, 75, 100]

if __name__ == '__main__':
    for trans in TRANSMISSION_TIME:
        print('\n' + '=' * 60)
        print('TRANSMISSION TIME: ' + str(trans))

        for arr in MEAN_ARRIVAL_TIME:
            print('\n' + '~' * 60)
            print("MEAN ARRIVAL TIME: " + str(arr))

            # PACKET SWITCHING
            sim_duration_hours = 1
            sim_duration_ms = sim_duration_hours * 3600000

            simulation_ps = ps.PacketSwitchingSim(sim_duration_ms, mean_data_arrival_time=arr, transmission_time=trans)
            # simulation.view_nodes()
            simulation_ps.run_sim()
            print('\n' + '-'*60)


            # CIRCUIT SWITCHING
            sim_duration_hours = 1
            sim_duration_ms = sim_duration_hours * 3600000

            simulation_cs = cs.CircuitSwitchingSim(sim_duration_ms, mean_data_arrival_time=arr, transmission_time=trans)
            # simulation_cs.view_nodes()
            simulation_cs.run_sim()

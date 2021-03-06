from heapq import *
import networkx as nx
import matplotlib.pyplot as plt
import collections
import random


class PacketSwitchingSim:

    def __init__(self, duration, mean_data_arrival_time, transmission_time):
        self.duration = duration
        self.complete_data = set()
        self.avg_delay = 0
        self.avg_queue_delay = 0

        self.nodes = nx.Graph()
        self.init_graph()
        self.destination_node = self.nodes.number_of_nodes() - 1
        self.busy_edges = set()

        self.events = []
        self.t = 0
        self.queues = [collections.deque() for _ in range(self.nodes.number_of_nodes())]
        self.mean_data_arrival_time = mean_data_arrival_time
        self.transmission_time = transmission_time
        self.id_counter = 0


    def init_graph(self):
        edges = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3], [2, 4], [2, 5], [3, 5], [4, 5]]
        self.nodes.add_edges_from(edges)

        # GENERATE RANDOM GRAPH
        # n = 25
        # p = 0.2
        # g = nx.erdos_renyi_graph(n, p)
        # while not nx.is_connected(g):
        #     g = nx.erdos_renyi_graph(n, p)
        # self.nodes = g

    def view_nodes(self):
        nx.draw_networkx(self.nodes)
        plt.show()

    def process_new_data_arrival(self, event):
        nodes_copy = self.nodes.copy()
        nodes_copy.remove_node(0)
        shortest_paths = [[0] + nx.shortest_path(nodes_copy, source=neighbor, target=self.destination_node)
                          for neighbor in nx.neighbors(self.nodes, 0)]
        paths = sorted(shortest_paths, key=lambda x: len(x))

        # check if next path is available
        busy_network = True
        for p in paths:
            if not (p[0], p[1]) in self.busy_edges:
                event['path'] = p
                event['curr_trip'] = [0, 1]
                self.process_transmission_start(event)
                busy_network = False
                break

        # store event in queue if no paths are available
        if busy_network:
            event['event_type'] = 'data_ready'
            self.queues[0].append(event)

        # generate new data arrival event
        new_data_arrival_time = self.t + random.uniform(0, self.mean_data_arrival_time * 2)
        heappush(self.events, (new_data_arrival_time, self.id_counter, {'event_type': 'new_data_arrival',
                                                                        'event_start_time': new_data_arrival_time,
                                                                        'event_time': new_data_arrival_time,
                                                                        'path': None,
                                                                        'curr_trip': None,
                                                                        'event_id': self.id_counter,
                                                                        'queue_delay': 0,
                                                                        'total_delay': 0}))
        self.id_counter += 1

    def process_data_ready(self, event, awake=False):
        path = event['path']
        trip_src_idx, trip_dest_idx = event['curr_trip'] if path else [0, 1]

        # check if path is available
        if not path or (path[trip_src_idx], path[trip_dest_idx]) in self.busy_edges:
            # check if next path is available
            src_node = path[trip_src_idx] if path else 0

            nodes_copy = self.nodes.copy()
            deleted_nodes = set(path[0:trip_src_idx+1]) if path else set([src_node])
            nodes_copy.remove_nodes_from(deleted_nodes)
            valid_neighbors = set(nx.neighbors(self.nodes, src_node)).difference(deleted_nodes)
            shortest_paths = []
            for neighbor in valid_neighbors:
                try:
                    shortest_paths.append([src_node] + nx.shortest_path(nodes_copy, source=neighbor, target=self.destination_node))
                except nx.NetworkXNoPath as err:
                    pass
            paths = sorted(shortest_paths, key=lambda x: len(x))

            for p in paths:
                if not (p[0], p[1]) in self.busy_edges:
                    visited = path[0:trip_src_idx] if path else []
                    new_path = visited + p

                    event['path'] = new_path
                    event['curr_trip'] = [trip_src_idx, trip_dest_idx]
                    if awake:
                        event['queue_delay'] += self.t - event['event_time']
                        event['event_time'] = self.t
                    self.process_transmission_start(event)
                    return True

            return False
        else:
            if awake:
                event['queue_delay'] += self.t - event['event_time']
                event['event_time'] = self.t
            self.process_transmission_start(event)
            return True

    def process_transmission_start(self, event):
        path = event['path']
        trip_src_idx, trip_dest_idx = event['curr_trip']
        trip_src_node = path[trip_src_idx]
        trip_dest_node = path[trip_dest_idx]

        # update nodes
        self.busy_edges.add((trip_src_node, trip_dest_node))

        # generate transmission end event
        event['event_type'] = 'transmission_end'
        event['event_time'] = self.t + self.transmission_time
        heappush(self.events, (self.t + self.transmission_time, event['event_id'], event))

    def process_transmission_end(self, event):
        path = event['path']
        trip_src_idx, trip_dest_idx = event['curr_trip']
        trip_src_node = path[trip_src_idx]
        trip_dest_node = path[trip_dest_idx]

        # update nodes
        self.busy_edges.remove((trip_src_node, trip_dest_node))

        # alert data waiting in queue for source node that a new path is free
        if self.queues[trip_src_node]:
            queue_idx = 0
            while queue_idx < len(self.queues[trip_src_node]):
                data_ready = self.queues[trip_src_node][queue_idx]

                if self.process_data_ready(data_ready, awake=True):
                    del self.queues[trip_src_node][queue_idx]
                    break
                queue_idx += 1

        # generate data ready event if not at destination node
        if trip_dest_node != self.destination_node:
            event['curr_trip'] = [trip_dest_idx, trip_dest_idx + 1]

            if not self.process_data_ready(event):
                event['event_type'] = 'data_ready'
                self.queues[trip_dest_node].append(event)
        else:
            # update stats
            event['total_delay'] = self.t - event['event_start_time']
            complete_qty = len(self.complete_data)
            self.avg_delay = (self.avg_delay * complete_qty + event["total_delay"]) / (complete_qty + 1)
            self.avg_queue_delay = (self.avg_queue_delay * complete_qty + event["queue_delay"]) / (complete_qty + 1)
            self.complete_data.add(event['event_id'])

    def print_stats(self):
        print(f'{"*"*20} SIMULATION RESULTS {"*"*20}\n')
        print(f'Total simulation duration: {round(self.t, 2)} ms')
        print(f'Total arrived: {self.id_counter}')
        print(f'Total completed: {len(self.complete_data)}')
        print(f'Average total delay: {round(self.avg_delay, 2)} ms')
        print(f'Average queue delay: {round(self.avg_queue_delay, 2)} ms')

        print('\nQueue lengths at simulation end:')
        for idx, q in enumerate(self.queues):
            print(f'    Queue {idx}: {len(self.queues[idx])}')

    def run_sim(self):
        print(f'New Packet Switching simulation running...\n')
        self.t = 0

        heappush(self.events, (0, self.id_counter, {'event_type': 'new_data_arrival',
                                                    'event_start_time': 0,
                                                    'event_time': 0,
                                                    'path': None,
                                                    'curr_trip': None,
                                                    'event_id': self.id_counter,
                                                    'queue_delay': 0,
                                                    'total_delay': 0}))
        self.id_counter += 1

        while self.events and self.t < self.duration:

            event = heappop(self.events)[2]
            self.t = event['event_time']

            if event['event_type'] == 'new_data_arrival':
                self.process_new_data_arrival(event)

            elif event['event_type'] == 'transmission_end':
                self.process_transmission_end(event)

        print(f'Simulation finished!\n')
        self.print_stats()
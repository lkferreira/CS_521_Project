from heapq import *
import networkx as nx
import matplotlib.pyplot as plt
import collections
import random


class CircuitSwitchingSim:

    def __init__(self, duration, mean_data_arrival_time, transmission_time):
        self.duration = duration
        self.complete_data = set()
        self.avg_delay = 0
        self.avg_queue_delay = 0

        self.nodes = nx.DiGraph()
        self.init_graph()
        self.destination_node = self.nodes.number_of_nodes() - 1
        self.busy_edges = set()

        self.events = []
        self.t = 0
        self.queue = collections.deque()
        self.mean_data_arrival_time = mean_data_arrival_time
        self.transmission_time = transmission_time
        self.id_counter = 0

    def init_graph(self):
        edges = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3], [2, 4], [2, 5], [3, 5], [4, 5],
                  [1, 0], [2, 0], [3, 0], [2, 1], [3, 1], [3, 2], [4, 2], [5, 2], [5, 3], [5, 4]]
        self.nodes.add_edges_from(edges)

        # n = 25
        # p = 0.2
        # g = nx.erdos_renyi_graph(n, p, directed=True)
        # while not nx.is_strongly_connected(g):
        #     g = nx.erdos_renyi_graph(n, p)
        # self.nodes = g

    def view_nodes(self):
        nx.draw_networkx(self.nodes)
        plt.show()

    def process_data_arrival(self, event):
        if event['event_type'] == 'new_data_arrival':
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

        else:
            # update delay stats
            event['queue_delay'] += self.t - event['event_start_time']

        # find path to destination
        nodes_copy = self.nodes.copy()
        nodes_copy.remove_node(0)

        shortest_paths = [[0] + nx.shortest_path(nodes_copy, source=neighbor, target=self.destination_node)
                          for neighbor in nx.neighbors(self.nodes, 0)]
        paths = sorted(shortest_paths, key=lambda x: len(x))

        # begin transmission if a path is available
        if paths:
            event['path'] = paths[0]
            self.process_transmission_start(event)
        else:
            event['event_type'] = 'data_ready'
            self.queue.append(event)

    def process_transmission_start(self, event):
        path = event['path']
        edge_qty = len(path) - 1

        # update edges
        path_edges = [[path[i], path[i+1]] for i in range(len(path) - 1)]
        self.nodes.remove_edges_from(path_edges)

        # generate transmission end event
        event['event_type'] = 'transmission_end'
        event['event_time'] = self.t + (edge_qty * self.transmission_time)
        heappush(self.events, (event['event_time'], event['event_id'], event))

    def process_transmission_end(self, event):
        path = event['path']

        # update edges
        path_edges = [[path[i], path[i + 1]] for i in range(len(path) - 1)]
        self.nodes.add_edges_from(path_edges)

        # alert data waiting in queue for source node that path is free
        if self.queue:
            data_ready = self.queue.popleft()
            data_ready['event_time'] = self.t
            self.process_data_arrival(data_ready)

        # update stats
        event['total_delay'] = self.t - event['event_start_time']

        # update stats
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

        print(f'\nQueue length at simulation end: {len(self.queue)}')

    def run_sim(self):
        print(f'New Circuit Switching simulation running...\n')
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
                self.process_data_arrival(event)

            elif event['event_type'] == 'transmission_end':
                # print(event['path'])
                self.process_transmission_end(event)

        print('Simulation finished!\n')
        self.print_stats()

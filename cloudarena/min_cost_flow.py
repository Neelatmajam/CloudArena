from dataclasses import dataclass
import heapq
from math import inf


@dataclass
class Edge:
    to: int
    rev: int
    capacity: int
    cost: float


class MinCostFlow:
    def __init__(self, n: int):
        if n <= 0:
            raise ValueError("Graph must contain at least one node.")

        self.n = n
        self.graph: list[list[Edge]] = [[] for _ in range(n)]

    def add_edge(self, u: int, v: int, capacity: int, cost: float) -> None:
        self._validate_node(u)
        self._validate_node(v)

        if capacity < 0:
            raise ValueError("Edge capacity cannot be negative.")
        if cost < 0:
            raise ValueError(
                "Edge cost cannot be negative when using Dijkstra potentials."
            )

        forward = Edge(
            to=v,
            rev=len(self.graph[v]),
            capacity=capacity,
            cost=cost,
        )
        reverse = Edge(
            to=u,
            rev=len(self.graph[u]),
            capacity=0,
            cost=-cost,
        )

        self.graph[u].append(forward)
        self.graph[v].append(reverse)

    def min_cost_flow(
        self,
        source: int,
        sink: int,
        max_flow: int,
    ) -> tuple[int, float]:
        self._validate_node(source)
        self._validate_node(sink)

        if max_flow < 0:
            raise ValueError("Requested flow cannot be negative.")
        if source == sink:
            raise ValueError("Source and sink must be different nodes.")

        flow_sent = 0
        total_cost = 0.0
        potential = [0.0] * self.n

        while flow_sent < max_flow:
            distance, parent_node, parent_edge = self._dijkstra_with_potentials(
                source,
                potential,
            )

            if distance[sink] == inf:
                break

            for node, shortest_distance in enumerate(distance):
                if shortest_distance < inf:
                    potential[node] += shortest_distance

            path_flow = max_flow - flow_sent
            node = sink

            while node != source:
                previous = parent_node[node]
                edge_index = parent_edge[node]

                if previous is None or edge_index is None:
                    path_flow = 0
                    break

                edge = self.graph[previous][edge_index]
                path_flow = min(path_flow, edge.capacity)
                node = previous

            if path_flow == 0:
                break

            node = sink
            while node != source:
                previous = parent_node[node]
                edge_index = parent_edge[node]
                edge = self.graph[previous][edge_index]
                reverse_edge = self.graph[edge.to][edge.rev]

                edge.capacity -= path_flow
                reverse_edge.capacity += path_flow
                total_cost += path_flow * edge.cost

                node = previous

            flow_sent += path_flow

        return flow_sent, total_cost

    def _dijkstra_with_potentials(
        self,
        source: int,
        potential: list[float],
    ) -> tuple[list[float], list[int | None], list[int | None]]:
        distance = [inf] * self.n
        parent_node: list[int | None] = [None] * self.n
        parent_edge: list[int | None] = [None] * self.n

        distance[source] = 0
        heap: list[tuple[float, int]] = [(0, source)]

        while heap:
            current_distance, node = heapq.heappop(heap)

            if current_distance > distance[node]:
                continue

            for edge_index, edge in enumerate(self.graph[node]):
                if edge.capacity <= 0:
                    continue

                reduced_cost = edge.cost + potential[node] - potential[edge.to]
                new_distance = current_distance + reduced_cost

                if new_distance >= distance[edge.to]:
                    continue

                distance[edge.to] = new_distance
                parent_node[edge.to] = node
                parent_edge[edge.to] = edge_index
                heapq.heappush(heap, (new_distance, edge.to))

        return distance, parent_node, parent_edge

    def _validate_node(self, node: int) -> None:
        if node < 0 or node >= self.n:
            raise IndexError(f"Node {node} is outside graph size {self.n}.")

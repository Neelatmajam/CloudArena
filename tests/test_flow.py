import pytest

from cloudarena.min_cost_flow import MinCostFlow


def test_simple_path_choice_uses_lowest_cost_path():
    source, node_a, node_b, sink = 0, 1, 2, 3
    flow = MinCostFlow(4)
    flow.add_edge(source, node_a, capacity=1, cost=1)
    flow.add_edge(source, node_b, capacity=1, cost=5)
    flow.add_edge(node_a, sink, capacity=1, cost=1)
    flow.add_edge(node_b, sink, capacity=1, cost=1)

    flow_sent, total_cost = flow.min_cost_flow(source, sink, max_flow=1)

    assert flow_sent == 1
    assert total_cost == 2


def test_two_jobs_two_servers_finds_minimum_assignment():
    source = 0
    job_1, job_2 = 1, 2
    server_1, server_2 = 3, 4
    sink = 5
    flow = MinCostFlow(6)

    flow.add_edge(source, job_1, capacity=1, cost=0)
    flow.add_edge(source, job_2, capacity=1, cost=0)
    flow.add_edge(job_1, server_1, capacity=1, cost=3)
    flow.add_edge(job_1, server_2, capacity=1, cost=8)
    flow.add_edge(job_2, server_1, capacity=1, cost=4)
    flow.add_edge(job_2, server_2, capacity=1, cost=2)
    flow.add_edge(server_1, sink, capacity=1, cost=0)
    flow.add_edge(server_2, sink, capacity=1, cost=0)

    flow_sent, total_cost = flow.min_cost_flow(source, sink, max_flow=2)

    assert flow_sent == 2
    assert total_cost == 5


def test_no_path_returns_zero_flow_and_zero_cost():
    flow = MinCostFlow(3)
    flow.add_edge(0, 1, capacity=1, cost=4)

    flow_sent, total_cost = flow.min_cost_flow(source=0, sink=2, max_flow=1)

    assert flow_sent == 0
    assert total_cost == 0


def test_capacity_greater_than_one_sends_multiple_units():
    source, job_1, job_2, server, sink = 0, 1, 2, 3, 4
    flow = MinCostFlow(5)
    flow.add_edge(source, job_1, capacity=1, cost=0)
    flow.add_edge(source, job_2, capacity=1, cost=0)
    flow.add_edge(job_1, server, capacity=1, cost=2)
    flow.add_edge(job_2, server, capacity=1, cost=3)
    flow.add_edge(server, sink, capacity=2, cost=0)

    flow_sent, total_cost = flow.min_cost_flow(source, sink, max_flow=2)

    assert flow_sent == 2
    assert total_cost == 5


def test_reverse_edges_allow_rerouting_to_global_optimum():
    source = 0
    job_a, job_b = 1, 2
    server_x, server_y = 3, 4
    sink = 5
    flow = MinCostFlow(6)

    flow.add_edge(source, job_a, capacity=1, cost=0)
    flow.add_edge(source, job_b, capacity=1, cost=0)
    flow.add_edge(job_a, server_x, capacity=1, cost=1)
    flow.add_edge(job_a, server_y, capacity=1, cost=2)
    flow.add_edge(job_b, server_x, capacity=1, cost=1)
    flow.add_edge(job_b, server_y, capacity=1, cost=100)
    flow.add_edge(server_x, sink, capacity=1, cost=0)
    flow.add_edge(server_y, sink, capacity=1, cost=0)

    flow_sent, total_cost = flow.min_cost_flow(source, sink, max_flow=2)

    assert flow_sent == 2
    assert total_cost == 3


def test_reverse_edge_capacity_increases_after_augmentation():
    flow = MinCostFlow(2)
    flow.add_edge(0, 1, capacity=2, cost=7)

    flow_sent, total_cost = flow.min_cost_flow(source=0, sink=1, max_flow=1)

    assert flow_sent == 1
    assert total_cost == 7
    forward_edge = flow.graph[0][0]
    reverse_edge = flow.graph[1][forward_edge.rev]
    assert forward_edge.capacity == 1
    assert reverse_edge.capacity == 1


def test_public_edges_must_have_non_negative_costs_for_dijkstra_potentials():
    flow = MinCostFlow(2)

    with pytest.raises(ValueError, match="Edge cost cannot be negative"):
        flow.add_edge(0, 1, capacity=1, cost=-1)


@pytest.mark.parametrize(
    ("node_count", "message"),
    [
        (0, "Graph must contain at least one node."),
        (-1, "Graph must contain at least one node."),
    ],
)
def test_graph_requires_positive_node_count(node_count, message):
    with pytest.raises(ValueError, match=message):
        MinCostFlow(node_count)

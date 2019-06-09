import numpy as np

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from .google import get_distance_matrix

class SolverError(RuntimeError):
    """Error when the traveling salesman solution fails."""
    pass


def _create_data_model(locations, start_index=0):
    """Generate the dictionary required by the solver."""
    data = {}
    data['depot'] = start_index  # The starting location

    # Generate distance matrix from locations
    nl = len(locations)
    dm = get_distance_matrix(locations, locations)

    # The default TSP will always close the loop. What we want is to avoid
    # closing the loop and allow the path to end anywhere, but we need a
    # defined starting point. The easiest option is to create a degenerate
    # Hamiltonian path by adding one extra point added to everything, and
    # another that's only connected to the starting point (so that we
    # ensure starting and ending at that point).
    dm = np.array(dm)
    new_dm = np.zeros((nl+2, nl+2))

    # First fill in the known points
    new_dm[:nl, :nl] = dm

    # Now add a point of distance 0 to all points so that it can be placed
    # anywhere in the route, allowing any point to be the end point.
    new_dm[nl, :] = 0
    new_dm[:, nl] = 0

    # Add another point that is extremely distance from all points, except
    # for the desired starting point.
    effective_infinity = np.max(dm)*10000
    new_dm[nl+1, :] = effective_infinity
    new_dm[:, nl+1] = effective_infinity
    new_dm[start_index, nl+1] = 0
    new_dm[nl+1, start_index] = 0

    data['distance_matrix'] = new_dm
    data['num_vehicles'] = 1  # For TSP, there is only 1 vehicle
    return data


def solve_tsp(locations, start_index=0):
    """Solve the traveling salesman problem for a set of locations that can be
    found with the Google Maps API.

    Args:
        locations (list): A list of valid locations to search for using the
                          Google Maps API.

    Returns:
        list: The locations in the desired order.
    """
    data = _create_data_model(locations,start_index)

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes by directly accessing the
        data matrix in the parent scope."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    # The manager is just a container.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), data['num_vehicles'], data['depot'])

    # The actual model that solves the problem
    routing = pywrapcp.RoutingModel(manager)

    # Creates pointer to distance function to use, then sets it as evaluator.
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Define the algorithm used to optimize
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    assignment = routing.SolveWithParameters(search_parameters)

    # def print_solution(manager, routing, assignment):
        # """Prints assignment on console."""
        # print('Objective: {} miles'.format(assignment.ObjectiveValue()))
        # index = routing.Start(0)
        # plan_output = 'Route for vehicle 0:\n'
        # route_distance = 0
        # while not routing.IsEnd(index):
            # plan_output += ' {} ->'.format(manager.IndexToNode(index))
            # previous_index = index
            # index = assignment.Value(routing.NextVar(index))
            # route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
        # plan_output += ' {}\n'.format(manager.IndexToNode(index))
        # print(plan_output)
        # plan_output += 'Route distance: {}miles\n'.format(route_distance)

    # if assignment:
        # print_solution(manager, routing, assignment)
    if assignment:
        index = routing.Start(0)
        solution = []
        while not routing.IsEnd(index):
            next_loc = manager.IndexToNode(index)
            previous_index = index
            index = assignment.Value(routing.NextVar(index))

            # Don't add either dummy index. The indices that has no distance to anything.
            if next_loc >= len(locations):
                continue
            solution.append(next_loc)
    else:
        raise SolverError("Unable to converge solution to traveling salesman.")

    return solution

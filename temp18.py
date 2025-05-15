import itertools
from collections import defaultdict

def calculate_rungs(n):
    """Calculate rung latencies using the recurrence relation r_{i+1} = r_i + 2(n-i) + 1"""
    rungs = [1]
    for i in range(1, n):
        next_r = rungs[-1] + 2*(n - i) + 1
        rungs.append(next_r)
    return rungs

def simulate_network(n, coalition, choices, rungs):
    """Simulate network with coalition choices and return costs/routes"""
    left_rails = defaultdict(int)
    right_rails = defaultdict(int)
    routes = {}
    coalition_set = set(coalition)
    
    # Process coalition members first
    for idx, player in enumerate(coalition):
        if choices[idx]:  # Deviate to top rung
            routes[player] = 1
            for seg in range(1, player):
                left_rails[seg] += 1
                right_rails[seg] += 1
        else:  # Use original rung
            routes[player] = player
    
    # Process selfish players
    for player in range(1, n+1):
        if player in coalition_set:
            continue
        
        # Calculate costs for both options
        original_cost = rungs[player-1]
        
        # Cost of deviating to top rung
        dev_left_cost = sum(left_rails[seg] + 1 for seg in range(1, player))
        dev_right_cost = sum(right_rails[seg] + 1 for seg in range(1, player))
        deviation_cost = dev_left_cost + dev_right_cost + rungs[0]
        
        # Choose minimum cost route
        if deviation_cost < original_cost:
            routes[player] = 1
            for seg in range(1, player):
                left_rails[seg] += 1
                right_rails[seg] += 1
        else:
            routes[player] = player
    
    # Calculate individual costs
    individual_costs = {}
    for player in range(1, n+1):
        rung = routes[player]
        if rung == player:
            individual_costs[player] = rungs[player-1]
        else:
            left_cost = sum(left_rails[seg] for seg in range(rung, player))
            right_cost = sum(right_rails[seg] for seg in range(rung, player))
            individual_costs[player] = left_cost + right_cost + rungs[rung-1]
    
    system_cost = sum(individual_costs.values())
    coalition_cost = sum(individual_costs[p] for p in coalition)
    
    return system_cost, coalition_cost, routes, individual_costs

def analyze_bottom_coalitions(n_min=4, n_max=8):
    """Analyze all bottom-k coalitions up to n_max"""
    results = {}
    for n in range(n_min, n_max + 1):
        results[n] = {}
        rungs = calculate_rungs(n)
        
        for k in range(2, n):  # k from 2 to n-1
            coalition = list(range(n - k + 1, n + 1))  # Bottom k players
            min_coalition_cost = float('inf')
            best_system_cost = float('inf')
            best_routes = None
            best_choices = None
            
            # Try all possible coalition strategies
            for choices in itertools.product([True, False], repeat=k):
                sys_cost, coal_cost, routes, _ = simulate_network(
                    n, coalition, choices, rungs
                )
                
                if coal_cost < min_coalition_cost or \
                   (coal_cost == min_coalition_cost and sys_cost < best_system_cost):
                    min_coalition_cost = coal_cost
                    best_system_cost = sys_cost
                    best_routes = routes.copy()
                    best_choices = choices
            
            results[n][k] = {
                'system_cost': best_system_cost,
                'coalition_cost': min_coalition_cost,
                'routes': best_routes,
                'coalition_choices': dict(zip(coalition, best_choices))
            }
    return results

def print_results(results):
    """Print results with detailed routing information"""
    for n in sorted(results):
        print(f"\n=== n = {n} ===")
        rungs = calculate_rungs(n)
        print(f"Rung latencies: {rungs}")
        
        for k in sorted(results[n]):
            data = results[n][k]
            coalition = list(data['coalition_choices'].keys())
            
            print(f"\nBottom-{k} Coalition: Players {coalition}")
            print(f"System Cost: {data['system_cost']}")
            print(f"Coalition Cost: {data['coalition_cost']}")
            print("Route Decisions:")
            for p in sorted(data['routes'].items()):
                print(f"  Player {p[0]}: {p[1]}")

# looking at networks with n_min people to n_max people
n_min = 4
n_max = 7 
results = analyze_bottom_coalitions(n_min, n_max)
print_results(results)

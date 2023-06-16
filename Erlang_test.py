from pyworkforce.queuing import ErlangC
import pandas as pd


erlang = ErlangC(transactions=37906, aht=9.2, interval=15660, asa=30, shrinkage=0.30)

positions_requirements = erlang.required_positions(service_level=0.65, max_occupancy=0.85)
print("positions_requirements: ", positions_requirements)


achieved_service_level = erlang.service_level(positions=positions_requirements['raw_positions'])
print("achieved_service_level: ", achieved_service_level)

achieved_service_level = erlang.service_level(positions=positions_requirements['positions'],
                                              scale_positions=True)
print("achieved_service_level: ", achieved_service_level)


waiting_probability = erlang.waiting_probability(positions=positions_requirements['raw_positions'])
print("waiting_probability: ", waiting_probability)


achieved_occupancy = erlang.achieved_occupancy(positions=positions_requirements['raw_positions'])
print("achieved_occupancy: ", achieved_occupancy)


from pyworkforce.shifts import MinAbsDifference


# Columns are an hour of the day, rows are the days
required_resources = [
    [9, 11, 17, 9, 7, 12, 5, 11, 8, 9, 18, 17, 8, 12, 16, 8, 7, 12, 11, 10, 13, 19, 16, 7],
    [13, 13, 12, 15, 18, 20, 13, 16, 17, 8, 13, 11, 6, 19, 11, 20, 19, 17, 10, 13, 14, 23, 16, 8]
]


required_resources = pd.DataFrame(required_resources)
required_resources


shifts_coverage = {"Morning": [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   "Afternoon": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
                   "Night": [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
                   "Mixed": [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]}

shifts_coverage = pd.DataFrame(shifts_coverage)
shifts_coverage

scheduler = MinAbsDifference(num_days=2,
                             periods=24,
                             shifts_coverage=shifts_coverage,
                             required_resources=required_resources,
                             max_period_concurrency=27,
                             max_shift_concurrency=25)

solution = scheduler.solve()
print(solution)


# In[32]:


from pyworkforce.shifts import MinRequiredResources

# Columns are an hour of the day, rows are the days
required_resources = [
    [9, 11, 17, 9, 7, 12, 5, 11, 8, 9, 18, 17, 8, 12, 16, 8, 7, 12, 11, 10, 13, 19, 16, 7],
    [13, 13, 12, 15, 18, 20, 13, 16, 17, 8, 13, 11, 6, 19, 11, 20, 19, 17, 10, 13, 14, 23, 16, 8]
]

# Each entry of a shift, is an hour of the day (24 columns)
shifts_coverage = {"Morning": [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   "Afternoon": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
                   "Night": [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
                   "Mixed": [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]}


# The cost of shifting a resource if each shift, if present, solver will minimize the total cost
cost_dict = {"Morning": 8, "Afternoon": 8, "Night": 10, "Mixed": 7}


scheduler = MinRequiredResources(num_days=2,
                                 periods=24,
                                 shifts_coverage=shifts_coverage,
                                 required_resources=required_resources,
                                 cost_dict=cost_dict,
                                 max_period_concurrency=25,
                                 max_shift_concurrency=25)

solution = scheduler.solve()

print(solution)





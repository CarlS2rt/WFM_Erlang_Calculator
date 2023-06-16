import math


def utilisation(Intensity, agents):
    try:
        utilisation = Intensity / agents
    except ZeroDivisionError:
        utilisation = 0
        
    if utilisation < 0:
        utilisation = 0
    elif utilisation > 1:
        utilisation = 1
    
    return utilisation


def top_row(Intensity, agents):
    return (Intensity ** agents) / math.factorial(agents)


def bottom_row(Intensity, agents):
    answer = 0
    
    for k in range(agents):
        answer += (Intensity ** k) / math.factorial(k)
    
    return answer


def ErlangC1(Intensity, agents):
    try:
        erlang_top_row = top_row(Intensity, agents)
        erlang_bottom_row = bottom_row(Intensity, agents)
        erlang_utilisation = utilisation(Intensity, agents)
        erlang_c = erlang_top_row / (erlang_top_row + ((1 - erlang_utilisation) * erlang_bottom_row))
    except ZeroDivisionError:
        erlang_c = 0
    
    if erlang_c < 0:
        erlang_c = 0
    elif erlang_c > 1:
        erlang_c = 1
    
    return erlang_c


def ServiceLevel(Calls, Reporting_Period, average_handling_time, agents):
    erlang_c = ErlangC1((Calls / (Reporting_Period * 60)) * average_handling_time, agents)
    service_level = 1 - erlang_c * math.exp(-1 * agents * ((Calls / (Reporting_Period * 60)) * average_handling_time - 1/agents))
    
    if service_level < 0:
        service_level = 0
    elif service_level > 1:
        service_level = 1
    
    return service_level


def AgentsReq(Calls, Reporting_Period, average_handling_time, service_level_percent, service_level_time):
    min_agents = int((Calls / (Reporting_Period * 60)) * average_handling_time)
    agents = min_agents
    
    while ServiceLevel(Calls, Reporting_Period, average_handling_time, agents) < service_level_percent:
        agents += 1
    
    if agents > 600:
        print("This calculator only works up to 600 agents. For higher numbers, please use the online version of this calculator")
    
    return agents


def AgentsFTE(Calls, Reporting_Period, average_handling_time, service_level_percent, service_level_time, Shrinkage):
    min_agents = int((Calls / (Reporting_Period * 60)) * average_handling_time)
    agents = min_agents
    
    while ServiceLevel(Calls, Reporting_Period, average_handling_time, agents) < service_level_percent:
        agents += 1
    
    if Shrinkage < 0:
        Shrinkage = 0
    elif Shrinkage > 0.9998:
        Shrinkage = 0.99
    
    agents_fte = agents / (1 - Shrinkage)
    
    if agents_fte > 600:
        print("This calculator only works up to 600 agents. For higher numbers, please use the online version of this calculator")
    
    return agents_fte


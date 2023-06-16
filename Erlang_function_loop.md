```python
team = ['Commercial_Billing','Commercial_Sales','Cable_Sales','Cable_Retention','Cable_Seniors','Residential_FS','Commercial_FS',
        'Wireline_Sales','Wireline_Retention','Wireline_Seniors']
dfs = []
for t in team:
    team_group = appended_data.loc[(appended_data['Team']  == t)]
    actual_cv = team_group.groupby(['Team','DateTime'])['Actual_CV'].sum()
    actual_cv = actual_cv.reset_index()
    actual_cv.set_index('DateTime', inplace=True) # set the index to the 'DateTime' column
    actual_cv = actual_cv.resample('30 min').sum() # remove the 'on' parameter
    actual_cv.reset_index(inplace=True)
    actual_cv.set_index('DateTime', inplace=True)
    
    forecasted_cv = team_group.groupby(['Team','DateTime'])['Forecasted_CV'].sum()
    forecasted_cv = forecasted_cv.reset_index()
    forecasted_cv.set_index('DateTime', inplace=True) # set the index to the 'DateTime' column
    forecasted_cv = forecasted_cv.resample('30 min').sum() # remove the 'on' parameter
    forecasted_cv.reset_index(inplace=True)
    forecasted_cv.set_index('DateTime', inplace=True)
    
    grouped_aht = team_group.groupby(['Team','DateTime'])['Actual_Workload'].sum()
    grouped_aht = grouped_aht.reset_index()
    grouped_aht['Actual_Workload'] = grouped_aht['Actual_Workload'].replace(0, np.nan)
    grouped_aht.set_index('DateTime', inplace=True) # set the index to the 'DateTime' column
    grouped_aht = grouped_aht.resample('30 min').sum() # remove the 'on' parameter
    grouped_cv = team_group.groupby(['Team','DateTime'])['Actual_CV'].sum()
    grouped_cv = grouped_cv.reset_index()
    grouped_cv.set_index('DateTime', inplace=True) # set the index to the 'DateTime' column
    grouped_cv = grouped_cv.resample('30 min').sum() # remove the 'on' parameter
    actual_aht = grouped_aht.merge(grouped_cv, on='DateTime', how='left')
    actual_aht['Actual_AHT'] = actual_aht['Actual_Workload'] / actual_aht['Actual_CV']
    actual_aht = actual_aht.drop(columns=['Actual_Workload','Actual_CV'])
    actual_aht.reset_index(inplace=True)
    actual_aht.set_index('DateTime', inplace=True)
    actual_aht['Actual_AHT'] = actual_aht['Actual_AHT'].fillna(0)
    actual_aht['Actual_AHT'] = round(actual_aht['Actual_AHT'])
    
    grouped_faht = team_group.groupby(['Team','DateTime'])['Forecasted_Workload'].sum()
    grouped_faht = grouped_faht.reset_index()
    grouped_faht['Forecasted_Workload'] = grouped_faht['Forecasted_Workload'].replace(0, np.nan)
    grouped_faht.set_index('DateTime', inplace=True) # set the index to the 'DateTime' column
    grouped_faht = grouped_faht.resample('30 min').sum() # remove the 'on' parameter
    grouped_fcv = team_group.groupby(['Team','DateTime'])['Forecasted_CV'].sum()
    grouped_fcv = grouped_fcv.reset_index()
    grouped_fcv.set_index('DateTime', inplace=True) # set the index to the 'DateTime' column
    grouped_fcv = grouped_fcv.resample('30 min').sum() # remove the 'on' parameter
    forecasted_aht = grouped_faht.merge(grouped_fcv, on='DateTime', how='left')
    forecasted_aht['Forecasted_AHT'] = forecasted_aht['Forecasted_Workload'] / forecasted_aht['Forecasted_CV']
    forecasted_aht = forecasted_aht.drop(columns=['Forecasted_Workload','Forecasted_CV'])
    forecasted_aht.reset_index(inplace=True)
    forecasted_aht.set_index('DateTime', inplace=True)
    forecasted_aht['Forecasted_AHT'] = forecasted_aht['Forecasted_AHT'].fillna(0)
    forecasted_aht['Forecasted_AHT'] = round(forecasted_aht['Forecasted_AHT'])

    cv = actual_cv.merge(forecasted_cv, on=['DateTime'], how='left')
    aht = actual_aht.merge(forecasted_aht, on=['DateTime'], how='left')
    table = cv.merge(aht, on=['DateTime'], how='left')
    # table = table.merge(req_fte, on=['DateTime'], how='left')
    table['Team'] = t
    table = table.reindex(columns=['Team'] + list(table.columns[:-1]))
    dfs.append(table)

result = pd.concat(dfs)
result.reset_index(inplace=True)
result['Date'] = result['DateTime'].dt.date
result['Time'] = result['DateTime'].dt.time
result = result.drop('DateTime', axis=1)
result['Time_Interval'] = '00:30'
result = result[['Team', 'Date', 'Time', 'Time_Interval', 'Actual_CV', 'Forecasted_CV', 'Actual_AHT', 'Forecasted_AHT']]
result.head()

```

```python
def AgentsFTE(Calls, Reporting_Period, average_handling_time, service_level_percent, service_level_time, Shrinkage):
    
    def ProbCallWaits(Calls, Reporting_Period, average_handling_time, agents):
        try:
            def PowerFact(m, x):
                s = 0
                for k in range(1, m + 1):
                    s += math.log(x / k)
                return math.exp(s)

            Intensity = (Calls * average_handling_time) / (Reporting_Period * 60)
            ProbCallWaits = PowerFact(agents, Intensity) / math.factorial(agents) / (1 - Intensity / agents + (Intensity / agents) * (PowerFact(agents, Intensity) / math.factorial(agents)))
            
        except ZeroDivisionError:
            ProbCallWaits = 0
        
        if ProbCallWaits < 0:
            ProbCallWaits = 0
        elif ProbCallWaits > 1:
            ProbCallWaits = 1
        
        return ProbCallWaits

    if Calls == 0:
        return 0
    min_agents = math.ceil((Calls / (Reporting_Period * 60)) * average_handling_time)
    agents = min_agents
    Intensity = (Calls * average_handling_time) / (Reporting_Period * 60)
    def ServiceLevel(Calls, Reporting_Period, average_handling_time, agents):
        
        try:
            service_level = 1 - ProbCallWaits(Calls, Reporting_Period, average_handling_time, agents) * math.exp(-(agents - Intensity) * service_level_time / average_handling_time)
        except ZeroDivisionError:
            service_level = 0

        if service_level < 0:
            service_level = 0
        elif service_level > 1:
            service_level = 1

        return service_level
        
    while ServiceLevel(Calls, Reporting_Period, average_handling_time, agents) < service_level_percent:
        agents += 1
    
    if Shrinkage < 0:
        Shrinkage = 0
    elif Shrinkage > 0.9998:
        Shrinkage = 0.99
    
    agents_fte = agents / (1 - Shrinkage)
    agents_fte_rounded = math.ceil(agents_fte)
    
    return agents_fte_rounded
```


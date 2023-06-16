import pandas as pd
import os
import math
from math import exp, ceil, floor
import numpy as np
import cx_Oracle
from config import oracle_wfm_key
import time
import datetime as dt
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.types import String
from tqdm import tqdm
import itertools
import databases as db
import pyworkforce

ods = db.oracle('cco_wfm',oracle_wfm_key)
verint  = db.ssms()
directory = "I:\\GitHub\\forecasting\\accuracy\\accuracy_exports\\"

service = ['BSSC Billing ALL (new)','BSSC Senior','Commercial COAST','Mooresville_BSSC_Billing','BSSC Sales Cable','BSSC Sales Wireline','Mooresville_BSSC_Sales',
            'Bend/Cable Consumer Sales','OB_QCB Bend/Cable Sales','Cable Specialist','OB_OCB_Cable_Con_Spec','Cable Sales Seniors',
            'Financial Services Res','Financial Services Bus',
            'Wireline Sales and Service','Wireline Service QCB','Wireline Consumer Specialist','Wireline Consumer Triage','Wireline Retention QCB','Wireline Senior Specialist 1','Wireline Repair Residential']
start = '2023-04-12 00:00:00.000'
end = '2023-04-27 23:45:00.000'
appended_data = []
for name in service:
    new_query = f'''SELECT 
                        [Queue],
                        [DateTime],
                        [Actual_CV],
                        [Forecasted_CV],
                        [Actual_AHT],
                        [Forecasted_AHT]                                             
                    FROM [BPMAINDB].[dbo].[V_AdHoc_PerformanceStatistics]
                    WHERE ([Queue] = '{name}') AND ([DateTime] BETWEEN '{start}' AND '{end}')
                    AND ([UserName] = 'satverintwrkoptmgmt')'''
    data = pd.read_sql(new_query, verint)
    appended_data.append(data)
appended_data = pd.concat(appended_data)

team_dict = {'BSSC Billing ALL (new)' : 'Commercial_Billing','BSSC Senior' : 'Commercial_Billing','Commercial COAST' : 'Commercial_Billing','Mooresville_BSSC_Billing' : 'Commercial_Billing',
        'BSSC Sales Cable' : 'Commercial_Sales','BSSC Sales Wireline' : 'Commercial_Sales','Mooresville_BSSC_Sales' : 'Commercial_Sales',
        'Bend/Cable Consumer Sales' : 'Cable_Sales','OB_QCB Bend/Cable Sales' : 'Cable_Sales','Cable Specialist' : 'Cable_Retention','OB_OCB_Cable_Con_Spec' : 'Cable_Retention',
        'Cable Sales Seniors' : 'Cable_Seniors',
        'Financial Services Res' : 'Residential_FS','Financial Services Bus' : 'Commercial_FS',
        'Wireline Sales and Service' : 'Wireline_Sales','Wireline Service QCB' : 'Wireline_Sales',
        'Wireline Consumer Specialist' : 'Wireline_Retention','Wireline Consumer Triage' : 'Wireline_Retention','Wireline Retention QCB' : 'Wireline_Retention',
        'Wireline Senior Specialist 1': 'Wireline_Seniors', 'Wireline Repair Residential': 'Wireline_Repair'}

appended_data['Team'] = appended_data['Queue'].map(team_dict)
appended_data = appended_data.reindex(columns=['Team'] + list(appended_data.columns[:-1]))
appended_data['Actual_Workload'] = appended_data['Actual_AHT'] * appended_data['Actual_CV']
appended_data['Actual_Workload'] = appended_data['Actual_Workload'].replace(0, np.nan)
appended_data['Forecasted_Workload'] = appended_data['Forecasted_AHT'] * appended_data['Forecasted_CV']
appended_data['Forecasted_Workload'] = appended_data['Forecasted_Workload'].replace(0, np.nan)

team = ['Commercial_Billing','Commercial_Sales','Cable_Sales','Cable_Retention','Cable_Seniors','Residential_FS','Commercial_FS',
        'Wireline_Sales','Wireline_Retention','Wireline_Seniors', 'Wireline_Repair']
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
    table['Team'] = t
    table = table.reindex(columns=['Team'] + list(table.columns[:-1]))
    dfs.append(table)

call_data = pd.concat(dfs)
call_data.reset_index(inplace=True)
call_data['Date'] = call_data['DateTime'].dt.date
call_data['Time'] = call_data['DateTime'].dt.time
call_data = call_data.drop('DateTime', axis=1)
call_data['Time_Interval'] = '00:30'
call_data = call_data[['Team', 'Date', 'Time', 'Time_Interval', 'Actual_CV', 'Forecasted_CV', 'Actual_AHT', 'Forecasted_AHT']]

# ## Erlang Testing

class ErlangC:
    """
    Computes the number of positions required to attend a number of transactions in a
    queue system based on erlangc.rst. Implementation inspired on:
    https://lucidmanager.org/data-science/call-centre-workforce-planning-erlang-c-in-r/
    Parameters
    ----------
    transactions: float,
        The number of total transactions that comes in an interval.
    aht: float,
        Average handling time of a transaction (minutes).
    asa: float,
        The required average speed of answer (minutes).
    interval: int,
        Interval length (minutes) where the transactions come in
    shrinkage: float,
        Percentage of time that an operator unit is not available.
    """

    def __init__(self, transactions: float, aht: float, asa: float,
                 interval: int, shrinkage=0.0,
                 **kwargs):

        if transactions <= 0:
            raise ValueError("transactions can't be smaller or equals than 0")

        if aht <= 0:
            raise ValueError("aht can't be smaller or equals than 0")

        if asa <= 0:
            raise ValueError("asa can't be smaller or equals than 0")

        if interval <= 0:
            raise ValueError("interval can't be smaller or equals than 0")

        if shrinkage < 0 or shrinkage >= 1:
            raise ValueError("shrinkage must be between in the interval [0,1)")

        self.n_transactions = transactions
        self.aht = aht / 60  # Convert aht from seconds to minutes
        self.interval = interval
        self.asa = asa
        self.intensity = (self.n_transactions / self.interval) * self.aht
        self.shrinkage = shrinkage


    def waiting_probability(self, positions: int, scale_positions: bool = False):
        """
        Returns the probability of waiting in the queue
        Parameters
        ----------
        positions: int,
            The number of positions to attend the transactions.
        scale_positions: bool, default=False
            Set it to True if the positions were calculated using shrinkage.
        """

        if scale_positions:
            productive_positions = floor((1 - self.shrinkage) * positions)
        else:
            productive_positions = positions

        erlang_b_inverse = 1
        for position in range(1, productive_positions + 1):
            erlang_b_inverse = 1 + (erlang_b_inverse * position / self.intensity)

        erlang_b = 1 / erlang_b_inverse
        return productive_positions * erlang_b / (productive_positions - self.intensity * (1 - erlang_b))

    def service_level(self, positions: int, scale_positions: bool = False):
        """
        Returns the expected service level given a number of positions
        Parameters
        ----------
        positions: int,
            The number of positions attending.
        scale_positions: bool, default = False
            Set it to True if the positions were calculated using shrinkage.
        """
        if scale_positions:
            productive_positions = floor((1 - self.shrinkage) * positions)
        else:
            productive_positions = positions

        probability_wait = self.waiting_probability(productive_positions, scale_positions=False)
        exponential = exp(-(productive_positions - self.intensity) * (self.asa / self.aht))
        return max(0, 1 - (probability_wait * exponential))

    def achieved_occupancy(self, positions: int, scale_positions: bool = False):
        """
        Returns the expected occupancy of positions
        Parameters
        ----------
        positions: int,
            The number of raw positions
        scale_positions: bool, default=False
            Set it to True if the positions were calculated using shrinkage.
        """
        if scale_positions:
            productive_positions = floor((1 - self.shrinkage) * positions)
        else:
            productive_positions = positions

        return self.intensity / productive_positions

    def required_positions(self, service_level: float, max_occupancy: float = 1.0):
        """
        Computes the requirements using erlangc.rst
        Parameters
        ----------
        service_level: float,
            Target service level
        max_occupancy: float,
            The maximum fraction of time that a transaction can occupy a position
        Returns
        -------
        raw_positions: int,
            The required positions assuming shrinkage = 0
        positions: int,
            The number of positions needed to ensure the required service level
        service_level: float,
            The fraction of transactions that are expected to be assigned to a position,
            before the asa time
        occupancy: float,
            The expected occupancy of positions
        waiting_probability: float,
            The probability of a transaction waiting in the queue
        """

        if service_level < 0 or service_level > 1:
            raise ValueError("service_level must be between 0 and 1")

        if max_occupancy < 0 or max_occupancy > 1:
            raise ValueError("max_occupancy must be between 0 and 1")

        positions = round(self.intensity + 1)
        achieved_service_level = self.service_level(positions, scale_positions=False)
        while achieved_service_level < service_level:
            positions += 1
            achieved_service_level = self.service_level(positions, scale_positions=False)

        achieved_occupancy = self.achieved_occupancy(positions, scale_positions=False)

        raw_positions = ceil(positions)

        if achieved_occupancy > max_occupancy:
            raw_positions = ceil(self.intensity / max_occupancy)
            achieved_occupancy = self.achieved_occupancy(raw_positions)
            achieved_service_level = self.service_level(raw_positions)

        waiting_probability = self.waiting_probability(positions=raw_positions)
        positions = ceil(raw_positions / (1 - self.shrinkage))

        return {"raw_positions": raw_positions,
                "positions": positions,
                "service_level": achieved_service_level,
                "occupancy": achieved_occupancy,
                "waiting_probability": waiting_probability}

team_settings = {
    'Commercial_Billing': (0.60, 0.05, 30, 30),
    'Commercial_Sales': (0.60, 0.05, 30, 30),
    'Cable_Sales': (0.65, 0.05, 30, 30),
    'Cable_Retention': (0.65, 0.05, 30, 30),
    'Cable_Seniors': (0.70, 0.05, 30, 30),
    'Residential_FS': (0.65, 0.05, 30, 30),
    'Commercial_FS': (0.65, 0.05, 30, 30),
    'Wireline_Sales': (0.65, 0.10, 30, 30),
    'Wireline_Retention': (0.65, 0.10, 30, 30),
    'Wireline_Seniors': (0.70, 0.05, 30, 30),
    'Wireline_Repair': (0.65, 0.30, 30, 30)
}	
	
def process_data(team_info, team, interval_df, data_type):
    service_level_percent, shrinkage, reporting_period, service_level_time = team_info
    results = []

    for _, row in interval_df.iterrows():
        transactions = row[f'{data_type}_CV']
        aht = row[f'{data_type}_AHT']
        interval = reporting_period
        asa = service_level_time / 60

        if transactions > 0 and aht > 0:
            erlang = ErlangC(transactions=transactions, aht=aht, interval=interval, asa=asa, shrinkage=shrinkage)
            positions_requirements = erlang.required_positions(service_level=service_level_percent)

            result = {
                'Team': team,
                'Date': row['Date'],
                'Time': row['Time'],
                'Time_Interval': row['Time_Interval'],
                f'{data_type}_CV': transactions,
                f'{data_type}_AHT': aht,
                f'{data_type}_Required_FTE': positions_requirements['positions'],
                f'{data_type}_Raw_FTE': positions_requirements['raw_positions'],
                f'Service_Level_{data_type}': positions_requirements['service_level'],
                f'Occupancy_{data_type}': positions_requirements['occupancy'],
                f'Waiting_Probablility_{data_type}': positions_requirements['waiting_probability'],
            }
            results.append(result)

    return pd.DataFrame(results)

results = []
for team, settings in team_settings.items():
    team_df = call_data[call_data['Team'] == team]
    actual_df = process_data(settings, team, team_df, 'Actual')
    forecasted_df = process_data(settings, team, team_df, 'Forecasted')
    result_df = actual_df.merge(forecasted_df, on=['Team', 'Date', 'Time', 'Time_Interval'], how='outer')
    
    if not result_df.empty:
        results.append(result_df)

final_results = pd.concat(results, ignore_index=True)
final_results.fillna(0, inplace=True)
final_results['Date'] = pd.to_datetime(final_results['Date'], format='%Y-%m-%d')
final_results = final_results.sort_values(by=['Team', 'Date', 'Time'])
directory = "I:\\GitHub\\forecasting\\accuracy\\accuracy_exports\\"

# Convert 'Date' column to datetime and create a new 'Month' column
final_results['Date'] = pd.to_datetime(final_results['Date'])
final_results['Month'] = final_results['Date'].dt.strftime('%Y-%m')

# Export the data
teams = final_results['Team'].unique()
for team in teams:
    team_result = final_results[final_results['Team'] == team]
    for month in team_result['Month'].unique():
        month_result = team_result[team_result['Month'] == month]
        file_name = f"{team}_{month}.txt"
        file_path = os.path.join(directory, file_name)
        month_result.to_csv(file_path, sep='\t', index=False)


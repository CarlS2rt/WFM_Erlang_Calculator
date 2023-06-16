# Call Center Performance Analysis

This repository contains a Python script that performs analysis and forecasting of call center performance metrics. The script utilizes data from call center systems, processes it, and provides insights into various performance indicators. The analysis is based on the Erlang C formula for workforce planning.

## Purpose

The purpose of this script is to help call center managers and analysts gain valuable insights into call center performance and make informed decisions regarding workforce planning. By analyzing historical call center data, the script provides metrics such as call volume, average handling time (AHT), forecasted workload, actual workload, service levels, waiting probabilities, and required workforce positions.

## How the Code Works

The script follows the following steps:

1. Database Connection: Establishes connections to the Oracle and SSMS databases using custom classes and retrieves call center data.

2. Data Transformation and Aggregation: Transforms and aggregates the retrieved data by mapping service names to corresponding teams, calculating workload, and rearranging column orders.

3. Data Processing and Analysis: Groups the transformed data by team and datetime, performs resampling to a 30-minute interval, and calculates metrics such as actual and forecasted CV (Call Volume), AHT, and workload. This analysis is performed for each team.

4. Workforce Requirements Calculation: Utilizes the Erlang C formula to calculate the number of required workforce positions based on service levels, average handling time, call volume, and other parameters. The script provides insights into service levels achieved, occupancy rates, and waiting probabilities.

5. Exporting Results: The analyzed data is exported to text files, separated by team and month, for further analysis or reporting purposes.

## Possible Applications

- **Workforce Planning:** Call center managers can utilize the script to accurately forecast workforce requirements based on historical data and service level targets. This can help optimize staffing levels, reduce costs, and improve customer service.

- **Performance Monitoring:** Analysts can use the script to monitor call center performance over time, identify trends, and track key performance indicators such as service levels, workload, and waiting probabilities. This information can be used to identify areas for improvement and make data-driven decisions.

- **Benchmarking and Comparison:** The script allows for easy comparison of call center performance across different teams or time periods. By analyzing metrics such as service levels and occupancy rates, analysts can identify top-performing teams or areas that require improvement.

- **Capacity Planning:** The insights provided by the script can aid in capacity planning and resource allocation. Call center managers can ensure that they have adequate staffing levels to handle call volumes while maintaining desired service levels.

## Requirements and Dependencies

To run the script, ensure you have the following:

- Python 3.x
- Required Python packages: pandas, numpy, cx_Oracle, sqlalchemy, tqdm

## Usage

1. Clone the repository: `git clone https://github.com/your-username/call-center-performance.git`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Configure the database connections and credentials in the script.
4. Modify the time range, service names, and other parameters as per your requirements.
5. Run the script: `python call_center_analysis.py`
6. The analyzed results will be exported as text files in the specified directory.

Feel free to customize the script according to your specific needs and data sources.

## Contributing

Contributions to this repository are welcome. If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use and modify the code as per the license terms.

## Acknowledgments

This script was inspired by the need for accurate call center performance analysis and workforce planning. We would like to thank the

 open-source community for their valuable contributions and the libraries used in this project.

For detailed code explanations and examples, please refer to the code comments and the documentation of the libraries used.

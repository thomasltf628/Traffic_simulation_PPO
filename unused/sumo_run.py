import traci
traci.init(port=8813)
import pandas as pd
from datetime import datetime

now = datetime.now()
dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")

# Start SUMO simulation
port = 8813  # Choose any available port number
sumoCmd = ["sumo", "-c", "osm.sumocfg", "--remote-port", str(port)]
traci.start(sumoCmd, port=port)

# Initialize data storage
traffic_data = []

# Dictionary to store vehicle data
vehicle_data = {}

# Speed threshold to consider a vehicle is waiting (in m/s)
speed_threshold = 0.1

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()

    # Extract features for each intersection
    for junction in traci.trafficlight.getIDList():
        try:
            state = traci.trafficlight.getRedYellowGreenState(junction)
            phase_duration = traci.trafficlight.getPhaseDuration(junction)

            for link in traci.trafficlight.getControlledLinks(junction):
                for lane_tuple in link:
                    lane_id = lane_tuple[0]
                    edge_id = traci.lane.getEdgeID(lane_id)

                    # Collect parameters for each lane
                    lane_queue_length = traci.lane.getLastStepHaltingNumber(lane_id)
                    lane_avg_speed = traci.lane.getLastStepMeanSpeed(lane_id)
                    lane_throughput = traci.lane.getLastStepVehicleNumber(lane_id)
                    lane_fuel_consumption = traci.lane.getFuelConsumption(lane_id)
                    lane_emissions = traci.lane.getCO2Emission(lane_id)
                    lane_length = traci.lane.getLength(lane_id)
                    lane_density = traci.lane.getLastStepVehicleNumber(lane_id) / lane_length

                    # Collect vehicle-specific data
                    for vehicle_id in traci.lane.getLastStepVehicleIDs(lane_id):
                        if vehicle_id not in vehicle_data:
                            vehicle_data[vehicle_id] = {
                                'total_travel_time': 0,
                                'stop_count': 0,
                                'waiting_time': 0,
                                'last_speed': 0
                            }
                        vehicle_data[vehicle_id]['total_travel_time'] += traci.simulation.getDeltaT() / 1000.0
                        if traci.vehicle.getSpeed(vehicle_id) < speed_threshold:
                            vehicle_data[vehicle_id]['waiting_time'] += traci.simulation.getDeltaT() / 1000.0
                        if traci.vehicle.getSpeed(vehicle_id) < 0.1 and vehicle_data[vehicle_id]['last_speed'] >= 0.1:
                            vehicle_data[vehicle_id]['stop_count'] += 1
                        vehicle_data[vehicle_id]['last_speed'] = traci.vehicle.getSpeed(vehicle_id)

                    # Append lane data to storage
                    traffic_data.append({
                        "junction": junction,
                        "state": state,
                        "phase_duration": phase_duration,
                        "lane_id": lane_id,
                        "queue_length": lane_queue_length,
                        "avg_speed": lane_avg_speed,
                        "throughput": lane_throughput,
                        "fuel_consumption": lane_fuel_consumption,
                        "emissions": lane_emissions,
                        "traffic_density": lane_density,
                        "time": traci.simulation.getTime()
                    })

        except traci.exceptions.TraCIException as e:
            print(f"Error processing junction {junction}: {e}")
            continue

traci.close()

# Convert to DataFrame for analysis
df = pd.DataFrame(traffic_data)

# Save the data to an Excel file
try:
    df.to_excel(f"output_{dt_string}.xlsx", index=False)
except Exception as e:
    print(e)
    while(True):
        user_input = input('Please rectify error and press "done" to proceed')
        if user_input == 'done':
            df.to_excel(f"output_{dt_string}.xlsx", index=False)
            break
        else:
            break
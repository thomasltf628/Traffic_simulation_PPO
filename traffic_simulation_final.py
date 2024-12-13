import traci
import pandas as pd
from datetime import datetime

import os
import sys

def check_sumo_setup():
    # 檢查 SUMO_HOME
    sumo_home = os.environ.get('SUMO_HOME')
    print(f"SUMO_HOME: {sumo_home}")
    
    # 檢查 SUMO 可執行檔
    sumo_binary = os.path.join(sumo_home, 'bin', 'sumo-gui.exe')
    if os.path.exists(sumo_binary):
        print(f"SUMO GUI 存在於: {sumo_binary}")
    else:
        print("找不到 SUMO GUI")
    
    # 檢查 SUMO tools 路徑
    tools_path = os.path.join(sumo_home, 'tools')
    if tools_path not in sys.path:
        sys.path.append(tools_path)
        print(f"已添加 SUMO tools 到 Python 路徑: {tools_path}")
    
    # 嘗試導入 traci
    try:
        import traci
        print("成功導入 traci")
    except ImportError as e:
        print(f"無法導入 traci: {str(e)}")

check_sumo_setup()

now = datetime.now()
dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")

# Start SUMO simulation
sumoCmd = ["sumo-gui", "-c", r"C:\Users\super\traffic_simulation\intersection.sumocfg"]
traci.start(sumoCmd)
step = 0
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()  # Advance the simulation by one step
    print(f"Simulation at step: {step}")
    step += 1
    
    # Example: Retrieve vehicle data
    vehicle_ids = traci.vehicle.getIDList()
    tl_ids = traci.trafficlight.getIDList()
    """for vehicle_id in vehicle_ids:
        position = traci.vehicle.getPosition(vehicle_id)
        road_id = traci.vehicle.getRoadID(vehicle_id)
        lane_id = traci.vehicle.getLaneID(vehicle_id)
        print(vehicle_id, position, road_id, lane_id)"""
    for tl_id in tl_ids:
        current_phase = traci.trafficlight.getPhase(tl_id)
        current_state = traci.trafficlight.getRedYellowGreenState(tl_id)
        print(f"""
        交通燈 {tl_id}:
        - 當前相位: {current_phase}
        - 當前狀態: {current_state}
        """)
# Close the simulation Traffic_simulation_PPO
traci.close()
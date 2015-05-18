#!/usr/bin/env python
"""
@file    runner.py
@author  Joao Goncalves
@date    2015-05-18

Master Thesis Scenario 1 - A Simple SUMO to ADAS communication.
"""

import os
import sys
import optparse
import subprocess
import socket

# we need to import python modules from the $SUMO_HOME/tools directory
try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")),
        "tools"))  # tutorial in docs
    from sumolib import checkBinary
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME'"
        + "as the root directory of your sumo installation"
        + "(it should contain folders 'bin', 'tools' and 'docs')")

import traci
# the port used for communicating with your sumo instance
PORT = 8873

ANDROID_PORT = 5173
ANDROID_IP = "10.17.242.101"
# ANDROID_IP = "192.168.1.6"


def run():
    """execute the TraCI control loop"""
    traci.init(PORT)
    step = 0

    # Android
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ANDROID_IP, ANDROID_PORT))
    # data = sock.recv(4096)
    # print (data)

    # Lanes
    lanes = traci.lane.getIDList()
    rlane = lanes[0]
    for lane in lanes:
        ms = float(traci.lane.getMaxSpeed(lane))
        kmh = ms * 3.6
        print 'Lane ' + lane + ' ' + str(kmh) + 'km/h'
    # Lanes #

    # Vehicles
    # add(vehID, routeID, depart=-2, pos=0, speed=0, lane=0,
    #     typeID='DEFAULT_VEHTYPE')
    traci.vehicle.add("veh1", "route0", 5)
    # Vehicles #
    while traci.simulation.getMinExpectedNumber() > 0:
        ms = float(traci.lane.getLastStepMeanSpeed(rlane))
        kmh = ms * 3.6

        maxms = float(traci.lane.getMaxSpeed(rlane))
        maxkmh = maxms * 3.6
        print 'Lane ' + rlane + ' ' + str(int(kmh)) + 'km/h'
        bstring = '{"speedLimit":'\
            + str(int(maxkmh)) + ',"currentSpeed":'\
            + str(int(kmh)) + ',"avgLaneSpeed":'\
            + str(int(kmh))\
            + '}\n'
        try:
            sock.send(bstring)
            # data = sock.recv(4096)
        except:
            sock.close()

        traci.simulationStep()
        step += 1
    traci.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui",
                         action="store_true",
                         default=False,
                         help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line.
    # It will start sumo as a server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    sumoProcess = subprocess.Popen([
        sumoBinary, "-c", "data/scenario1.sumocfg", "--tripinfo-output",
        "tripinfo.xml", "--remote-port", str(PORT)], stdout=sys.stdout,
        stderr=sys.stderr)
    run()
    sumoProcess.wait()

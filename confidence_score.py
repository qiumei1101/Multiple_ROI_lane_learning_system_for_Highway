import csv
# header = ['x', 'y', 'w','h','frameid','cf']

def confidence_score(vehicles):
    with open('./collect_vehicles_2_csv_file', 'w') as f:
        writer = csv.writer(f)
        # writer.writerow(header)
        # print("vehicles",vehicles)
        conf_x = []
        conf_y = []
        conf_conf = []
        X = []

        for veh in vehicles:
            writer.writerow(veh)
            if veh[-1] > 0:
                conf_x.append(veh[0] + 1 / 2 * veh[2])
                conf_y.append(veh[1] + 1 / 2 * veh[3])
                conf_conf.append(veh[-1])
                X.append((veh[0] + 1 / 2 * veh[2], veh[1] + 1 / 2 * veh[3], veh[-1]))

    import numpy as np
    import matplotlib.pyplot as plt
    fig=plt.figure()
    ax = plt.axes(projection = '3d')
    fig = plt.figure(figsize=(9,6))
    ax = plt.axes(projection='3d')
    ax.scatter3D(conf_x,conf_y,conf_conf)
    #give labels
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('confidence score')

    plt.savefig("3d_conf.png",dpi=300)
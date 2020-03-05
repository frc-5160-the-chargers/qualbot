import json, requests
import matplotlib.pyplot as plt
import numpy as np

with open("zebraData.json") as readFile:
    zebraData = json.load(readFile)

xRaw = zebraData["alliances"]["blue"][2]["xs"]
yRaw = zebraData["alliances"]["blue"][2]["ys"]
timesRaw = zebraData["times"]

x, y, times = [], [], []
for i in range(len(xRaw)):
    if xRaw[i] != None:
        x.append(xRaw[i])
        y.append(yRaw[i])
        times.append(timesRaw[i])

heatmap, xedges, yedges = np.histogram2d(x, y, bins=64)
extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

plt.clf()
im = plt.imread("2019_game_field.jpeg")
plt.imshow(im, extent=[0, 54 + 1/12, 0, 26 + 7/12])
# plt.imshow(heatmap.T, extent=extent, origin='lower')
plt.scatter(x, y, c=times)

plt.xlim(left=0, right=54 + 1/12)
plt.ylim(bottom=0, top=26 + 7/12)

plt.ylabel("Height of Field")
plt.xlabel("Width of Field")
plt.title("Location of Robot " + zebraData["alliances"]["blue"][2]["team_key"] + " in match " + zebraData["key"])

plt.show()
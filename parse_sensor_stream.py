import json
import matplotlib.pyplot as plt


def readfile(file):
    lines = []
    with open(file, 'r') as f:
        lines = f.readlines()
    return lines


x_accel = []
y_accel = []
z_accel = []

lines = readfile("test.txt")
count = 0
x = []

for line in lines:
    jl = json.loads(line)
    x_accel.append(jl['gyr']['accel']['x'])
    y_accel.append(jl['gyr']['accel']['y'])
    z_accel.append(jl['gyr']['accel']['z'])
    count += 1
    x.append(count)

plt.subplot(3, 1, 1)
plt.plot(x, x_accel, '.-')
plt.title('A tale of 3 subplots')
plt.ylabel('X acceleration')

plt.subplot(3, 1, 2)
plt.plot(x, y_accel, '.-')
plt.xlabel('time (s)')
plt.ylabel('Y acceleration')

plt.subplot(3, 1, 3)
plt.plot(x, z_accel, '.-')
plt.xlabel('time (s)')
plt.ylabel('Z acceleration')

plt.show()
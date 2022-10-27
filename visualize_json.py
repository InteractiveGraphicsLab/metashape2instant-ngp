import sys
import json
import numpy as np
from matplotlib import pyplot as plt


if len(sys.argv) != 2:
  print('python visualize_json.py <path to transform.json>')
  exit()


# transform.jsonの読み込み
file_name = sys.argv[1]
with open(file_name) as f:
  transform = json.load(f)


# カメラの回転行列と座標の取得
cameras = transform['frames']


# 表示画面の初期化
fig = plt.figure(dpi=150)
ax = fig.add_subplot(111, projection='3d')
ax.set_title(file_name)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
plt.axis('off')
plt.tight_layout()


# カメラの座標
x = []
y = []
z = []
t = 1
for c in cameras:
  tm = np.array(c['transform_matrix'], dtype='float64')

  # カメラの座標を取得
  origin = np.array([tm[0, 3], tm[1, 3], tm[2, 3]], dtype='float64')
  cx, cy, cz = origin

  # カメラのx方向のベクトルを表示
  x.append(cx)
  dir_x = tm[:3, 0]
  dir_x = dir_x / np.linalg.norm(dir_x)
  u, v, w = origin + t * dir_x
  ax.plot([cx, u], [cy, v], [cz, w], '-', color='red', linewidth=0.5)

  # カメラのx方向のベクトルを表示
  y.append(cy)
  dir_y = -tm[:3, 1]
  dir_y = dir_y / np.linalg.norm(dir_y)
  u, v, w = origin + t * dir_y
  ax.plot([cx, u], [cy, v], [cz, w], '-', color='green', linewidth=0.5)

  # カメラのx方向のベクトルを表示
  z.append(cz)
  dir_z = -tm[:3, 2]
  u, v, w = origin + t * dir_z
  ax.plot([cx, u], [cy, v], [cz, w], '-', color='blue', linewidth=0.5)


# カメラの位置を表示
ax.scatter(x, y, z, color='black', linewidths=0.5)


# グラフを表示
plt.show()

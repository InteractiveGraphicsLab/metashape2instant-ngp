import sys
import numpy as np
import xml.etree.ElementTree as ET
from matplotlib import pyplot as plt


if len(sys.argv) != 2:
  print('python visualize_json.py <path to xml file>')
  exit()

# metashapeの出力ファイルの読み込み
file_name = sys.argv[1]
tree = ET.parse(file_name)
root = tree.getroot()


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
for c in root.iter('camera'):
  # transform matrixを取得
  transform = c.find('./transform')
  tm = np.array([float(t) for t in transform.text.split()], dtype='float64').reshape([4,4])

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

# カメラの座標をプロット
ax.scatter(x, y, z, color='black', linewidths=0.5)


# グラフを表示
plt.show()

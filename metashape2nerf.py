import argparse
import os
import cv2
import sys
import json
import math
import numpy as np
import xml.etree.ElementTree as ET


# 座標の重心を原点に合わせる
def recenter_frames(frames):
  # 全カメラ座標を取得
  coords = frames[:,:,3]

  # 重心の座標を求める
  g = np.mean(coords, axis=0)

  frames[:,:,3] -= g

  return frames


# aabb_scale 16固定?
def get_sensors(root):
  """
  センサーの情報を取得する
  args:
    root: XML ElementTreeのroot
  returns:
    sensors: センサーの情報が入った辞書の配列
              - id: str センサーのid
              - width, height: str
              - f, p1, p2: str
  """
  sensors = []
  for sens in root.iter('sensor') :
    # カメラのメタ情報を取得
    calibration = root.find('./chunk/sensors/sensor/calibration')
    
    # 画像のwidhtとheightを取得
    resolution = calibration.find('./resolution')
    width, height = float(resolution.attrib['width']), float(resolution.attrib['height'])
    
    # カメラのfocalを取得
    f = float(calibration.find('./f').text)

    # p1, p2(円周方向の歪み係数)を取得 (無ければば0に設定)
    p1, p2 = calibration.find('./p1'), calibration.find('./p2')
    p1 = float(p1.text) if p1 != None else 0.
    p2 = float(p2.text) if p2 != None else 0.

    # k1, k2(半径方向の歪み係数)を取得 (無ければ0に設定)
    k1, k2 = calibration.find('./k1'), calibration.find('./k2')
    k1 = float(k1.text) if k1 != None else 0.
    k2 = float(k2.text) if k2 != None else 0.

    # width, heightからangel_x, angle_yを導出
    angle_x = math.atan(width / (f * 2)) * 2
    angle_y = math.atan(height / (f * 2)) * 2

    # cx, cyを取得
    cx, cy = calibration.find('./cx'), calibration.find('./cy')
    cx = width/2. + float(cx.text) if cx != None else width/2.
    cy = height/2. + float(cy.text) if cy != None else height/2.

    sensors.append({'camera_angle_x': angle_x, 'camera_angle_y': angle_y,
                    'fl_x': f, 'fl_y': f,
                    'k1': k1, 'k2': k2,
                    'p1': p1, 'p2': p2,
                    'cx': cx, 'cy': cy,
                    'w': width, 'h': height,
                    'aabb_scale': 16})

  # 複数センサーはアウト?
  if len(sensors) != 1:
    return None

  return sensors[0]


def get_frames(xml_root, image_dir, is_recenter) :
  """
  XMLからカメラの情報を取得する
  args:
    root: XML ElementTreeのroot
  returns:
    cameras: カメラの情報が入った辞書の配列
              - id: str カメラのid
              - sensor_id: str 写真に使われているセンサーのid
              - label: str 写真のファイル名
              - transform: ndarray, [4,4], str 回転行列とカメラの座標
  """
  # 画像のファイル名のリスト
  image_list = os.listdir(image_dir)

  # 画像の情報のリストを作成
  frames = []
  transforms = np.empty([0,4,4], dtype=np.float64)
  for cam in xml_root.iter('camera') :
    # camに対応する画像ファイル名を取得
    label = cam.attrib['label']
    image_files = list(filter(lambda f: label == os.path.splitext(f)[0], image_list))
    if len(image_files) != 1:
      print('check image path')
      exit()
    image_path = os.path.join(image_dir, image_files[0])

    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

    # transform matrixを取得
    mat = cam.find('./transform')
    if mat == None:
      continue
    mat = np.array([float(n) for n in mat.text.split()]).reshape([4,4])
    # y軸を反転
    mat[:3, 1] *= -1.
    # z軸を反転
    mat[:3, 2] *= -1.
    
    transforms = np.append(transforms, np.array([mat], dtype=np.float64), axis=0)

    frames.append({'file_path': './images/' + image_files[0], 'sharpness': sharpness})

  if is_recenter:
    print('recenter')
    transforms = recenter_frames(transforms)

  for i, f in enumerate(frames):
    f['transform_matrix'] = transforms[i].tolist()

  return frames


def main(args) :
  camera_file = os.path.join(args.scene_dir, 'camera.xml')
  image_dir = os.path.join(args.scene_dir, 'images')

  # カメラファイルの拡張子をチェック
  if os.path.splitext(camera_file)[1] != '.xml':
    print('invalid file extension')
    return

  # XMLファイルをパース
  tree = ET.parse(camera_file)
  xml_root = tree.getroot()

  # カメラの情報を取得
  sensor = get_sensors(xml_root)
  # 複数カメラはアウト?
  if sensor == None:
    print('invalid number of sensors')
    return

  # 画像の情報を取得
  frames = get_frames(xml_root, image_dir, args.recenter)

  # transform.jsonの作成
  out = sensor
  out['frames'] = frames
  with open(os.path.join(args.scene_dir, 'transforms.json'), 'w') as f:
    json.dump(out, f, indent=2)


# 引数のパース
def parse_args():
  parser = argparse.ArgumentParser(exit_on_error=True)

  parser.add_argument('scene_dir', help='scene dir', type=str)
  parser.add_argument('--recenter', help='recenter or not', action='store_true')
  return parser.parse_args()


# ディレクトリの中で実行
if __name__ == '__main__':
  args = parse_args()
  main(args)

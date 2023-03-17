# metashape2instant-ngp
[**English**](./README.md)

本リポジトリは，以下のプログラムを含む
* metashape2nerf.py: フォトグラメトリソフト[Metashape](https://www.agisoft.com/)から取得できるXML形式のカメラ座標データを，[Instant NeRF](https://github.com/NVlabs/instant-ngp)に入力するJSON形式に成型するプログラム

* visualize_json.py: Instant NeRFに入力するJSON形式のカメラ座標データを可視化するプログラム

* visualize_xml.py: フォトグラメトリソフトMetashapeから得られる，XML形式のカメラ座標データを可視化するプログラム


## 実装環境
* Python 3.10.6
* opencv-python 4.6.0
* matplotlib 3.5.3

# metashape2nerf.py
## フォルダ構成
```
.
├─ metashape2nerf.py
└─ <scene_dir>
   ├─ camera.xml
   └─ images
      └─ カメラ座標を取得したすべての画像
```
## 引数
* `scene_dir`: Instant NeRFで再現したいシーンのディレクトリへのパス．このディレクトリの中にカメラ座標を取得したすべての画像が入っているディレクトリ`images`と，Metashapeで取得したカメラ座標が保存されたファイル`camera.xml`を入れる．
* `recenter`: Metashapeで取得したカメラ座標の重心を原点に合わせるかどうかのオプション．

## 出力
カメラ座標をXML形式からJSON形式に成型した，`transforms.json`を`scene_dir`に出力する

## 実行例
```
python metashape2nerf.py --recenter ./fern
```

# visualize_json.py / visualize_xml.py
## 引数
カメラ座標データが保存されているJSONファイル/XMLファイルへのパス

## 実行例
```
python visualize_json.py ship\transforms.json
```

![Figure](image/figure.png)


# 謝辞
本ソフトウエアはJSPS科研費 22H03710の助成を受けて開発されました。

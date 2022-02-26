from PIL import Image
import sys

import pyocr
import pyocr.builders
import cv2
import time

from isbn import search_book

# OCRの準備
tools = pyocr.get_available_tools()
if len(tools) == 0:
    print("No OCR tool found")
    sys.exit(1)
tool = tools[0]

# カメラを読み込む
capture = cv2.VideoCapture(0)

# OpneCVのQRコードのデコーダを定義（これを使ってQRコードを読み取る。）
qrd = cv2.QRCodeDetector()

# 初期化
fps = ""

while(True):
    t1 = time.perf_counter() # fpsを計算するため

    ret, frame = capture.read() # カメラから画像を読み取る
    cv2.putText(frame, fps, (10,30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2, cv2.LINE_AA) # fpsを表示
    cv2.imshow('frame',frame) # 画像を出力

    # OCRで文字を取得
    txt = tool.image_to_string(
        Image.fromarray(frame),
        lang="eng",
        builder=pyocr.builders.TextBuilder(tesseract_layout=6)
    )
    lst = txt.split("\n")

    for i in lst:
        if "ISBN" in i: # 読み取った文字の中から"ISBN"を探す
            i = i.split(" ")
            for k, j in enumerate(i):
                if "ISBN" in j:
                    isbn_index = k
                    break
            if i[k] == "ISBN":
                isbn = i[isbn_index+1]
            else:
                isbn = i[isbn_index]
            isbn = isbn.replace("ISBN", "").replace("-", "") # ISBNを数字だけにする
            res = search_book(isbn) # 本を探す
            if res:
                print(res) # 本が存在したら出力

    data, bbox, _ = qrd.detectAndDecode(frame) # QRコードを読み取る
    if data: # QRコードが読み取れたらGUIの学籍番号の欄を更新する
        print(data)

    # fpsを計算
    elapsedTime = time.perf_counter() - t1
    fps = f"{1/elapsedTime}FPS"


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # time.sleep(1)

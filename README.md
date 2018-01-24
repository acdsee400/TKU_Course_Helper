# Tensorflow 選課系統驗證碼判讀
* Requirements
    *  TensorFlow(CPU or GPU)
    *  Keras
    *  shutil
    *  opencv
    *  re
    *  h5py
    *  numpy
    *  PIL(Image)
    *  BeautifulSoup
*  本程式的作用
    *  此程式純粹為概念驗證使用，證明可以使用機器學習來進行驗證碼判斷
    *  還有 選課系統真爛
*  作用方式:
    *  使用requests函式庫自動抓取驗證碼
    *  在適度調整後將圖檔送進模型內進行驗證
    *  模型會自動回應此圖檔所對應的驗證碼

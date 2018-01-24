# Tensorflow 選課系統驗證碼判讀
* License: GNU GPLv3
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
* 免責聲明:
    * 你如果因為用了這個程式，導致你選不到課，這是你自己要承擔的結果。  
    這個程式開源出來的原因，就是希望有能力的人可以繼續維護下去，因原作者本人的程式寫的有夠爛，歡迎大家一起來讓它變得更好。

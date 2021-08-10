# MVC_singleCell

1. Set up environment according to requirements.txt
2. Run app.py

## computer vision part
computer vision part is based on https://github.com/andrewssobral/bgslibrary. Current method used here is Static background subtraction
computer vision pipeline:
* Median filter
* Static frame difference 
* Gaussian Blur
* floodfill
### environment setup
1. [for windows only] put pybgs-3.0.0.post2-py3.7-win-amd64.egg folder in the path where your interpreter can find. Mine is under "C:\ProgramData\Miniconda3\Lib\site-packages\pybgs-3.0.0.post2-py3.7-win-amd64.egg"
2. Otherwise, you can compile and build your own pybgs folder. This part is based on https://github.com/andrewssobral/bgslibrary. you need to build follow the bgslibrary document
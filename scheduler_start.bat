@ECHO OFF
dir >C:\Users\bono1\PycharmProjects\crafted_day\console.out
call "C:\Users\bono1\Anaconda3\Scripts\activate.bat" "C:\Users\bono1\Anaconda3"
cd /d C:\Users\bono1\PycharmProjects\crafted_day\
set PYTHONUNBUFFERED=1
set PYTHONPATH="C:\Users\bono1\PycharmProjects\crafted_day\Harvester;C:\Users\bono1\PycharmProjects\crafted_day;C:\Users\bono1\Anaconda3\python37.zip;C:\Users\bono1\Anaconda3\DLLs;C:\Users\bono1\Anaconda3\lib;C:\Users\bono1\Anaconda3;C:\Users\bono1\Anaconda3\lib\site-packages;C:\Users\bono1\Anaconda3\lib\site-packages\win32;C:\Users\bono1\Anaconda3\lib\site-packages\win32\lib;C:\Users\bono1\Anaconda3\lib\site-packages\Pythonwin"
"C:\Users\bono1\Anaconda3\python.exe" "C:/Users/bono1/PycharmProjects/crafted_day/Harvester/LocalDataSave.py"
pause
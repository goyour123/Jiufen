set build=.\build

if exist %build% rmdir /s /q %build%
mkdir %build%

python setup.py build>%build%\build.txt
copy mine.sqlite %build%\exe.win-amd64-3.5
cmd
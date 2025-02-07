# 환경설정 방법

새 PC에서 시작하기

```sh
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

가상 환경 변동시 반영하기

- (터미널 에서) 가상환경 활성화

```bash
.\.qtcreator\Python_3_12_5venv\Scripts\activate.ps1
```

패키지 정보 생성

```bash
pip freeze > requirements.txt
```

리소스 qrc 변경

```
pyside6-rcc .\src\resources\icons\_icons.qrc -o _icons_rc.py 
```

실행파일 생성

```
pyinstaller -w -F .\main.py
pyinstaller -w .\main.py
pyinstaller -F .\main.py
```

-w : 콘솔 비활성

-F : 단일파일 생성

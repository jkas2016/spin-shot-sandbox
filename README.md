# SpinShots : Dynamic Image Rotation & GIF Maker

1.	이미지 불러오기: Pillow(PIL)를 이용해 이미지를 RGBA 모드로 불러옵니다.
2.	회전 및 중앙 정렬: 특정 각도(angle)로 이미지를 회전시킨 뒤, 주어진 캔버스 크기 내에서 중앙에 맞춰 붙여 넣습니다.
3.	애니메이션 프레임 생성: 여러 각도로 회전된 이미지를 프레임 리스트로 생성합니다.
4.	GIF 저장: 생성된 프레임 리스트를 이용해 GIF 파일로 저장합니다.

## Learn play ground

[learn-spin-shot.ipynb](learn-spin-shot.ipynb)

## Build

```bash
# macOS에서 실행 파일 빌드
pyinstaller --onefile --windowed \
    --icon=icon.icns \
    src/spinshots_app.py

# Windows에서 실행 파일 빌드
pyinstaller --onefile --windowed \
    --icon=icon.ico \
    src/spinshots_app.py
```

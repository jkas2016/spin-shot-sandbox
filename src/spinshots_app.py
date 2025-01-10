import sys
import os
import tempfile
from PIL import Image
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QFileDialog, QLineEdit
)
from PyQt6.QtGui import QPixmap, QMovie
from PyQt6.QtCore import Qt, QSize
from datetime import datetime
import random


def create_rotated_frames(original_image: Image, canvas_size=(550, 550), angle_step=60):
    frames = []
    for angle in range(0, 360, angle_step):
        rotated_image = original_image.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
        canvas = Image.new("RGBA", canvas_size, (255, 255, 255, 0))

        x_offset = (canvas_size[0] - rotated_image.width) // 2
        y_offset = (canvas_size[1] - rotated_image.height) // 2
        canvas.paste(rotated_image, (x_offset, y_offset), rotated_image)

        frames.append(canvas)
    return frames


class SpinShotsPlayground(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SpinShots Playground")

        # GIF 임시 저장 경로 (사용 후 다운로드 전까지 임시로 보관)
        self.temp_gif_path = os.path.join(tempfile.gettempdir(), "spinshots_temp.gif")

        # 원본 PIL 이미지 객체를 저장할 변수
        self.original_image = None

        # 레이아웃 구성
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        left_panel = QVBoxLayout()
        main_layout.addLayout(left_panel)

        # 가로/세로 크기 입력 필드
        size_layout = QHBoxLayout()
        self.label_width = QLabel("가로(px):")
        self.width_edit = QLineEdit("550")
        self.label_height = QLabel("세로(px):")
        self.height_edit = QLineEdit("550")

        size_layout.addWidget(self.label_width)
        size_layout.addWidget(self.width_edit)
        size_layout.addWidget(self.label_height)
        size_layout.addWidget(self.height_edit)

        left_panel.addLayout(size_layout)

        right_panel = QVBoxLayout()
        main_layout.addLayout(right_panel)

        # 1) [이미지 불러오기] 버튼
        self.btn_load_image = QPushButton("이미지 불러오기")
        self.btn_load_image.clicked.connect(self.load_image) # type: ignore
        left_panel.addWidget(self.btn_load_image)

        # 2) 이미지 미리보기용 라벨
        self.label_image_preview = QLabel("이미지 미리보기")
        self.label_image_preview.setFixedSize(400, 400)
        self.label_image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_image_preview.setStyleSheet("border: 1px solid gray;")
        left_panel.addWidget(self.label_image_preview)

        # 3) "GIF 만들기" 버튼
        self.btn_make_gif = QPushButton("GIF 만들기")
        self.btn_make_gif.clicked.connect(self.make_gif) # type: ignore
        left_panel.addWidget(self.btn_make_gif)

        # 4) GIF 미리보기용 라벨
        self.label_gif_preview = QLabel("GIF 미리보기")
        self.label_gif_preview.setFixedSize(500, 500)
        self.label_gif_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_gif_preview.setStyleSheet("border: 1px solid gray;")
        right_panel.addWidget(self.label_gif_preview)

        # 5) "GIF 다운로드" 버튼
        self.btn_download_gif = QPushButton("GIF 다운로드")
        self.btn_download_gif.clicked.connect(self.download_gif) # type: ignore
        right_panel.addWidget(self.btn_download_gif)

    def load_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "이미지 선택",
            "",
            "이미지 파일 (*.png *.jpg *.jpeg *.bmp *.gif);;모든 파일 (*.*)"
        )

        if file_path:
            # PIL 이미지로 로드 & RGBA 변환
            self.original_image = Image.open(file_path).convert("RGBA")

            # QPixmap으로 라벨에 미리보기
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(
                self.label_image_preview.width(),
                self.label_image_preview.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.label_image_preview.setPixmap(pixmap)

    def make_gif(self):
        if not self.original_image:
            self.label_gif_preview.setText("먼저 이미지를 선택하세요!")
            return

        # 사용자가 입력한 너비/높이 읽기
        try:
            w = int(self.width_edit.text())
            h = int(self.height_edit.text())
            canvas_size = (w, h)
        except ValueError:
            self.label_gif_preview.setText("올바른 숫자를 입력하세요!")
            return

        # 회전 프레임 생성
        frames = create_rotated_frames(self.original_image, canvas_size=canvas_size)

        # GIF로 저장 (temp 파일에)
        frames[0].save(
            self.temp_gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0,
            disposal=2
        )

        # QMovie를 이용하여 GIF 미리보기
        movie = QMovie(self.temp_gif_path)
        # 라벨 크기에 맞춰 스케일링
        movie.setScaledSize(QSize(self.label_gif_preview.width(), self.label_gif_preview.height()))

        self.label_gif_preview.setMovie(movie)
        movie.start()

    def download_gif(self):
        """
        만들어진 GIF를 사용자 지정 경로로 저장한다.
        기본 파일명: "20230101_103045_1234.gif" (연월일_시분초_랜덤4자리)
        """
        if not os.path.exists(self.temp_gif_path):
            self.label_gif_preview.setText("다운로드할 GIF가 없습니다!")
            return

        # 날짜 + 랜덤 숫자를 조합한 기본 파일명 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_part = random.randint(1000, 9999)
        default_filename = f"{timestamp}_{random_part}.gif"

        # QFileDialog에 기본 경로(현재 디렉토리 + 파일명) 전달
        suggested_path = os.path.join(os.getcwd(), default_filename)

        save_dialog = QFileDialog()
        save_path, _ = save_dialog.getSaveFileName(
            self,
            "GIF 저장",
            suggested_path,  # 세 번째 인자: 기본 파일명 (경로 포함)
            "GIF 파일 (*.gif)"  # 네 번째 인자: 파일 형식 필터
        )

        if save_path:
            # temp 파일 -> 지정한 경로로 복사
            with open(self.temp_gif_path, "rb") as src, open(save_path, "wb") as dst:
                dst.write(src.read())
            self.label_gif_preview.setText("GIF 저장 완료!")


def main():
    app = QApplication(sys.argv)
    window = SpinShotsPlayground()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
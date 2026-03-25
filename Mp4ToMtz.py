import sys
import cv2
import os
import zipfile
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QLabel
from PyQt5.QtCore import QThread, pyqtSignal

class VideoWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path

    def run(self):
        frames_folder = "frames"
        part0_folder = "part0"

        os.makedirs(frames_folder, exist_ok=True)
        os.makedirs(part0_folder, exist_ok=True)

        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            self.finished.emit("ERROR")
            return

        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 24
        count = 0
        max_frames = fps * 3  # sadece ilk 3 saniye

        while count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            frame_path = os.path.join(frames_folder, f"{count:04d}.png")
            cv2.imwrite(frame_path, frame)
            count += 1

        cap.release()

        for file in os.listdir(frames_folder):
            shutil.move(os.path.join(frames_folder, file), os.path.join(part0_folder, file))

        desc_text = f"720 1280 {fps}\np 0 0 part0\n"
        with open("desc.txt", "w") as f:
            f.write(desc_text)

        boot_zip = os.path.join(os.getcwd(), "bootanimation.zip")  # tam yol kullan
        with zipfile.ZipFile(boot_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write("desc.txt", "desc.txt")
            for file in os.listdir(part0_folder):
                zipf.write(os.path.join(part0_folder, file), f"part0/{file}")

        shutil.rmtree(frames_folder)
        shutil.rmtree(part0_folder)
        os.remove("desc.txt")

        self.finished.emit(boot_zip)

class VideoToMtzApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Boot Animation MTZ Creator")
        self.setGeometry(100, 100, 400, 220)

        layout = QVBoxLayout()

        self.label = QLabel("Video seç", self)
        layout.addWidget(self.label)

        self.import_btn = QPushButton("İçe Aktar", self)
        self.import_btn.clicked.connect(self.import_video)
        layout.addWidget(self.import_btn)

        self.export_zip_btn = QPushButton("ZIP Olarak Kaydet", self)
        self.export_zip_btn.setEnabled(False)
        self.export_zip_btn.clicked.connect(self.export_zip)
        layout.addWidget(self.export_zip_btn)

        self.export_mtz_btn = QPushButton("MTZ Olarak Kaydet", self)
        self.export_mtz_btn.setEnabled(False)
        self.export_mtz_btn.clicked.connect(self.export_mtz)
        layout.addWidget(self.export_mtz_btn)

        self.setLayout(layout)
        self.video_path = ""
        self.boot_zip_path = ""

    def import_video(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Video Seç", "", "Video Files (*.mp4 *.avi *.mov)")
        if file_name:
            self.video_path = file_name
            self.label.setText("İşleniyor...")
            self.process_video()

    def process_video(self):
        self.worker = VideoWorker(self.video_path)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, result):
        if result == "ERROR":
            self.label.setText("Hata oluştu")
        else:
            self.boot_zip_path = result
            self.label.setText("Bootanimation hazır!")
            self.export_zip_btn.setEnabled(True)
            self.export_mtz_btn.setEnabled(True)

    def export_zip(self):
        if not self.boot_zip_path or not os.path.exists(self.boot_zip_path):
            self.label.setText("Hata: ZIP dosyası bulunamadı!")
            return
        save_path, _ = QFileDialog.getSaveFileName(self, "Kaydet", "bootanimation.zip", "ZIP Files (*.zip)")
        if save_path:
            shutil.copy(self.boot_zip_path, save_path)  # copy ile güvenli taşıma
            self.label.setText("ZIP olarak kaydedildi!")

    def export_mtz(self):
        if not self.boot_zip_path or not os.path.exists(self.boot_zip_path):
            self.label.setText("Hata: ZIP dosyası bulunamadı!")
            return
        save_path, _ = QFileDialog.getSaveFileName(self, "Kaydet", "theme.mtz", "MTZ Files (*.mtz)")
        if save_path:
            os.makedirs("mtz_temp/boots", exist_ok=True)
            shutil.copy(self.boot_zip_path, "mtz_temp/boots/bootanimation.zip")
            with open("mtz_temp/description.xml", "w") as f:
                f.write("""<MIUI_Theme>
<title>Boot Animation</title>
<author>You</author>
<version>1.0</version>
</MIUI_Theme>""")
            with zipfile.ZipFile(save_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk("mtz_temp"):
                    for file in files:
                        full = os.path.join(root, file)
                        zipf.write(full, os.path.relpath(full, "mtz_temp"))
            shutil.rmtree("mtz_temp")
            self.label.setText("MTZ olarak kaydedildi!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = VideoToMtzApp()
    ex.show()
    sys.exit(app.exec_())

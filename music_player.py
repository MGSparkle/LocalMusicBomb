import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QWidget, 
                             QFileDialog, QLabel, QSlider, QListWidget)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QIcon, QFont

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

STYLE_SHEET = """
QMainWindow { background-color: #121212; }
QLabel { color: #FFFFFF; font-size: 16px; font-family: "Microsoft YaHei"; }
QListWidget { background-color: #1E1E1E; border: none; border-radius: 8px; color: #B3B3B3; outline: none; }
QListWidget::item { padding: 10px; border-radius: 5px; }
QListWidget::item:selected { background-color: #333333; color: #1DB954; }

/* 进度条 */
QSlider::groove:horizontal { border: 1px solid #333; height: 4px; background: #535353; border-radius: 2px; }
QSlider::handle:horizontal { background: #1DB954; width: 12px; height: 12px; margin: -5px 0; border-radius: 6px; }

/* 按钮样式 */
QPushButton { background-color: #1DB954; color: white; border-radius: 20px; padding: 10px; font-weight: bold; }
QPushButton:hover { background-color: #1ED760; }

#MainBtn { font-size: 18px; border-radius: 25px; min-width: 120px; min-height: 50px; }
#SideBtn { background-color: transparent; border: 2px solid #535353; color: #FFFFFF; border-radius: 15px; }
#SideBtn:hover { border-color: #FFFFFF; }
"""

class SimplePlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("本地音爆 - 极简版")
        self.setFixedSize(500, 450)

        self.mediaPlayer = QMediaPlayer(self)
        self.playlist_data = []
        
        self.init_ui()
        self.setStyleSheet(STYLE_SHEET)

        # 信号绑定
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)
        self.mediaPlayer.stateChanged.connect(self.update_ui_state)

    def init_ui(self):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(30, 20, 30, 30)

        # 1. 歌曲标题
        self.title_label = QLabel("暂无播放歌曲")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # 2. 歌曲列表
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.play_selected)
        layout.addWidget(self.list_widget)

        # 3. 播放速度滑块
        speed_box = QHBoxLayout()
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(20, 400) # 0.5x - 2.0x
        self.speed_slider.setValue(100)
        self.speed_slider.sliderReleased.connect(self.update_playback_rate)
        
        self.speed_text = QLabel("1.0x")
        self.speed_text.setFixedWidth(40)
        
        speed_box.addWidget(QLabel("变速变调"))
        speed_box.addWidget(self.speed_slider)
        speed_box.addWidget(self.speed_text)
        layout.addLayout(speed_box)

        # 4. 进度条
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.sliderMoved.connect(self.set_position)
        layout.addWidget(self.progress_slider)

        # 5. 控制按钮
        control_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("添加歌曲")
        self.add_btn.setObjectName("SideBtn")
        self.add_btn.clicked.connect(self.add_files)
        
        self.play_pause_btn = QPushButton("播放")
        self.play_pause_btn.setObjectName("MainBtn")
        self.play_pause_btn.clicked.connect(self.toggle_play)

        control_layout.addWidget(self.add_btn)
        control_layout.addStretch()
        control_layout.addWidget(self.play_pause_btn)
        control_layout.addStretch()
        
        # 为了左右视觉平衡，右边加个空白占位
        dummy = QWidget()
        dummy.setFixedWidth(80)
        control_layout.addWidget(dummy)

        layout.addLayout(control_layout)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择音乐", "", "Audio Files (*.mp3 *.wav)")
        if files:
            for f in files:
                self.list_widget.addItem(os.path.basename(f))
                self.playlist_data.append(f)

    def play_selected(self):
        row = self.list_widget.currentRow()
        if row != -1:
            path = self.playlist_data[row]
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
            self.title_label.setText(os.path.basename(path))
            self.update_playback_rate() # 播放时应用当前选定的速度
            self.mediaPlayer.play()

    def toggle_play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            # 如果没选歌就点播放，默认放第一首
            if self.mediaPlayer.mediaStatus() == QMediaPlayer.NoMedia:
                if self.list_widget.count() > 0:
                    self.list_widget.setCurrentRow(0)
                    self.play_selected()
            else:
                self.mediaPlayer.play()

    def update_ui_state(self, state):
        """核心：播放/暂停文字自动切换"""
        self.play_pause_btn.setText("暂停" if state == QMediaPlayer.PlayingState else "播放")

    def update_playback_rate(self):
        rate = self.speed_slider.value() / 100.0
        self.speed_text.setText(f"{rate:.1f}x")
        self.mediaPlayer.setPlaybackRate(rate)

    def position_changed(self, pos):
        if not self.progress_slider.isSliderDown():
            self.progress_slider.setValue(pos)

    def duration_changed(self, dur):
        self.progress_slider.setRange(0, dur)

    def set_position(self, pos):
        self.mediaPlayer.setPosition(pos)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = SimplePlayer()
    player.show()
    sys.exit(app.exec_())
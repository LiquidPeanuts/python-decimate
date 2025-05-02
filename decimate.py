import sys
import trimesh
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLabel, QSlider, QFileDialog, QMessageBox, QHBoxLayout, QLineEdit
)
from PyQt5.QtCore import Qt

class DecimateGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('STL Decimator')
        self.resize(400, 200)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel('Reduction: 50%')

        # Slider setup (we’ll scale it 0–990 internally for 1-decimal float)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(10)   # 1.0%
        self.slider.setMaximum(990)  # 99.0%
        self.slider.setValue(500)    # 50.0%
        self.slider.valueChanged.connect(self.update_from_slider)

        # Input box setup
        self.input_box = QLineEdit()
        self.input_box.setFixedWidth(60)
        self.input_box.setText('50.0')
        self.input_box.editingFinished.connect(self.update_from_input)

        # Horizontal layout for slider + input box
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.input_box)

        # Buttons
        self.load_button = QPushButton('Load STL')
        self.load_button.clicked.connect(self.load_stl)

        self.save_button = QPushButton('Save Decimated STL')
        self.save_button.clicked.connect(self.save_stl)
        self.save_button.setEnabled(False)

        # Assemble layout
        self.layout.addWidget(self.label)
        self.layout.addLayout(slider_layout)
        self.layout.addWidget(self.load_button)
        self.layout.addWidget(self.save_button)

        self.mesh = None

    def update_from_slider(self, value):
        percent = value / 10  # convert to float percent
        self.label.setText(f'Reduction: {percent:.1f}%')
        self.input_box.setText(f'{percent:.1f}')

    def update_from_input(self):
        try:
            value = float(self.input_box.text())
            value = max(0.0000000001, min(99.999999999, value))  # clamp between 1.0 and 99.0
            self.slider.setValue(float(value * 10))  # convert to slider scale
        except ValueError:
            QMessageBox.warning(self, 'Invalid Input', 'Please enter a number between 1.0 and 99.0.')
            current_value = self.slider.value() / 10
            self.input_box.setText(f'{current_value:.1f}')

    def load_stl(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open STL File', '', 'STL Files (*.stl)')
        if file_name:
            self.mesh = trimesh.load(file_name)
            if not isinstance(self.mesh, trimesh.Trimesh):
                QMessageBox.warning(self, 'Error', 'Failed to load STL mesh.')
                self.mesh = None
                return
            QMessageBox.information(self, 'Loaded', f'Loaded {file_name}')
            self.save_button.setEnabled(True)

    def save_stl(self):
        if self.mesh is None:
            return

        reduction_fraction = self.slider.value() / 1000  # scale to 0–1
        current_faces = len(self.mesh.faces)
        target_faces = max(4, int(current_faces * (1 - reduction_fraction)))

        simplified = self.mesh.simplify_quadric_decimation(face_count=target_faces)

        save_file, _ = QFileDialog.getSaveFileName(self, 'Save Decimated STL', '', 'STL Files (*.stl)')
        if save_file:
            simplified.export(save_file)
            QMessageBox.information(self, 'Saved', f'Saved decimated mesh to {save_file}')

def main():
    app = QApplication(sys.argv)
    window = DecimateGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

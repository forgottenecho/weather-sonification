import sys
from PySide6.QtWidgets import QApplication, QWidget, QComboBox

class MyMainForm(QWidget):
    def __init__(self):
        super().__init__()

if __name__ == '__main__':
    # creat the qt app
    app = QApplication(sys.argv)

    # create form and display it
    widget = MyMainForm()
    widget.resize(800, 600)
    widget.show()

    # run the main loop
    sys.exit(app.exec())

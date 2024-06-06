import logging
import subprocess
import time
import main
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon, QPixmap, QImage
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QCheckBox, QLabel, QLineEdit, QFileDialog, QDialog, QVBoxLayout, QRadioButton, QTextBrowser, QWidget, QFrame

class Window(QMainWindow):
    def closeEvent(self, event):
        #logging.info('Thanks for using Festival Charter!')
        #time.sleep(0.1)
        event.accept()

    def __init__(self):
        super().__init__()
        
        self.setWindowTitle(f"FunkinFF")
        wid = 750
        hei = 650

        self.setFixedSize(QSize(wid, hei))
        self.setMinimumSize(QSize(wid, hei))
        self.setMaximumSize(QSize(wid, hei))

        _currentY = 20

        self.pathlabel = QLabel("Paths", self)
        self.pathlabel.move(20, _currentY)
        self.pathlabel.resize(35, 30)

        self.lineseppath = QFrame(self)
        self.lineseppath.setFrameShape(QFrame.Shape.HLine)
        self.lineseppath.setFrameShadow(QFrame.Shadow.Sunken)
        self.lineseppath.move(self.pathlabel.x() + self.pathlabel.width() + 20, _currentY)
        self.lineseppath.resize(wid - (self.pathlabel.x() + 40), 30)

        _currentY += 40

        self.findbase = QLabel("Path to Base Game Root", self)
        self.findbase.move(20, _currentY)
        self.findbase.resize(220, 30)

        self.findbasebtn = QPushButton("Locate...", self)
        self.findbasebtn.setToolTip("Open File Dialog")
        self.findbasebtn.move((self.width() - 20) - self.findbasebtn.width(), _currentY)
        self.findbasebtn.clicked.connect(self.findBaseDir)

        self.baseLineEdit = QLineEdit('', self)
        self.baseLineEdit.move((self.findbasebtn.x() - 20) - 400, _currentY)
        self.baseLineEdit.resize(400, 30)

        _currentY += 40

        self.stemslabel = QLabel("Stems", self)
        self.stemslabel.move(20, _currentY)
        self.stemslabel.resize(35, 30)

        self.linesepstems = QFrame(self)
        self.linesepstems.setFrameShape(QFrame.Shape.HLine)
        self.linesepstems.setFrameShadow(QFrame.Shadow.Sunken)
        self.linesepstems.move(self.stemslabel.x() + self.stemslabel.width() + 20, _currentY)
        self.linesepstems.resize(wid - (self.linesepstems.x() - 600), 30)

        _currentY += 40

        self.backingsLabel = QLabel("Backing ogg (Required)", self)
        self.backingsLabel.move(20, _currentY)
        self.backingsLabel.resize(220, 30)

        self.findbkngbtn = QPushButton("Locate ogg...", self)
        self.findbkngbtn.setToolTip("Open File Dialog")
        self.findbkngbtn.move((self.width() - 20) - self.findbkngbtn.width(), _currentY)
        self.findbkngbtn.clicked.connect(self.findBacking)

        self.bkngLineEdit = QLineEdit('', self)
        self.bkngLineEdit.move((self.findbkngbtn.x() - 20) - 400, _currentY)
        self.bkngLineEdit.resize(400, 30)

        _currentY += 40

        self.drumsLabel = QLabel("Drums ogg", self)
        self.drumsLabel.move(20, _currentY)
        self.drumsLabel.resize(220, 30)

        self.finddrmsbtn = QPushButton("Locate ogg...", self)
        self.finddrmsbtn.setToolTip("Open File Dialog")
        self.finddrmsbtn.move((self.width() - 20) - self.finddrmsbtn.width(), _currentY)
        self.finddrmsbtn.clicked.connect(self.findDrums)

        self.drmsLineEdit = QLineEdit('', self)
        self.drmsLineEdit.move((self.finddrmsbtn.x() - 20) - 400, _currentY)
        self.drmsLineEdit.resize(400, 30)

        _currentY += 40

        self.bassLabel = QLabel("Bass ogg", self)
        self.bassLabel.move(20, _currentY)
        self.bassLabel.resize(220, 30)

        self.findbssbtn = QPushButton("Locate ogg...", self)
        self.findbssbtn.setToolTip("Open File Dialog")
        self.findbssbtn.move((self.width() - 20) - self.findbssbtn.width(), _currentY)
        self.findbssbtn.clicked.connect(self.findBass)

        self.bssLineEdit = QLineEdit('', self)
        self.bssLineEdit.move((self.findbssbtn.x() - 20) - 400, _currentY)
        self.bssLineEdit.resize(400, 30)

        _currentY += 40

        self.leadLabel = QLabel("Lead ogg", self)
        self.leadLabel.move(20, _currentY)
        self.leadLabel.resize(220, 30)

        self.findldbutn = QPushButton("Locate ogg...", self)
        self.findldbutn.setToolTip("Open File Dialog")
        self.findldbutn.move((self.width() - 20) - self.findldbutn.width(), _currentY)
        self.findldbutn.clicked.connect(self.findlead)

        self.leadlineedit = QLineEdit('', self)
        self.leadlineedit.move((self.findldbutn.x() - 20) - 400, _currentY)
        self.leadlineedit.resize(400, 30)

        _currentY += 40

        self.vclsLabel = QLabel("Vocals ogg", self)
        self.vclsLabel.move(20, _currentY)
        self.vclsLabel.resize(220, 30)

        self.findvclsbutn = QPushButton("Locate ogg...", self)
        self.findvclsbutn.setToolTip("Open File Dialog")
        self.findvclsbutn.move((self.width() - 20) - self.findvclsbutn.width(), _currentY)
        self.findvclsbutn.clicked.connect(self.findvoc)

        self.vocllineedit = QLineEdit('', self)
        self.vocllineedit.move((self.findvclsbutn.x() - 20) - 400, _currentY)
        self.vocllineedit.resize(400, 30)

        _currentY += 40

        self.midiseplabel = QLabel("Charts", self)
        self.midiseplabel.move(20, _currentY)
        self.midiseplabel.resize(35, 30)

        self.linesepmidi = QFrame(self)
        self.linesepmidi.setFrameShape(QFrame.Shape.HLine)
        self.linesepmidi.setFrameShadow(QFrame.Shadow.Sunken)
        self.linesepmidi.move(self.midiseplabel.x() + self.midiseplabel.width() + 20, _currentY)
        self.linesepmidi.resize(wid - (self.midiseplabel.x() + 20), 30)

        _currentY += 40

        self.midilabel = QLabel("MIDI File", self)
        self.midilabel.move(20, _currentY)
        self.midilabel.resize(220, 30)

        self.findmidibtn = QPushButton("Locate midi...", self)
        self.findmidibtn.setToolTip("Open File Dialog")
        self.findmidibtn.move((self.width() - 20) - self.findmidibtn.width(), _currentY)
        self.findmidibtn.clicked.connect(self.findmid)

        self.midilineedit = QLineEdit('', self)
        self.midilineedit.move((self.findmidibtn.x() - 20) - 400, _currentY)
        self.midilineedit.resize(400, 30)

        self.convert = QPushButton("Make .fnfc", self)
        self.convert.move((self.width() - 20) - self.convert.width(), (self.height() - 20) - self.convert.height())
        self.convert.clicked.connect(self.convertCallback)

        self.lastFnfc = None

        self.charteditorbtn = QPushButton("Open .fnfc in Chart Editor", self)
        self.charteditorbtn.resize(200, 30)
        self.charteditorbtn.move((self.width() - 20) - (self.convert.width() + 20 + self.charteditorbtn.width()), (self.height() - 20) - self.convert.height())
        self.charteditorbtn.clicked.connect(self.openFnfc)

    def findBaseDir(self):
        baseGameFolder = QFileDialog.getExistingDirectory(self, "Select Base Game Root")
        if len(baseGameFolder) > 0:
            self.baseLineEdit.setText(baseGameFolder)

    def findBacking(self):
        oggFile = QFileDialog.getOpenFileName(self, "Select Audio File", "", "*.ogg")
        if len(oggFile[0]) > 0:
            self.bkngLineEdit.setText(oggFile[0])

    def findDrums(self):
        oggFile = QFileDialog.getOpenFileName(self, "Select Audio File", "", "*.ogg")
        if len(oggFile[0]) > 0:
            self.drmsLineEdit.setText(oggFile[0])

    def findBass(self):
        oggFile = QFileDialog.getOpenFileName(self, "Select Audio File", "", "*.ogg")
        if len(oggFile[0]) > 0:
            self.bssLineEdit.setText(oggFile[0])

    def findlead(self):
        oggFile = QFileDialog.getOpenFileName(self, "Select Audio File", "", "*.ogg")
        if len(oggFile[0]) > 0:
            self.leadlineedit.setText(oggFile[0])

    def findvoc(self):
        oggFile = QFileDialog.getOpenFileName(self, "Select Audio File", "", "*.ogg")
        if len(oggFile[0]) > 0:
            self.vocllineedit.setText(oggFile[0])

    def findmid(self):
        midFile = QFileDialog.getOpenFileName(self, "Select MIDI File", "", "*.midi, *.mid")
        if len(midFile[0]) > 0:
            self.midilineedit.setText(midFile[0])

    def convertCallback(self):
        self.lastFnfc = main.makeFnfcFile(
             self.bkngLineEdit.text(),
             self.vocllineedit.text(),
             self.drmsLineEdit.text(),
             self.leadlineedit.text(),
             self.bssLineEdit.text(),
             f'chart_{int(time.time())}',
             self.baseLineEdit.text(),
             self.midilineedit.text()
        )

    def openFnfc(self):
        if self.lastFnfc != None:
            args = ['Funkin']
            args += ['--chart', self.lastFnfc]

            print(f'Attempting to subprocess with args: {args} at dir {self.baseLineEdit.text()}')

            try:
                 subprocess.run(args, cwd=f'{self.baseLineEdit.text()}/', shell=True)
            except Exception as e:
                 print(e)
        else:
             print('Not valid for opening!')

app = QApplication([])
window = Window()

def init():
	logging.info('Initiating window')

	window.show()

	app.exec()
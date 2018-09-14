#!/usr/bin/env python3

import sys
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QDesktopWidget, QMainWindow, QAction, QGridLayout, \
	QTextEdit, QLabel, QVBoxLayout, QHBoxLayout


class Toaster(QMainWindow):

	def __init__(self):
		# noinspection PyArgumentList
		super().__init__()
		self.status_bar = self.statusBar()
		self.window()

	def window(self):
		grid = QGridLayout()
		grid.setSpacing(10)
		# Two columns: left fixed, right can expand
		grid.setColumnStretch(0, 0)
		grid.setColumnStretch(1, 1)
		# noinspection PyArgumentList
		widg = QWidget()
		widg.setLayout(grid)
		self.central(grid)
		self.setCentralWidget(widg)

	def central(self, grid):
		self.set_status('Ready to toast')
		self.resize(250, 150)
		self.center()
		self.setWindowTitle('Crispy Flash Drives')

		toast_btn = self.gib_button_pls('Toast!')
		cancel_btn = self.gib_button_pls('Cancel')

		# Label and selection area (first row)
		grid.addWidget(QLabel('Distribution'), 1, 0)
		grid.addWidget(QTextEdit(), 1, 1)

		# Label and selection area (second row)
		grid.addWidget(QLabel('Flash drive'), 2, 0)
		grid.addWidget(QTextEdit(), 2, 1)

		# noinspection PyArgumentList
		button_area = QWidget()
		button_grid = QHBoxLayout()
		button_area.setLayout(button_grid)
		button_grid.addStretch()  # This is done twice to center buttons horizontally
		button_grid.addWidget(toast_btn)
		button_grid.addWidget(cancel_btn)
		button_grid.addStretch()

		grid.addWidget(button_area, 3, 0, 1, 2) # span both columns (and one row)

		self.show()

	# def closeEvent(self, event):
	# 	event.ignore()

	def center(self):
		main_window = self.frameGeometry()
		main_window.moveCenter(QDesktopWidget().availableGeometry().center())
		self.move(main_window.topLeft())

	def set_status(self, status: str):
		self.status_bar.showMessage(status)

	def gib_button_pls(self, text: str, tooltip=''):
		button = QPushButton(text, self)
		if len(tooltip) > 0:
			button.setToolTip(tooltip)
		button.resize(button.sizeHint())
		action = QAction('Do things', self)
		button.addAction(action)
		return button


def diff(start: QDateTime):
	now = QDateTime()
	now.currentDateTime().toSecsSinceEpoch()
	# print(time.toString(Qt.DefaultLocaleLongDate))
	return now - start.toSecsSinceEpoch()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = Toaster()
	sys.exit(app.exec_())

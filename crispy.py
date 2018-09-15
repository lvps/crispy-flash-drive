#!/usr/bin/env python3

import sys

import json
import subprocess
# noinspection PyUnresolvedReferences
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QDateTime, QAbstractListModel
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QDesktopWidget, QMainWindow, QGridLayout, QLabel, \
	QHBoxLayout, QListView


class Toaster(QMainWindow):

	def __init__(self):
		# noinspection PyArgumentList
		super().__init__()
		self.status_bar = self.statusBar()
		self.distro_list = DistroList()
		self.drives_list = DriveList()
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
		self.resize(300, 400)
		self.center()
		self.setWindowTitle('Crispy Flash Drives')

		toast_btn = self.make_button('Toast!', self.toast_clicked)
		cancel_btn = self.make_button('Cancel', self.cancel_clicked)

		# Label and selection area (first row)
		distro_list_view = QListView()
		distro_list_view.uniformItemSizes = True
		distro_list_view.setModel(self.distro_list)
		grid.addWidget(QLabel('Distribution'), 1, 0)
		grid.addWidget(distro_list_view, 1, 1)

		# Label and selection area (second row)
		drives_list_view = QListView()
		drives_list_view.uniformItemSizes = True
		drives_list_view.setModel(self.drives_list)
		grid.addWidget(QLabel('Flash drive'), 2, 0)
		grid.addWidget(drives_list_view, 2, 1)

		# noinspection PyArgumentList
		button_area = QWidget()
		button_grid = QHBoxLayout()
		button_area.setLayout(button_grid)
		button_grid.addStretch()  # This is done twice to center buttons horizontally
		# noinspection PyArgumentList
		button_grid.addWidget(toast_btn)
		# noinspection PyArgumentList
		button_grid.addWidget(cancel_btn)
		button_grid.addStretch()

		grid.addWidget(button_area, 3, 0, 1, 2)  # span both columns (and one row)

		self.show()

	# def closeEvent(self, event):
	# 	event.ignore()

	def center(self):
		main_window = self.frameGeometry()
		main_window.moveCenter(QDesktopWidget().availableGeometry().center())
		self.move(main_window.topLeft())

	def set_status(self, status: str):
		self.status_bar.showMessage(status)

	def make_button(self, text: str, action, tooltip=''):
		button = QPushButton(text, self)
		if len(tooltip) > 0:
			button.setToolTip(tooltip)
		button.resize(button.sizeHint())
		# Works perfectly but it's unresolved, yeah...
		# noinspection PyUnresolvedReferences
		button.clicked.connect(action)
		return button

	def toast_clicked(self):
		print("toast")
		# TODO: actually toast
		self.drives_list.refresh()

	def cancel_clicked(self):
		print("cancel")
		# TODO: actually cancel
		self.drives_list.refresh()


class DistroList(QAbstractListModel):
	def __init__(self):
		# noinspection PyArgumentList
		super().__init__()
		self.list = []
		self.list.append(('some_icon.png', 'Ubuntu 18.04 64 bit'))
		self.list.append(('some_icon.png', 'Arch Linux'))
		self.list.append(('some_icon.png', 'Debian GNU/Linux 1.0 pre-alpha'))

	# noinspection PyMethodOverriding
	def rowCount(self, parent):
		return len(self.list)

	# noinspection PyMethodOverriding
	def data(self, index, role):
		row = index.row()
		value = self.list[row]

		# if role == QtCore.Qt.ToolTipRole:
		# 	return 'test1: ' + value[0] + ' test2: ' + value[1]

		# if role == QtCore.Qt.DecorationRole:
		# 	pixmap = QtGui.QPixmap(images + 'small2.png')
		# 	icon = QtGui.QIcon(pixmap)
		# 	return icon

		if role == QtCore.Qt.DisplayRole:
			return value[1]

	def flags(self, index):
		return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


class DriveList(QAbstractListModel):
	def __init__(self):
		# noinspection PyArgumentList
		super().__init__()
		self.list = []
		self.system_drives = set()

		lsblk = self.do_lsblk()
		for device in lsblk["blockdevices"]:
			print(f"Detected /dev/{device['name']} as system drive")
			self.system_drives.add(device['name'])

	# noinspection PyMethodOverriding
	def rowCount(self, parent):
		return len(self.list)

	# noinspection PyMethodOverriding
	def data(self, index, role):
		row = index.row()

		if role == QtCore.Qt.DisplayRole:
			return self.list[row]

	def flags(self, index):
		return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

	def refresh(self):
		lsblk = self.do_lsblk()
		new_list = []
		for device in lsblk["blockdevices"]:
			if device['name'] not in self.system_drives:
				vendor = device['vendor'].trim()
				model = device['model'].trim()
				size = self.pretty_size(device['size'])
				device = f"/dev/{device['name']}"
				new_list.append(f'{vendor} {model}, {size} ({device})')

		if not new_list == self.list:
			print("No changes")
		else:
			print("Drives list changed")
			was = len(self.list)
			self.list = new_list
			# TODO: which index to use?
			# TODO: Also, doesn't work despite existing cases of people using the exact same code, since this needs a QModelIndex and not an int
			self.dataChanged.emit(0, max(len(new_list), was))

	@staticmethod
	def pretty_size(ugly_size: str) -> str:
		unit = ugly_size[-1:]
		size = ugly_size[:-1]
		return f"{size} {unit}iB"

	@staticmethod
	def do_lsblk():
		lsblk = subprocess.run(['lsblk', '-S', '-J', '-oNAME,LABEL,VENDOR,MODEL,RM,SIZE'], stdout=subprocess.PIPE)
		return json.loads(lsblk.stdout.decode('utf-8'))


def diff(start: QDateTime):
	now = QDateTime()
	now.currentDateTime().toSecsSinceEpoch()
	# print(time.toString(Qt.DefaultLocaleLongDate))
	return now - start.toSecsSinceEpoch()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = Toaster()
	sys.exit(app.exec_())

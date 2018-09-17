#!/usr/bin/env python3
import sys

from PyQt5.QtDBus import QDBusConnection, QDBusMessage
from PyQt5.QtGui import QIcon, QPixmap
from json import JSONDecodeError
from multiprocessing import Lock
from threading import Thread

import json
import subprocess
# noinspection PyUnresolvedReferences
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QDateTime, QSize, QObject, QEvent, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QDesktopWidget, QMainWindow, QGridLayout, QLabel, \
	QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem
from dataclasses import dataclass
from typing import List


def make_button(text: str, action, icon=None, tooltip=''):
	button = QPushButton(text)
	if len(tooltip) > 0:
		button.setToolTip(tooltip)
	if icon is not None:
		button.setIcon(icon)
	button.resize(button.sizeHint())
	# Works perfectly but it's unresolved, yeah...
	# noinspection PyUnresolvedReferences
	button.clicked.connect(action)
	return button


class Toaster(QMainWindow):

	def __init__(self, argv: List[str]):
		if len(argv) <= 1:
			# TODO: file selection dialog?
			print("Provide path to distro list JSON file")
			exit(1)

		json_distros = None
		distros = []
		try:
			with open(argv[1]) as file:
				json_distros = json.loads(file.read())
		except FileNotFoundError:
			print(f"Cannot open {argv[1]} for reading")
			exit(1)
		except JSONDecodeError as e:
			print(f"JSON decode error in {argv[1]} on line {e.lineno}, col {e.colno}: {e.msg}")
			exit(1)

		for json_distro in json_distros:
			distro = Distro(json_distro['name'], json_distro['file'], json_distro['logo'], json_distro['description'])
			distros.append(distro)

		# noinspection PyArgumentList
		super().__init__()
		self.status_bar = self.statusBar()
		self.distro_widget = DistroList(distros)
		self.drives_list = DriveList()
		self.window()

		dbus = QDBusConnection.systemBus()
		dbus.connect('org.freedesktop.UDisks2', '/org/freedesktop/UDisks2', 'org.freedesktop.DBus.ObjectManager', 'InterfacesAdded', self.handle_dbus_signal)

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
		self.resize(300, 550)
		self.center()
		self.setWindowTitle('Crispy Flash Drives')

		toast_btn = make_button('Toast!', self.toast_clicked)
		cancel_btn = make_button('Cancel', self.cancel_clicked)
		refresh_btn = make_button('Refresh', self.refresh_clicked)

		# Label and selection area (first row)
		# noinspection PyArgumentList
		grid.addWidget(self.distro_widget, 1, 0, 1, 2)  # span both columns (and one row)

		# Label and selection area (second row)
		grid.addWidget(QLabel('Flash drive'), 2, 0)
		grid.addWidget(self.drives_list, 2, 1)

		# noinspection PyArgumentList
		button_area = QWidget()
		button_grid = QHBoxLayout()
		button_area.setLayout(button_grid)
		button_grid.addStretch()  # This is done twice to center buttons horizontally
		# noinspection PyArgumentList
		button_grid.addWidget(toast_btn)
		# noinspection PyArgumentList
		button_grid.addWidget(cancel_btn)
		# noinspection PyArgumentList
		button_grid.addWidget(refresh_btn)
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

	def toast_clicked(self):
		print("toast")

	def cancel_clicked(self):
		print("cancel")

	def refresh_clicked(self):
		print("refresh")
		self.drives_list.refresh()

	# Good example (the only one that exists, actually): https://stackoverflow.com/q/38142809
	@pyqtSlot(QDBusMessage, name='handle_dbus_signal')
	def handle_dbus_signal(self, msg):
		print(msg)


@dataclass
class Distro:
	name: str
	file: str
	logo: str  # TODO: use QPixmap here? Or QIcon?
	description: str


class DistroList(QWidget):
	def __init__(self, distros: List[Distro]):
		# noinspection PyArgumentList
		super().__init__()
		self.list = distros
		self.position = 0

		grid = QGridLayout()
		# Three columns: sides fixed, center can expand
		grid.setColumnStretch(0, 0)
		grid.setColumnStretch(1, 1)
		grid.setColumnStretch(2, 0)
		self.setLayout(grid)

		icon = QIcon()
		# TODO: better shortcuts than Alt+P and Alt+N
		# TODO: no text, just buttons. LARGE buttons.
		# noinspection PyArgumentList
		grid.addWidget(make_button('&Previous', self.scroll_left, icon.fromTheme('arrow-left')), 1, 0)

		self.distro_widget = DistroView(distros[0])
		# noinspection PyArgumentList
		grid.addWidget(self.distro_widget, 1, 1)

		# noinspection PyArgumentList
		grid.addWidget(make_button('&Next', self.scroll_right, icon.fromTheme('arrow-right')), 1, 2)

	def scroll_left(self):
		self.position -= 1
		if self.position < 0:
			self.position = len(self.list) - 1
		self.distro_widget.set_distro(self.list[self.position])

	def scroll_right(self):
		self.position += 1
		self.position %= len(self.list)
		self.distro_widget.set_distro(self.list[self.position])


class DistroView(QWidget):
	def __init__(self, distro: Distro):
		# noinspection PyArgumentList
		super().__init__()
		stack = QVBoxLayout()
		self.setLayout(stack)
		self.distro = None

		self.icon_widget = QLabel(self)
		self.icon_widget.setAlignment(QtCore.Qt.AlignCenter)
		# noinspection PyArgumentList
		stack.addWidget(self.icon_widget)
		self.title_widget = QLabel(self)
		self.title_widget.setAlignment(QtCore.Qt.AlignCenter)
		# noinspection PyArgumentList
		stack.addWidget(self.title_widget)
		self.description_widget = QLabel(self)
		# self.description_widget.setAlignment(QtCore.Qt.AlignCenter)
		self.description_widget.setWordWrap(True)
		# noinspection PyArgumentList
		stack.addWidget(self.description_widget)
		stack.addStretch()

		self.set_distro(distro)

	def set_distro(self, distro: Distro):
		self.distro = distro
		self.title_widget.setText(f"<h2>{distro.name}</h2>")
		self.description_widget.setText(distro.description)
		size = QSize()
		size.setHeight(100)
		size.setWidth(100)
		pixmap = QIcon(distro.logo).pixmap(size)
		# noinspection PyArgumentList
		self.icon_widget.setPixmap(pixmap)


class DriveList(QListWidget):
	def __init__(self):
		# noinspection PyArgumentList
		super().__init__()
		self.list = []
		self.busy_lock = Lock()
		self.busy = set()
		self.system_drives = set()

		lsblk = self.do_lsblk()
		for device in lsblk["blockdevices"]:
			print(f"Detected /dev/{device['name']} as system drive")
			self.system_drives.add(device['name'])

	def refresh(self):
		lsblk = self.do_lsblk()
		new_list = []
		for device in lsblk["blockdevices"]:
			if device['name'] not in self.system_drives:
				vendor = device['vendor'].strip()
				model = device['model'].strip()
				size = self.pretty_size(device['size'])
				device = f"/dev/{device['name']}"
				if vendor == "ATA":
					new_list.append(f'{model}, {size} ({device})')
				else:
					new_list.append(f'{vendor} {model}, {size} ({device})')

		if new_list == self.list:
			print("No changes")
		else:
			print("Drives list changed")
			old_list = self.list
			self.list = new_list
			if len(old_list) > 0:
				self.clear()
			if len(new_list) > 0:
				with self.busy_lock:  # Maybe needed, maybe not
					for device in new_list:
						item = QListWidgetItem(self)
						item.setText(device)
						item.setIcon(self.icon_for(device))

	def icon_for(self, device: str) -> QIcon:
		icon = QIcon()
		if device in self.busy:  # Lock that somewhere before calling, maybe
			return icon.fromTheme("dialog-warning")
		else:
			return icon.fromTheme("drive-removable-media")

	@staticmethod
	def pretty_size(ugly_size: str) -> str:
		unit = ugly_size[-1:]
		size = ugly_size[:-1].replace(',', '.')
		return f"{size} {unit}iB"

	@staticmethod
	def do_lsblk():
		lsblk = subprocess.run(['lsblk', '-S', '-J', '-oNAME,VENDOR,MODEL,SIZE'], stdout=subprocess.PIPE)
		return json.loads(lsblk.stdout.decode('utf-8'))


def diff(start: QDateTime):
	now = QDateTime()
	now.currentDateTime().toSecsSinceEpoch()
	# print(time.toString(Qt.DefaultLocaleLongDate))
	return now - start.toSecsSinceEpoch()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = Toaster(app.arguments())
	sys.exit(app.exec_())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.03.19 01:00:00                  #
# ================================================== #

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QSplitter, QCheckBox, QLabel, QWidget

from pygpt_net.ui.widget.dialog.interpreter import InterpreterDialog
from pygpt_net.ui.widget.textarea.interpreter import PythonInput, PythonOutput
from pygpt_net.utils import trans


class Interpreter:
    def __init__(self, window=None):
        """
        Python interpreter dialog

        :param window: Window instance
        """
        self.window = window

    def setup(self):
        """Setup interpreter dialog"""
        self.window.interpreter = PythonOutput(self.window)
        self.window.interpreter.setReadOnly(True)

        self.window.ui.nodes['interpreter.code'] = PythonOutput(self.window)
        self.window.ui.nodes['interpreter.code'].textChanged.connect(self.window.controller.interpreter.save_edit)
        self.window.ui.nodes['interpreter.code'].setReadOnly(False)

        self.window.ui.nodes['interpreter.output_label'] = QLabel(trans("interpreter.edit_label.output"))
        self.window.ui.nodes['interpreter.edit_label'] = QLabel(trans("interpreter.edit_label.edit"))

        self.window.ui.nodes['interpreter.all'] = QCheckBox(trans("interpreter.all"))
        self.window.ui.nodes['interpreter.all'].setChecked(True)
        self.window.ui.nodes['interpreter.all'].clicked.connect(
            lambda: self.window.controller.interpreter.toggle_all())

        self.window.ui.nodes['interpreter.auto_clear'] = QCheckBox(trans("interpreter.auto_clear"))
        self.window.ui.nodes['interpreter.auto_clear'].setChecked(True)
        self.window.ui.nodes['interpreter.auto_clear'].clicked.connect(
            lambda: self.window.controller.interpreter.toggle_auto_clear())

        self.window.ui.nodes['interpreter.btn.clear'] = QPushButton(trans("dialog.logger.btn.clear"))
        self.window.ui.nodes['interpreter.btn.clear'].clicked.connect(
            lambda: self.window.controller.interpreter.clear())

        self.window.ui.nodes['interpreter.btn.send'] = QPushButton(trans("interpreter.btn.send"))
        self.window.ui.nodes['interpreter.btn.send'].clicked.connect(
            lambda: self.window.controller.interpreter.send_input())

        self.window.ui.nodes['interpreter.input'] = PythonInput(self.window)
        self.window.ui.nodes['interpreter.input'].setPlaceholderText(trans("interpreter.input.placeholder"))

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.window.ui.nodes['interpreter.output_label'])
        left_layout.addWidget(self.window.interpreter)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.window.ui.nodes['interpreter.edit_label'])
        right_layout.addWidget(self.window.ui.nodes['interpreter.code'])
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        self.window.ui.splitters['interpreter.columns'] = QSplitter(Qt.Horizontal)
        self.window.ui.splitters['interpreter.columns'].addWidget(left_widget)
        self.window.ui.splitters['interpreter.columns'].addWidget(right_widget)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.window.ui.nodes['interpreter.btn.clear'])
        bottom_layout.addWidget(self.window.ui.nodes['interpreter.auto_clear'])
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.window.ui.nodes['interpreter.all'])
        bottom_layout.addWidget(self.window.ui.nodes['interpreter.btn.send'])

        edit_layout = QVBoxLayout()
        edit_layout.addWidget(self.window.ui.splitters['interpreter.columns'])
        edit_layout.setContentsMargins(0, 0, 0, 0)

        edit_widget = QWidget()
        edit_widget.setLayout(edit_layout)

        self.window.ui.splitters['interpreter'] = QSplitter(Qt.Vertical)
        self.window.ui.splitters['interpreter'].addWidget(edit_widget)
        self.window.ui.splitters['interpreter'].addWidget(self.window.ui.nodes['interpreter.input'])
        self.window.ui.splitters['interpreter'].setStretchFactor(0, 4)
        self.window.ui.splitters['interpreter'].setStretchFactor(1, 1)

        layout = QVBoxLayout()
        layout.addWidget(self.window.ui.splitters['interpreter'])
        layout.addLayout(bottom_layout)

        self.window.ui.dialog['interpreter'] = InterpreterDialog(self.window)
        self.window.ui.dialog['interpreter'].setLayout(layout)
        self.window.ui.dialog['interpreter'].setWindowTitle(trans("dialog.interpreter.title"))
        self.window.ui.dialog['interpreter'].resize(800, 500)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.03.16 12:00:00                  #
# ================================================== #

from PySide6.QtCore import Qt
from .base import BaseDialog


class InterpreterDialog(BaseDialog):
    def __init__(self, window=None, id="interpreter"):
        """
        Interpreter dialog

        :param window: main window
        :param id: logger id
        """
        super(InterpreterDialog, self).__init__(window, id)
        self.window = window

    def closeEvent(self, event):
        """
        Close event

        :param event: close event
        """
        self.cleanup()
        super(InterpreterDialog, self).closeEvent(event)

    def keyPressEvent(self, event):
        """
        Key press event

        :param event: key press event
        """
        if event.key() == Qt.Key_Escape:
            self.cleanup()
            self.close()  # close dialog when the Esc key is pressed.
        else:
            super(InterpreterDialog, self).keyPressEvent(event)

    def cleanup(self):
        """
        Cleanup on close
        """
        if self.window is None:
            return
        self.window.controller.interpreter.opened = False
        self.window.controller.interpreter.close()
        self.window.controller.interpreter.update()

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
import os

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QWidget

from pygpt_net.utils import trans
import pygpt_net.icons_rc


class Actions:
    def __init__(self, window=None):
        """
        Filesystem actions

        :param window: Window instance
        """
        self.window = window

    def has_preview(self, path: str) -> bool:
        """
        Check if file has preview action

        :param path: path to file
        :return: True if file has preview
        """
        if os.path.isdir(path):
            return False
        return True

    def has_use(self, path: str) -> bool:
        """
        Check if file has preview action

        :param path: path to file
        :return: True if file has preview
        """
        return self.window.core.filesystem.types.is_image(path) or self.window.core.filesystem.types.is_video(path)

    def get_preview(self, parent: QWidget, path: str) -> list:
        """
        Get preview actions for context menu

        :param parent: explorer widget
        :param path: path to file
        :return: list of context menu actions
        """
        actions = []
        if self.window.core.filesystem.types.is_video(path) or self.window.core.filesystem.types.is_audio(path):
            action = QAction(
                QIcon(":/icons/video.svg"),
                trans('action.video.play'),
                parent,
            )
            action.triggered.connect(
                lambda: self.window.controller.video.play(path),
            )
            actions.append(action)
            action = QAction(
                QIcon(":/icons/hearing.svg"),
                trans('action.video.transcribe'),
                parent,
            )
            action.triggered.connect(
                lambda: self.window.controller.audio.transcript.from_file(path),
            )
            actions.append(action)
        elif self.window.core.filesystem.types.is_image(path):
            action = QAction(
                QIcon(":/icons/image.svg"),
                trans('action.preview'),
                parent,
            )
            action.triggered.connect(
                lambda: self.window.controller.chat.image.open_preview(path),
            )
            actions.append(action)
        else:
            ext = os.path.splitext(path)[1][1:].lower()
            if ext not in self.window.core.filesystem.types.get_excluded_extensions():
                action = QAction(
                    QIcon(":/icons/edit.svg"),
                    trans('action.edit'),
                    parent,
                )
                action.triggered.connect(
                    lambda: self.window.controller.editor.toggle(path),
                )
                actions.append(action)
        return actions

    def get_use(self, parent: QWidget, path: str) -> list:
        """
        Get use actions for context menu

        :param parent: explorer widget
        :param path: path to file
        :return: list of context menu actions
        """
        actions = []
        if self.window.core.filesystem.types.is_image(path):
            action = QAction(
                QIcon(":/icons/brush.svg"),
                trans('action.use.image'),
                parent,
            )
            action.triggered.connect(
                lambda: self.window.controller.painter.open_external(path),
            )
            actions.append(action)
        return actions

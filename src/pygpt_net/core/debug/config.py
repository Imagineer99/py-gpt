#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.02.25 22:00:00                  #
# ================================================== #

import os


class ConfigDebug:
    def __init__(self, window=None):
        """
        Config debug

        :param window: Window instance
        """
        self.window = window
        self.id = 'config'

    def update(self):
        """Update debug window."""
        self.window.core.debug.begin(self.id)

        path = os.path.join(self.window.core.config.path, '', 'config.json')
        self.window.core.debug.add(self.id, 'Config File', str(path))
        self.window.core.debug.add(
            self.id, 'Sections',
            str(self.window.controller.settings.editor.get_sections())
        )
        self.window.core.debug.add(
            self.id, 'Options',
            str(self.window.controller.settings.editor.get_options())
        )

        # config data
        for key in self.window.core.config.all():
            self.window.core.debug.add(self.id, key, str(self.window.core.config.get(key)))

        self.window.core.debug.end(self.id)

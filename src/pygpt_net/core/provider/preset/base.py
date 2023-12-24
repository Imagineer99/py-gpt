#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2023.12.23 19:00:00                  #
# ================================================== #


class BaseProvider:
    def __init__(self, window=None):
        self.window = window
        self.id = ""
        self.type = "preset"

    def install(self):
        pass

    def create(self, meta):
        pass

    def load(self):
        pass

    def save(self, id, item):
        pass

    def save_all(self, items):
        pass

    def remove(self, id):
        pass

    def truncate(self):
        pass

    def dump(self, ctx):
        pass

    def get_version(self):
        pass

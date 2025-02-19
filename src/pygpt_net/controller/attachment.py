#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.03.15 10:00:00                  #
# ================================================== #

import os
from datetime import datetime

from PySide6.QtWidgets import QFileDialog

from pygpt_net.item.assistant import AssistantItem
from pygpt_net.item.attachment import AttachmentItem
from pygpt_net.utils import trans


class Attachment:
    def __init__(self, window=None):
        """
        Attachment controller

        :param window: Window instance
        """
        self.window = window

    def setup(self):
        """Setup attachments"""
        # send clear
        if self.window.core.config.has('attachments_send_clear') \
                and self.window.core.config.get('attachments_send_clear'):
            self.window.ui.nodes['attachments.send_clear'].setChecked(True)
        else:
            self.window.ui.nodes['attachments.send_clear'].setChecked(False)

        #  capture clear
        if self.window.core.config.has('attachments_capture_clear') \
                and self.window.core.config.get('attachments_capture_clear'):
            self.window.ui.nodes['attachments.capture_clear'].setChecked(True)
        else:
            self.window.ui.nodes['attachments.capture_clear'].setChecked(False)

        self.window.core.attachments.load()
        self.update()

    def update(self):
        """Update attachments list"""
        mode = self.window.core.config.get('mode')
        items = self.window.core.attachments.get_all(mode)
        self.window.ui.chat.input.attachments.update(items)
        self.update_tab(mode)

        if not self.has(mode):
            self.window.controller.chat.vision.unavailable()
        else:
            if mode == 'vision' or self.window.controller.plugins.is_type_enabled('vision'):
                self.window.controller.chat.vision.available()

        # update tokens counter (vision plugin, etc.)
        self.window.controller.ui.update_tokens()

    def update_tab(self, mode: str):
        """
        Update tab label

        :param mode: mode
        """
        num_files = self.window.core.attachments.count(mode)
        suffix = ''
        if num_files > 0:
            suffix = f' ({num_files})'
        self.window.ui.tabs['input'].setTabText(
            1,
            trans('attachments.tab') + suffix,
        )

    def select(self, mode: str, idx: int):
        """
        Select attachment

        :param mode: mode
        :param idx: index
        """
        self.window.core.attachments.current = self.window.core.attachments.get_id_by_idx(
            mode=mode,
            idx=idx,
        )

    def selection_change(self):
        """
        Select on list change
        """
        # TODO: implement this
        pass

    def delete(self, idx: int, force: bool = False, remove_local: bool = False):
        """
        Delete attachment

        :param idx: index of attachment
        :param force: force delete
        :param remove_local: remove local file
        """
        mode = self.window.core.config.get('mode')
        if not force:
            self.window.ui.dialogs.confirm(
                type='attachments.delete',
                id=idx,
                msg=trans('attachments.delete.confirm'),
            )
            return

        file_id = self.window.core.attachments.get_id_by_idx(
            mode=mode,
            idx=idx,
        )
        self.window.core.attachments.delete(
            mode=mode,
            id=file_id,
            remove_local=remove_local,
        )

        # clear current if current == deleted
        if self.window.core.attachments.current == file_id:
            self.window.core.attachments.current = None

        if not self.has(mode):
            self.window.controller.chat.vision.unavailable()

        self.update()

    def rename(self, mode: str, idx: int):
        """
        Rename attachment

        :param mode: mode
        :param idx: selected attachment index
        """

        # get attachment ID by index
        file_id = self.window.core.attachments.get_id_by_idx(
            mode=mode,
            idx=idx,
        )

        # get attachment object by ID
        data = self.window.core.attachments.get_by_id(
            mode=mode,
            id=file_id,
        )
        if data is None:
            return

        # set dialog and show
        self.window.ui.dialog['rename'].id = 'attachment'
        self.window.ui.dialog['rename'].input.setText(data.name)
        self.window.ui.dialog['rename'].current = file_id
        self.window.ui.dialog['rename'].show()
        self.update()

    def update_name(self, file_id: str, name: str):
        """
        Update name

        :param file_id: file_id
        :param name: name
        """
        # rename filename in attachments
        mode = self.window.core.config.get('mode')
        self.window.core.attachments.rename_file(
            mode=mode,
            id=file_id,
            name=name,
        )

        # rename filename in assistant data if mode = assistant
        if self.window.core.config.get('mode') == 'assistant':
            assistant_id = self.window.core.config.get('assistant')
            if assistant_id is not None:
                self.window.controller.assistant.files.update_name(
                    file_id=file_id,
                    name=name,
                )

        # close rename dialog and update attachments list
        self.window.ui.dialog['rename'].close()
        self.update()

    def add(self, mode: str, attachment: AttachmentItem):
        """
        Add attachment item to list

        :param mode: mode
        :param attachment: attachment object
        """
        self.window.core.attachments.add(
            mode=mode,
            item=attachment,
        )
        self.update()

    def clear(self, force: bool = False, remove_local=False):
        """
        Clear attachments list

        :param force: force clear
        :param remove_local: remove local copies
        """
        if not force:
            self.window.ui.dialogs.confirm(
                type='attachments.clear',
                id=-1,
                msg=trans('attachments.clear.confirm'),
            )
            return

        # delete all from attachments for current mode
        mode = self.window.core.config.get('mode')
        self.window.core.attachments.delete_all(
            mode=mode,
            remove_local=remove_local,
        )

        self.window.controller.chat.vision.unavailable()  # set no content to provide

        if mode == 'assistant':
            # delete all from assistant data
            assistant_id = self.window.core.config.get('assistant')
            if assistant_id is not None:
                assistant = self.window.core.assistants.get_by_id(
                    id=assistant_id,
                )
                if assistant is not None:
                    self.window.controller.assistant.files.clear_attachments(
                        assistant=assistant,
                    )
        self.update()

    def open_add(self):
        """Open add attachment file dialog"""
        last_dir = self.window.core.config.get_last_used_dir()
        mode = self.window.core.config.get('mode')
        dialog = QFileDialog(self.window)
        dialog.setDirectory(last_dir)
        dialog.setFileMode(QFileDialog.ExistingFiles)
        if dialog.exec():
            files = dialog.selectedFiles()
            if files:
                self.window.core.config.set_last_used_dir(
                    os.path.dirname(files[0]),
                )
                for path in files:
                    # build attachment object
                    basename = os.path.basename(path)
                    attachment = self.window.core.attachments.new(
                        mode=mode,
                        name=basename,
                        path=path,
                        auto_save=False,
                    )
                    # append attachment to assistant if current mode = assistant
                    if mode == 'assistant':
                        assistant_id = self.window.core.config.get('assistant')
                        if assistant_id is not None:
                            assistant = self.window.core.assistants.get_by_id(assistant_id)
                            if assistant is not None:
                                self.window.controller.assistant.files.append(
                                    assistant=assistant,
                                    attachment=attachment,
                                )

            # save attachments and update attachments list
            self.window.core.attachments.save()
            self.update()

    def open_dir(self, mode: str, idx: int):
        """
        Open in directory

        :param mode: mode
        :param idx: index
        """
        # TODO: check dict/obj
        file_id = self.window.core.attachments.get_id_by_idx(
            mode=mode,
            idx=idx,
        )
        data = self.window.core.attachments.get_by_id(
            mode=mode,
            id=file_id,
        )
        if data.path is not None and data.path != '' and os.path.exists(data.path):
            self.window.controller.files.open_dir(
                path=data.path,
                select=True,
            )

    def open(self, mode: str, idx: int):
        """
        Open attachment

        :param mode: mode
        :param idx: index
        """
        # TODO: check dict/obj
        file_id = self.window.core.attachments.get_id_by_idx(
            mode=mode,
            idx=idx,
        )
        data = self.window.core.attachments.get_by_id(
            mode=mode,
            id=file_id,
        )
        if data.path is not None and data.path != '' and os.path.exists(data.path):
            self.window.controller.files.open(
                path=data.path,
            )

    def import_from_assistant(self, mode: str, assistant: AssistantItem):
        """
        Load attachments from assistant

        :param mode: mode
        :param assistant: assistant object
        """
        if assistant is None:
            return

        # restore attachments from assistant
        self.window.core.attachments.from_attachments(
            mode=mode,
            attachments=assistant.attachments,
        )

    def has(self, mode: str) -> bool:
        """
        Return True if current mode has attachments

        :param mode: mode to check
        :return: True if has attachments
        """
        return self.window.core.attachments.has(mode)

    def get_download_path(self, file_name: str) -> str:
        """
        Get file download path

        :param file_name: file name
        :return: download directory
        """
        if self.window.core.config.has("download.dir") and self.window.core.config.get("download.dir") != "":
            path = os.path.join(
                self.window.core.config.get_user_dir('data'),
                self.window.core.config.get("download.dir"),
                file_name,
            )
        else:
            path = os.path.join(
                self.window.core.config.get_user_dir('data'),
                file_name,
            )
        return path

    def download(self, file_id: str, ext: str = None) -> str or None:
        """
        Download file

        :param file_id: file id to download (id in OpenAI API)
        :param ext: file extension to add (optional)
        :return: path to downloaded file
        """
        try:
            # get file info from assistant API
            data = self.window.core.gpt.assistants.file_info(file_id)
            if data is None:
                return

            # prepare path to download file
            data.filename = os.path.basename(data.filename)

            # add extension if provided
            if ext is not None:
                data.filename = data.filename + ext

            # prepare path to downloaded file
            path = self.get_download_path(data.filename)

            # create download directory if not exists
            directory = os.path.dirname(path)
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            # check if file exists, if yes, append timestamp prefix
            if os.path.exists(path):
                # append timestamp prefix to filename
                filename = f'{datetime.now().strftime("%Y%m%d%H%M%S")}_{data.filename}'
                path = self.get_download_path(filename)

            # download file
            self.window.core.gpt.assistants.file_download(
                file_id=file_id,
                path=path,
            )
            return path  # return path to downloaded file
        except Exception as e:
            self.window.core.debug.log(e)
            self.window.ui.dialogs.alert(e)

    def toggle_send_clear(self, value: bool):
        """
        Toggle send clear

        :param value: value of the checkbox
        """
        self.window.core.config.set('attachments_send_clear', value)

    def toggle_capture_clear(self, value: bool):
        """
        Toggle capture clear

        :param value: value of the checkbox
        """
        self.window.core.config.set('attachments_capture_clear', value)

    def is_capture_clear(self) -> bool:
        """
        Return True if capture clear is enabled

        :return: True if capture clear is enabled
        """
        if not self.window.core.config.has('attachments_capture_clear'):
            self.window.core.config.set('attachments_capture_clear', False)
        return self.window.core.config.get('attachments_capture_clear')

    def is_send_clear(self) -> bool:
        """
        Return True if send clear is enabled

        :return: True if send clear is enabled
        """
        if not self.window.core.config.has('attachments_send_clear'):
            self.window.core.config.set('attachments_send_clear', False)
        return self.window.core.config.get('attachments_send_clear')

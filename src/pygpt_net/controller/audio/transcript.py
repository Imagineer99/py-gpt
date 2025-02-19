#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.03.19 06:00:00                  #
# ================================================== #

import os

from PySide6.QtWidgets import QFileDialog

from pygpt_net.core.dispatcher import Event
from pygpt_net.item.ctx import CtxItem
from pygpt_net.utils import trans


class Transcript:
    def __init__(self, window=None):
        """
        Transcript controller

        :param window: Window instance
        """
        self.window = window
        self.is_open = False

    def setup(self):
        """Setup controller"""
        self.restore()
        self.restore_auto_convert()

    def update(self):
        """Update transcribe menu"""
        if self.is_open:
            self.window.ui.menu['audio.transcribe'].setChecked(True)
        else:
            self.window.ui.menu['audio.transcribe'].setChecked(False)

    def open_file(self):
        """Open transcribe file dialog"""
        path, _ = QFileDialog.getOpenFileName(
            self.window,
            trans("action.video.open"),
            "",
            "Audio Files (*.mp3 *.wav *.ogg *.flac *.m4a *.mp4 *.avi *.mov *.mkv *.webm)")
        if path:
            self.transcribe(path)

    def transcribe(self, path: str, force: bool = False):
        """
        Transcribe audio file

        :param path: audio file path
        :param force: force transcribe
        """
        if not force:
            self.window.ui.dialogs.confirm(
                type='audio.transcribe',
                id=path,
                msg=trans("audio.transcribe.confirm"),
            )
            return
        path = self.prepare_audio(path)
        if path is not None:
            event = Event(Event.AUDIO_INPUT_TRANSCRIBE, {
                'path': str(path),
            })
            event.ctx = CtxItem()  # tmp
            self.clear(force=True)
            self.window.controller.command.dispatch_only(event)
            self.window.ui.nodes['audio.transcribe.status'].setText(
                "Transcribing: {} ... Please wait...".format(os.path.basename(path)))

    def on_transcribe(self, path: str, text: str):
        """
        On audio transcribed

        :param path: audio file path
        :param text: transcribed text
        """
        self.store(text)
        self.window.ui.nodes['audio.transcribe.status'].setText(
            trans("audio.transcribe.result.finished").format(path=os.path.basename(path)))
        self.window.ui.editor["audio.transcribe"].setPlainText(text)

    def from_file(self, path: str):
        """
        Open and transcribe audio file

        :param path: audio file path
        """
        self.open()
        self.window.ui.nodes['audio.transcribe.status'].setText(
            trans("audio.transcribe.result.selected").format(path=os.path.basename(path)))
        self.transcribe(path)

    def open(self):
        """Open transcriber"""
        self.window.ui.nodes['audio.transcribe.status'].setText("")
        self.window.ui.dialogs.open('audio.transcribe', width=800, height=600)
        self.is_open = True
        self.update()

    def close(self):
        """Close transcribe"""
        self.window.ui.dialogs.close('audio.transcribe')
        self.is_open = False

    def prepare_audio(self, path: str) -> str:
        """
        Convert video to audio if needed

        :param path: video file path
        """
        # ffmpeg required here
        if self.is_video(path) and self.is_auto_convert():
            try:
                self.window.ui.nodes['audio.transcribe.status'].setText(
                    "Converting to audio: {} ... Please wait...".format(os.path.basename(path)))
                video_type = path.split(".")[-1].lower()
                try:
                    from pydub import AudioSegment
                except ImportError:
                    self.window.ui.nodes['audio.transcribe.status'].setText("Please install pydub 'pip install pydub'")
                    raise ImportError("Please install pydub 'pip install pydub' ")
                video = AudioSegment.from_file(path, format=video_type)
                # extract audio from video
                audio = video.split_to_mono()[0]
                file_str = os.path.join(self.window.core.config.get_user_path(), "transcript.mp3")
                if os.path.exists(file_str):
                    os.remove(file_str)
                audio.export(file_str, format="mp3")
                self.window.ui.nodes['audio.transcribe.status'].setText("Converted: {}".format(os.path.basename(file_str)))
                path = file_str
            except Exception as e:
                self.window.core.debug.log(e)
                self.window.ui.nodes['audio.transcribe.status'].setText(
                    "Aborted. Can't convert video to mp3! FFMPEG not installed?\n"
                    "Please install \"ffmpeg\" or disable the option \"Always convert video to mp3\" to transcribe from video file.")
                self.window.ui.dialogs.alert(e)
                path = None
        return path

    def toggle_auto_convert(self):
        """Toggle auto video conversion"""
        state = self.window.ui.nodes['audio.transcribe.convert_video'].isChecked()
        self.window.core.config.set('audio.transcribe.convert_video', state)
        self.window.core.config.save()

    def restore_auto_convert(self):
        """Restore auto video conversion"""
        if self.window.core.config.has('audio.transcribe.convert_video'):
            state = self.window.core.config.get('audio.transcribe.convert_video', True)
            self.window.ui.nodes['audio.transcribe.convert_video'].setChecked(state)

    def is_auto_convert(self) -> bool:
        """
        Check if auto video conversion is enabled

        :return: True if enabled
        """
        return self.window.ui.nodes['audio.transcribe.convert_video'].isChecked()

    def store(self, text: str):
        """
        Store transcription to file

        :param text: transcribed text
        """
        path = os.path.join(self.window.core.config.get_user_path(), "transcript.txt")
        with open(path, "w") as f:
            f.write(text)

    def restore(self):
        """Restore transcription from file"""
        path = os.path.join(self.window.core.config.get_user_path(), "transcript.txt")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = f.read()
                self.window.ui.editor["audio.transcribe"].setPlainText(data)

    def is_video(self, file: str) -> bool:
        """
        Check if file is a video.

        :param file: file path
        :return: True if file is a video
        """
        ext = file.split(".")[-1].lower()
        return ext in ["mp4", "avi", "mov", "mkv", "webm"]

    def show_hide(self, show: bool = True):
        """
        Show/hide transcribe window

        :param show: show/hide
        """
        if show:
            self.open()
        else:
            self.close()

    def on_close(self):
        """On transcribe window close"""
        self.is_open = False
        self.update()

    def clear(self, force: bool = False):
        """
        Clear transcribe data

        :param force: force clear
        """
        if not force:
            self.window.ui.dialogs.confirm(
                type='audio.transcribe.clear',
                id=0,
                msg=trans("audio.transcribe.clear.confirm"),
            )
            return
        id = 'audio.transcribe'
        self.window.ui.editor[id].clear()
        self.window.ui.nodes['audio.transcribe.status'].setText("")
        self.store("")

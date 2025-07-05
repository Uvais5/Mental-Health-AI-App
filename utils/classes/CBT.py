from kivymd.app import MDApp
from kivy.metrics import dp
from kivymd.uix.spinner import MDSpinner
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager,Screen
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout

import threading
import yt_dlp
import threading
from kivy.uix.videoplayer import VideoPlayer
from kivy.uix.videoplayer import VideoPlayer
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.spinner import MDSpinner
import threading
from kivy.utils import platform

class cbt(Screen):


    def show_video_dialog(self):
        # Loading UI
        youtube_url = "https://www.youtube.com/watch?v=FEEmD7ngx6U&ab_channel=AddictionPolicyForum"  # Example URL

        if platform == "android":
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Intent = autoclass("android.content.Intent")
            Uri = autoclass("android.net.Uri")

            intent = Intent(Intent.ACTION_VIEW, Uri.parse(youtube_url))
            currentActivity = PythonActivity.mActivity
            currentActivity.startActivity(intent)
        else:
            import webbrowser

            webbrowser.open(youtube_url)
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image as img

from kivymd.uix.button import MDFloatingActionButton
import pandas as pd

from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.video import Video
from kivy.app import App
class reels(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_called = False  # Flag to track if start has been called
    
    def start(self):
        if self.start_called:
            return  # Exit if start has already been called
        
        self.start_called = True  # Set the flag to True
        # List to store video and thumbnail references
        self.video_widgets = []
        
        # Load video URLs from a CSV file
        data = pd.read_csv("C:/Users/uvais/ML(projects)/insta fetch/Insta_reels_direct_link.csv")
        data = data.drop(columns=["Unnamed: 0"], axis=0)

        # Add video widgets to the scrollable list
        for video_url in data.sample(frac = 1)["Reels_url"]:
            # Create a layout to hold the video and its thumbnail
            video_layout = RelativeLayout(size_hint_y=None, height=dp(600),width=320)  # Set height of the layout
            
            # Create the video widget
            video = Video(source=video_url, state="pause", options={'eos': 'loop'})
            video.size_hint_y = None
            video.height = dp(600)  # Height of each video
            video.width = dp(600)
            video.allow_fullscreen=True
            video.adaptive_height=True

            # Create a thumbnail image to overlay on the video
            thumbnail = img(source="C:\\Users\\uvais\\Downloads\\pimg\\loding.jpg",size_hint=(1, 1), allow_stretch=True, keep_ratio=True)
            
            # Add both the video and the thumbnail to the layout
            video_layout.add_widget(video)
            video_layout.add_widget(thumbnail)

            # Store the video and thumbnail references
            self.video_widgets.append((video, thumbnail))

            # Bind touch event to toggle play/pause and hide/show thumbnail
            video.bind(on_touch_down=self.toggle_video_playback)

            # Add the video layout to the UI
            self.ids.video_list.add_widget(video_layout)
        
        # Play the first video automatically
        if self.video_widgets:
            first_video, first_thumbnail = self.video_widgets[0]
            first_video.state = "play"
            first_thumbnail.opacity = 0  # Hide the thumbnail for the first video

        # Bind scroll event to check video visibility
        self.ids.scroll_view.bind(scroll_y=self.check_video_visibility)
        self.ids.video_list.add_widget(MDFloatingActionButton( icon="pencil",theme_icon_color="Custom",md_bg_color="white",icon_color="red"))
        
    def toggle_video_playback(self, video, touch):
        # Find the corresponding thumbnail for the video
        for vid, thumb in self.video_widgets:
            if vid == video:
                # Toggle video play/pause and thumbnail visibility
                if video.collide_point(*touch.pos):
                    if video.state == "play":
                        video.state = "pause"
                        #thumb.opacity = 1  # Show thumbnail when video pauses
                    else:
                        video.state = "play"
                        thumb.opacity = 0  # Hide thumbnail when video plays
                break

    def check_video_visibility(self, *args):
        # Get the current scroll position
        scroll_y = self.ids.scroll_view.scroll_y
        layout_height = self.ids.video_list.height

        for video, thumbnail in self.video_widgets:
            # Get video position from its parent (RelativeLayout)
            parent = video.parent
            video_top = parent.y + parent.height
            video_bottom = parent.y+2

            # Check if the video is in the visible part of the screen
            if video_bottom < layout_height * scroll_y < video_top:
                # If the video is visible and not already playing, play it
                if video.state == "pause":
                    video.state = "play"
                    thumbnail.opacity = 0  # Hide the thumbnail
            else:
                # If the video is not visible, pause it and show the thumbnail
                if video.state == "play":
                    video.state = "pause"
                    #thumbnail.opacity = 1  # Show the thumbnail

        # Make sure only one video plays at a time
        visible_videos = [video for video, _ in self.video_widgets if video.state == "play"]
        if len(visible_videos) > 1:
            for video in visible_videos[1:]:
                video.state = "pause"
                # Find corresponding thumbnail and show it
                for vid, thumb in self.video_widgets:
                    if vid == video:
                        thumb.opacity = 1  # Show thumbnail
    def on_back_button_press(self):
        # Pause all videos when back button is pressed
        for video, thumbnail in self.video_widgets:
            if video.state == "play":
                video.state = "pause"
                thumbnail.opacity = 0 
        App.get_running_app().change_screen("home")
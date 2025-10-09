import os
import streamlit as st

class Dataset:
    """
    class Dataset is designed for loading the learning_database
    """
    root_path = "database/learning_database/"
    def __init__(self, user_name:str) -> None:
        # create the folder for the specific user
        self.user_name = user_name
        self.path = self.root_path + f"{user_name}/"
        # name of text and video
        self.text_data = []
        self.video_data = []
    
    def build_dirs(self):
        # build text and video folder for a user
        # this method seems a little meaningless
        try:
            os.makedirs(self.path, exist_ok=False)
        except:
            print("Failed to build the directories!")

    @staticmethod
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def _load_data_cached(user_name: str):
        """
        Cached version of data loading to avoid reloading files on every rerun.
        Returns tuple of (text_data, video_data, path)
        """
        path = Dataset.root_path + f"{user_name}/"
        text_data = []
        video_data = []
        
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith('.txt'):
                    text_data.append(f)
                elif f.endswith('.mp4'):
                    video_data.append(f)
        
        return text_data, video_data, path

    def load_data(self):
        """Load data using cached method"""
        self.text_data, self.video_data, self.path = Dataset._load_data_cached(self.user_name)

if __name__ == "__main__":
    dataset = Dataset('qi')
    dataset.load_data()
    print(dataset.text_data, dataset.video_data)
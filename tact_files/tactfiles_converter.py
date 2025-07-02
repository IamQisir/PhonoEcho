"""
TactGlove Pattern Converter

This module provides functions to convert vibration patterns between left and right gloves,
and to create patterns that affect both gloves simultaneously.
"""

import json
import copy


def right_to_left(input_file_path, output_file_path):
    """
    Convert right glove vibration patterns to left glove patterns.
    
    This function takes a .tact file designed for the right glove and creates
    a mirrored version for the left glove by:
    1. Moving all vibration effects from GloveR to GloveL
    2. Mirroring X coordinates (new_x = 1 - original_x)
    3. Updating project metadata
    
    Args:
        input_file_path (str): Path to the input right glove .tact file
        output_file_path (str): Path where the left glove .tact file will be saved
    
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    try:
        # Read the input file
        with open(input_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Update project metadata
        data['project']['name'] = data['project']['name'].replace('Right', 'Left')
        data['project']['id'] = 'Left_' + data['project']['id']
        
        # Process each track
        for track in data['project']['tracks']:
            if track['enable']:
                for effect in track['effects']:
                    # Get the right glove settings
                    glove_r_settings = effect['modes']['GloveR']
                    
                    # Move right glove settings to left glove
                    effect['modes']['GloveL'] = copy.deepcopy(glove_r_settings)
                    
                    # Clear right glove settings
                    effect['modes']['GloveR'] = {
                        "dotMode": {"dotConnected": False, "feedback": [{"startTime": 0, "endTime": 0, "playbackType": "NONE", "pointList": []}]},
                        "pathMode": {"feedback": [{"movingPattern": "CONST_SPEED", "playbackType": "NONE", "visible": True, "pointList": []}]},
                        "mode": "PATH_MODE"
                    }
                    
                    # Mirror X coordinates in left glove path mode
                    if 'pathMode' in effect['modes']['GloveL'] and 'feedback' in effect['modes']['GloveL']['pathMode']:
                        for feedback in effect['modes']['GloveL']['pathMode']['feedback']:
                            if 'pointList' in feedback:
                                for point in feedback['pointList']:
                                    if 'x' in point:
                                        point['x'] = 1 - point['x']
        
        # Save the converted file
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, separators=(',', ':'))
        
        print(f"Successfully converted right glove pattern to left glove: {output_file_path}")
        return True
        
    except Exception as e:
        print(f"Error converting right to left glove pattern: {e}")
        return False


def left_to_right(input_file_path, output_file_path):
    """
    Convert left glove vibration patterns to right glove patterns.
    
    This function takes a .tact file designed for the left glove and creates
    a mirrored version for the right glove by:
    1. Moving all vibration effects from GloveL to GloveR
    2. Mirroring X coordinates (new_x = 1 - original_x)
    3. Updating project metadata
    
    Args:
        input_file_path (str): Path to the input left glove .tact file
        output_file_path (str): Path where the right glove .tact file will be saved
    
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    try:
        # Read the input file
        with open(input_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Update project metadata
        data['project']['name'] = data['project']['name'].replace('Left', 'Right')
        data['project']['id'] = 'Right_' + data['project']['id']
        
        # Process each track
        for track in data['project']['tracks']:
            if track['enable']:
                for effect in track['effects']:
                    # Get the left glove settings
                    glove_l_settings = effect['modes']['GloveL']
                    
                    # Move left glove settings to right glove
                    effect['modes']['GloveR'] = copy.deepcopy(glove_l_settings)
                    
                    # Clear left glove settings
                    effect['modes']['GloveL'] = {
                        "dotMode": {"dotConnected": False, "feedback": [{"startTime": 0, "endTime": 0, "playbackType": "NONE", "pointList": []}]},
                        "pathMode": {"feedback": [{"movingPattern": "CONST_SPEED", "playbackType": "NONE", "visible": True, "pointList": []}]},
                        "mode": "PATH_MODE"
                    }
                    
                    # Mirror X coordinates in right glove path mode
                    if 'pathMode' in effect['modes']['GloveR'] and 'feedback' in effect['modes']['GloveR']['pathMode']:
                        for feedback in effect['modes']['GloveR']['pathMode']['feedback']:
                            if 'pointList' in feedback:
                                for point in feedback['pointList']:
                                    if 'x' in point:
                                        point['x'] = 1 - point['x']
        
        # Save the converted file
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, separators=(',', ':'))
        
        print(f"Successfully converted left glove pattern to right glove: {output_file_path}")
        return True
        
    except Exception as e:
        print(f"Error converting left to right glove pattern: {e}")
        return False


def right_to_both(input_file_path, output_file_path):
    """
    Convert right glove vibration patterns to affect both gloves simultaneously.
    
    This function takes a .tact file designed for the right glove and creates
    a version that activates both gloves with:
    1. Keeping original patterns in GloveR
    2. Copying and mirroring patterns to GloveL
    3. Both gloves will vibrate with mirrored patterns
    4. Updating project metadata
    
    Args:
        input_file_path (str): Path to the input right glove .tact file
        output_file_path (str): Path where the both gloves .tact file will be saved
    
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    try:
        # Read the input file
        with open(input_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Update project metadata
        data['project']['name'] = data['project']['name'].replace('Right', 'Both')
        data['project']['id'] = 'Both_' + data['project']['id']
        
        # Process each track
        for track in data['project']['tracks']:
            if track['enable']:
                for effect in track['effects']:
                    # Get the right glove settings
                    glove_r_settings = effect['modes']['GloveR']
                    
                    # Copy right glove settings to left glove and mirror coordinates
                    effect['modes']['GloveL'] = copy.deepcopy(glove_r_settings)
                    
                    # Mirror X coordinates in left glove path mode
                    if 'pathMode' in effect['modes']['GloveL'] and 'feedback' in effect['modes']['GloveL']['pathMode']:
                        for feedback in effect['modes']['GloveL']['pathMode']['feedback']:
                            if 'pointList' in feedback:
                                for point in feedback['pointList']:
                                    if 'x' in point:
                                        point['x'] = 1 - point['x']
        
        # Save the converted file
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, separators=(',', ':'))
        
        print(f"Successfully converted right glove pattern to both gloves: {output_file_path}")
        return True
        
    except Exception as e:
        print(f"Error converting right to both glove pattern: {e}")
        return False


# Example usage
if __name__ == "__main__":
    # Example file paths
    right_glove_file = "tact_files/wav6_right.tact"
    left_glove_file = "tact_files/wav6_left.tact"
    both_gloves_file = "BothGloves.tact"
    
    # Example conversions
    print("TactGlove Pattern Converter Examples:")
    print("1. Converting right glove pattern to left glove...")
    right_to_left(right_glove_file, left_glove_file)
    
    print("2. Converting left glove pattern to right glove...")
    # left_to_right(left_glove_file, "LeftToRight.tact")
    
    print("3. Converting right glove pattern to both gloves...")
    # right_to_both(right_glove_file, both_gloves_file)
    
    print("\nUncomment the function calls above to run the conversions.")
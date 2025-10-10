"""
Complete Async Haptic Integration Example
for Video-TactGlove Synchronization in PhonoEcho

This module demonstrates how to integrate the new bhaptics async SDK
with Streamlit for better video-haptics synchronization.
"""

import asyncio
import json
import time
import streamlit as st
import bhaptics_python
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict

# Global configuration
BHAPTICS_CONFIG = {
    "app_id": "68e8965a321923083807c4b3",
    "api_key": "wlkPxwUpWUJnO0yiYyOv",
    "app_name": "TactGlove"
}

# Thread pool for async execution in Streamlit
_executor = ThreadPoolExecutor(max_workers=2)


class AsyncHapticController:
    """
    Async wrapper for bhaptics SDK with synchronization capabilities
    """
    
    def __init__(self, app_id: str, api_key: str, app_name: str):
        self.app_id = app_id
        self.api_key = api_key
        self.app_name = app_name
        self.initialized = False
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> bool:
        """Initialize the bhaptics SDK"""
        async with self._lock:
            if not self.initialized:
                result = await bhaptics_python.registry_and_initialize(
                    self.app_id,
                    self.api_key,
                    self.app_name
                )
                self.initialized = result
                return result
            return True
    
    async def play_haptic_pattern(
        self,
        position: int,
        duration_ms: int,
        motors: list,
        delay_ms: float = 0
    ) -> int:
        """
        Play haptic pattern with optional delay
        
        Args:
            position: Device position (8=Left Glove, 9=Right Glove)
            duration_ms: Duration in milliseconds
            motors: List of motor intensities (0-100)
            delay_ms: Delay before playing (milliseconds)
        
        Returns:
            Request ID from bhaptics
        """
        if not self.initialized:
            await self.initialize()
        
        # Apply delay if specified
        if delay_ms > 0:
            await asyncio.sleep(delay_ms / 1000.0)
        
        # Play the haptic
        request_id = await bhaptics_python.play_dot(
            position,
            duration_ms,
            motors
        )
        
        return request_id
    
    async def play_synchronized_multimodal(
        self,
        lesson_config: Dict,
        calibration_delay_ms: float = 0
    ):
        """
        Play video and haptics with synchronized timing
        
        Args:
            lesson_config: Dictionary containing haptic pattern info
            calibration_delay_ms: User-calibrated delay for synchronization
        """
        if not self.initialized:
            await self.initialize()
        
        # Extract haptic parameters
        position = lesson_config.get('position', 8)  # Left glove default
        duration_ms = lesson_config.get('duration_ms', 5000)
        motor_pattern = lesson_config.get('motor_pattern', [100] * 6)
        
        # Record start time for logging
        start_time = time.time()
        
        # Apply calibration delay
        if calibration_delay_ms > 0:
            await asyncio.sleep(calibration_delay_ms / 1000.0)
        
        # Start haptics
        request_id = await bhaptics_python.play_dot(
            position,
            duration_ms,
            motor_pattern
        )
        
        actual_delay = (time.time() - start_time) * 1000
        
        return {
            'request_id': request_id,
            'start_time': start_time,
            'actual_delay_ms': actual_delay,
            'target_delay_ms': calibration_delay_ms
        }
    
    async def stop_all(self):
        """Stop all haptic playback"""
        if self.initialized:
            await bhaptics_python.stop_all()
    
    async def close(self):
        """Close the connection"""
        if self.initialized:
            await bhaptics_python.close()
            self.initialized = False


class SyncHapticWrapper:
    """
    Synchronous wrapper for use with Streamlit and threading
    """
    
    def __init__(self, controller: AsyncHapticController):
        self.controller = controller
    
    def initialize(self) -> bool:
        """Sync initialization"""
        return asyncio.run(self.controller.initialize())
    
    def play_haptic_pattern(
        self,
        position: int,
        duration_ms: int,
        motors: list,
        delay_ms: float = 0
    ) -> int:
        """Sync play haptic pattern"""
        return asyncio.run(
            self.controller.play_haptic_pattern(
                position, duration_ms, motors, delay_ms
            )
        )
    
    def play_synchronized(self, lesson_config: Dict, delay_ms: float = 0):
        """Sync play with video synchronization"""
        return asyncio.run(
            self.controller.play_synchronized_multimodal(
                lesson_config, delay_ms
            )
        )
    
    def stop_all(self):
        """Sync stop all"""
        asyncio.run(self.controller.stop_all())


def threaded_play_haptics(
    controller: SyncHapticWrapper,
    lesson_config: Dict,
    delay_ms: float
):
    """
    Function to run in separate thread for Streamlit
    
    Args:
        controller: Synchronous haptic controller
        lesson_config: Haptic pattern configuration
        delay_ms: Calibration delay in milliseconds
    """
    try:
        result = controller.play_synchronized(lesson_config, delay_ms)
        print(f"Haptics played: {result}")
    except Exception as e:
        print(f"Error playing haptics: {e}")


def load_haptic_config(tact_file_path: str) -> Dict:
    """
    Load haptic configuration from .tact file
    
    Args:
        tact_file_path: Path to .tact file
    
    Returns:
        Dictionary with haptic configuration
    """
    try:
        with open(tact_file_path, 'r') as f:
            tact_data = json.load(f)
        
        # Extract relevant information
        # Adjust based on your actual .tact file structure
        project = tact_data.get('project', {})
        tracks = project.get('tracks', [])
        
        # Calculate duration from tracks
        duration_ms = 5000  # Default
        if tracks:
            # Find max duration from all tracks
            max_duration = 0
            for track in tracks:
                effects = track.get('effects', [])
                for effect in effects:
                    end_time = effect.get('startTime', 0) + effect.get('offsetTime', 0)
                    max_duration = max(max_duration, end_time)
            duration_ms = max_duration if max_duration > 0 else 5000
        
        return {
            'position': 8,  # Left glove
            'duration_ms': duration_ms,
            'motor_pattern': [100] * 6,  # Full intensity all motors
            'raw_data': tact_data
        }
    except Exception as e:
        print(f"Error loading haptic config: {e}")
        return {
            'position': 8,
            'duration_ms': 5000,
            'motor_pattern': [100] * 6
        }


# ============================================================================
# Streamlit Integration Functions
# ============================================================================

def initialize_haptic_system():
    """
    Initialize the haptic system in Streamlit session state
    Should be called once at app startup
    """
    if 'haptic_controller' not in st.session_state:
        # Create async controller
        async_controller = AsyncHapticController(
            BHAPTICS_CONFIG['app_id'],
            BHAPTICS_CONFIG['api_key'],
            BHAPTICS_CONFIG['app_name']
        )
        
        # Create sync wrapper
        sync_wrapper = SyncHapticWrapper(async_controller)
        
        # Initialize
        result = sync_wrapper.initialize()
        
        if result:
            st.session_state.haptic_controller = sync_wrapper
            st.session_state.haptic_initialized = True
            return True
        else:
            st.error("Failed to initialize haptic system!")
            return False
    
    return st.session_state.get('haptic_initialized', False)


def play_video_and_haptics(lesson_idx: int, tact_settings: Dict):
    """
    Trigger synchronized video and haptic playback
    
    Args:
        lesson_idx: Index of the lesson
        tact_settings: Dictionary mapping lesson indices to .tact files
    """
    # Get haptic controller
    if 'haptic_controller' not in st.session_state:
        st.error("Haptic system not initialized!")
        return
    
    controller = st.session_state.haptic_controller
    
    # Load haptic configuration
    tact_file = tact_settings.get(str(lesson_idx))
    if not tact_file:
        st.error(f"No haptic configuration for lesson {lesson_idx}")
        return
    
    haptic_config = load_haptic_config(tact_file)
    
    # Get calibration delay from session state
    delay_ms = st.session_state.get('calibration_delay_ms', 500)
    
    # Increment play count to trigger video reload
    st.session_state.play_count = st.session_state.get('play_count', 0) + 1
    
    # Start haptic playback in separate thread
    _executor.submit(
        threaded_play_haptics,
        controller,
        haptic_config,
        delay_ms
    )
    
    # Trigger Streamlit rerun to reload video
    st.rerun()


def create_calibration_ui():
    """
    Create UI for synchronization calibration
    Should be placed in sidebar or settings section
    """
    st.subheader("🎯 同期キャリブレーション")
    
    st.markdown("""
    ビデオと触覚の同期を調整します。
    
    - **遅延時間**: 触覚をビデオの後にどれくらい遅らせるか
    - **0ms**: 同時スタート
    - **500ms**: ビデオ開始から0.5秒後に触覚
    """)
    
    # Calibration slider
    delay_ms = st.slider(
        "触覚遅延時間 (ミリ秒)",
        min_value=0,
        max_value=2000,
        value=st.session_state.get('calibration_delay_ms', 500),
        step=50,
        help="値を調整してビデオと触覚が同期するようにします"
    )
    
    st.session_state.calibration_delay_ms = delay_ms
    
    # Display current settings
    st.info(f"現在の遅延: {delay_ms}ms ({delay_ms/1000:.2f}秒)")
    
    # Quick presets
    st.markdown("**プリセット:**")
    col1, col2, col3 = st.columns(3)
    
    if col1.button("同時", use_container_width=True):
        st.session_state.calibration_delay_ms = 0
        st.rerun()
    
    if col2.button("標準", use_container_width=True):
        st.session_state.calibration_delay_ms = 500
        st.rerun()
    
    if col3.button("遅め", use_container_width=True):
        st.session_state.calibration_delay_ms = 1000
        st.rerun()
    
    # Test button
    if st.button("🧪 同期テスト", use_container_width=True):
        if 'haptic_controller' in st.session_state:
            controller = st.session_state.haptic_controller
            test_config = {
                'position': 8,
                'duration_ms': 1000,
                'motor_pattern': [100] * 6
            }
            
            _executor.submit(
                threaded_play_haptics,
                controller,
                test_config,
                delay_ms
            )
            
            st.success(f"テスト実行: {delay_ms}ms 遅延")
        else:
            st.error("触覚システムが初期化されていません")


# ============================================================================
# Example Usage in echo_learning.py
# ============================================================================

def example_integration():
    """
    Example of how to integrate into your echo_learning.py
    """
    
    # At module initialization (replace old player initialization)
    # Initialize async haptic system
    initialize_haptic_system()
    
    # In your UI layout
    with st.sidebar:
        create_calibration_ui()
    
    # In your button handler (replace old threading code)
    # if my_grid.button("多感覚学習しよう!", use_container_width=True):
    #     play_video_and_haptics(lesson_idx, tact_settings)


if __name__ == "__main__":
    """
    Standalone test of the async haptic controller
    """
    
    async def test_async_controller():
        print("Testing Async Haptic Controller...")
        
        # Create controller
        controller = AsyncHapticController(
            BHAPTICS_CONFIG['app_id'],
            BHAPTICS_CONFIG['api_key'],
            BHAPTICS_CONFIG['app_name']
        )
        
        # Initialize
        print("Initializing...")
        result = await controller.initialize()
        print(f"Initialization result: {result}")
        
        if result:
            # Test pattern
            print("Playing test pattern on left glove...")
            test_config = {
                'position': 8,
                'duration_ms': 3000,
                'motor_pattern': [100] * 6
            }
            
            result = await controller.play_synchronized_multimodal(
                test_config,
                calibration_delay_ms=500
            )
            
            print(f"Playback result: {result}")
            
            # Wait for completion
            await asyncio.sleep(3.5)
            
            # Cleanup
            await controller.close()
            print("Test completed!")
        else:
            print("Failed to initialize controller")
    
    # Run test
    asyncio.run(test_async_controller())

import bhaptics_python
import asyncio
import time


async def haptic_demo():
    # 1. Initialization
    app_id = "your_app_id"
    api_key = "your_api_key"
    app_name = "Hello, bHaptics!"

    print("🔧 Initializing bHaptics SDK...")
    result = await bhaptics_python.registry_and_initialize(app_id, api_key, app_name)
    print(f"Initialization result: {result}")

    print("✅ Connected to bHaptics Player.")

    # 2. Check device information
    device_info = await bhaptics_python.get_device_info_json()
    print(f"📱 Connected device info: {device_info}")

    # # 3. Test haptic effects
    # print("\n🎮 Starting haptic effect tests...")

    # # Play dot pattern
    # print("• Playing dot pattern")
    # values = [50] * 16 + [0] * 16  # Activate first 16 of 32 motors
    # await bhaptics_python.play_dot(0, 2000, values)
    # await asyncio.sleep(2.5)

    # # Play path pattern
    # print("• Playing path pattern")
    # x = [0.2, 0.4, 0.6, 0.8]
    # y = [0.2, 0.8, 0.2, 0.8]
    # intensity = [80, 60, 80, 60]
    # await bhaptics_python.play_path(0, 3000, x, y, intensity)
    # await asyncio.sleep(3.5)

    # Test glove haptics (if available)
    print("• Testing glove haptics")
    
    # Left hand - 5 seconds vibration using play_dot
    # For TactGlove (position 8 = Left, 9 = Right), there are 6 motors
    glove_motors = [100] * 6  # All 6 motors at 100% intensity
    duration_ms = 5000  # 5 seconds = 5000 milliseconds
    
    print(f"  Left hand vibrating for {duration_ms}ms...")
    await bhaptics_python.play_dot(8, duration_ms, glove_motors)
    await asyncio.sleep(5.5)  # Wait for vibration to complete (5s + 0.5s buffer)

    # # Right hand
    # await bhaptics_python.play_glove(9, glove_motors, glove_playtimes, glove_shapes, 0)
    # await asyncio.sleep(1)

    # 4. Cleanup
    await bhaptics_python.stop_all()
    await bhaptics_python.close()
    print("🔚 Demo completed")


# Run the demo
if __name__ == "__main__":
    asyncio.run(haptic_demo())

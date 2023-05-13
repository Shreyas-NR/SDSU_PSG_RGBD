#####################################################
##               Read bag from file                ##
#####################################################


# First import library
import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import cv2
# Import argparse for command-line options
import argparse
# Import os.path for file path manipulation
import os.path
import matplotlib.pyplot as plt
i = 0
filename = '20230512_151113.bag'
try:
    # Create pipeline
    pipeline = rs.pipeline()

    # Create a config object
    config = rs.config()

    # Tell config that we will use a recorded device from file to be used by the pipeline through playback.
    rs.config.enable_device_from_file(config, file_name=filename, repeat_playback=False)


    # Configure the pipeline to stream the depth stream
    # Change this parameters according to the recorded bag file resolution
    config.enable_stream(rs.stream.depth)
    config.enable_stream(rs.stream.color)

    # Get stream profile and camera intrinsics
    
    profile = pipeline.start(config)

    profile = pipeline.get_active_profile()
    color_profile = rs.video_stream_profile(profile.get_stream(rs.stream.color))
    print(f'color_profile = {color_profile}')
    color_intrinsics = color_profile.get_intrinsics()
    print(f'color_intrinsics = {color_intrinsics}')    
    depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
    depth_intrinsics = depth_profile.get_intrinsics()
    print(f'depth_intrinsics = {depth_intrinsics}')
    # w, h = depth_intrinsics.width, depth_intrinsics.height

    # Start streaming from file
    # profile = pipeline.start(config)
    playback = profile.get_device().as_playback()  # get playback device
    playback.set_real_time(True)  # disable real-time playback

    # Create opencv window to render image in
    # cv2.namedWindow("Depth Stream", cv2.WINDOW_AUTOSIZE)
    # cv2.namedWindow("Color Stream", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Fused Stream", cv2.WINDOW_AUTOSIZE)

    # Create colorizer object
    colorizer = rs.colorizer(3)

    
    align_to = rs.stream.color
    align = rs.align(align_to)
    print("Finished Setup")
    # depth_to_disparity = rs.disparity_transform(True)
    # disparity_to_depth = rs.disparity_transform(False)
    # decimation = rs.decimation_filter()
    # spatial = rs.spatial_filter()
    # temporal = rs.temporal_filter()
    # hole_filling = rs.hole_filling_filter()

    # Streaming loop
    while True:
        # Get frameset of depth
        frames = pipeline.wait_for_frames()
        # playback.pause()
        
        # frames = align.process(frames)
        # Get depth frame
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        # print(f"size = {depth_frame.size()}")
        print(f"type of depth frame = {(color_frame)}")
        # print(f"type of depth frame = {(depth_frame)}")
        # Colorize depth frame to jet colormap
        # depth_color_frame = colorizer.colorize(depth_frame)

        # Convert depth_frame to numpy array to render image in opencv
        # depth_color_image = np.asanyarray(depth_color_frame.get_data())

        frame = depth_frame
        # frame = decimation.process(frame)
        # frame = depth_to_disparity.process(frame)
        # frame = spatial.process(frame)
        # frame = temporal.process(frame)
        # frame = disparity_to_depth.process(frame)
        # frame = hole_filling.process(frame)
        colorized_depth = np.asanyarray(colorizer.colorize(frame).get_data())
        color_image = np.asanyarray(color_frame.get_data())
        color_image = cv2.cvtColor(color_image,cv2.COLOR_BGR2RGB)
        fused = color_image+colorized_depth
        color_depth_fused = np.hstack((color_image, colorized_depth,  fused))
        i += 1
        # playback.resume()

        # Render image in opencv window
        # cv2.imshow("Depth Stream", depth_color_image)
        # cv2.imshow("Depth Stream", colorized_depth)
        # color_image = cv2.cvtColor(color_image,cv2.COLOR_BGR2RGB)
        # cv2.imshow("Color Stream", color_image)
        cv2.imshow("Fused Stream", color_depth_fused)
        key = cv2.waitKey(1)
        # if pressed escape exit program
        if key == 27:
            cv2.destroyAllWindows()
            break
except RuntimeError:
    print("No more frames left")
    print("Total Number of Frames in the bag file = ", i)
    cv2.destroyAllWindows()


finally:
    # Stop streaming
    pipeline.stop()
    print("pipeline stopped streaming")

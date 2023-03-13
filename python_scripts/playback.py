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
try:
    # Create pipeline
    pipeline = rs.pipeline()

    # Create a config object
    config = rs.config()

    # Tell config that we will use a recorded device from file to be used by the pipeline through playback.
    rs.config.enable_device_from_file(config, file_name='black2white.bag', repeat_playback=False)

    # Configure the pipeline to stream the depth stream
    # Change this parameters according to the recorded bag file resolution
    config.enable_stream(rs.stream.depth, rs.format.z16, 30)

    # Start streaming from file
    profile = pipeline.start(config)
    playback = profile.get_device().as_playback()  # get playback device
    playback.set_real_time(True)  # disable real-time playback

    # Create opencv window to render image in
    cv2.namedWindow("Depth Stream", cv2.WINDOW_AUTOSIZE)

    # Create colorizer object
    colorizer = rs.colorizer(3)
    print("Finished Setup")
    depth_to_disparity = rs.disparity_transform(True)
    disparity_to_depth = rs.disparity_transform(False)
    decimation = rs.decimation_filter()
    spatial = rs.spatial_filter()
    temporal = rs.temporal_filter()
    hole_filling = rs.hole_filling_filter()

    # Streaming loop
    while True:
        # Get frameset of depth
        frames = pipeline.wait_for_frames()
        # playback.pause()
        # Get depth frame
        depth_frame = frames.get_depth_frame()
        # print(f"size = {depth_frame.size()}")
        print(f"type of depth frame = {(depth_frame)}")
        # Colorize depth frame to jet colormap
        depth_color_frame = colorizer.colorize(depth_frame)

        # Convert depth_frame to numpy array to render image in opencv
        depth_color_image = np.asanyarray(depth_color_frame.get_data())

        frame = depth_frame
        # frame = decimation.process(frame)
        # frame = depth_to_disparity.process(frame)
        # frame = spatial.process(frame)
        # frame = temporal.process(frame)
        # frame = disparity_to_depth.process(frame)
        # frame = hole_filling.process(frame)
        colorized_depth = np.asanyarray(colorizer.colorize(frame).get_data())
        i += 1
        # playback.resume()

        # Render image in opencv window
        # cv2.imshow("Depth Stream", depth_color_image)
        cv2.imshow("Depth Stream", colorized_depth)
        key = cv2.waitKey(1)
        # if pressed escape exit program
        if key == 27:
            cv2.destroyAllWindows()
            break
except RuntimeError:
    print("No more frames left")
    print("Total Number of Frames in the bag file = ", i)


finally:
    # Stop streaming
    pipeline.stop()

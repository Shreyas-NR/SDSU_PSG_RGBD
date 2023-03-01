#####################################################
##           STREAM COLOR and DEPTH                ##
#####################################################


# First import library
import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import cv2
i = 0
try:
    # Create pipeline
    pipeline = rs.pipeline()

    # Create a config object
    config = rs.config()

    # Configure the pipeline to stream the color and depth stream
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start streaming
    pipeline.start(config)

    # Create opencv window to render image in
    cv2.namedWindow("Color & Depth Stream", cv2.WINDOW_AUTOSIZE)

    # Create colorizer object
    colorizer = rs.colorizer(3)
    print("Finished Setup")

    # Streaming loop
    while True:
        # Get frameset of depth
        frames = pipeline.wait_for_frames()
        # Get depth frame
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        # print(f"size = {depth_frame.size()}")
        # print(f"type of depth frame = {depth_frame}")

        # Colorize depth frame to jet colormap
        depth_color_frame = colorizer.colorize(depth_frame)

        # Convert depth_frame to numpy array to render image in opencv
        depth_color_image = np.asanyarray(depth_color_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # frame = depth_frame
        # colorized_depth = np.asanyarray(colorizer.colorize(frame).get_data())
        images = np.hstack((color_image, depth_color_image))
        # Render image in opencv window
        cv2.imshow("Color & Depth Stream", images)
        key = cv2.waitKey(1)
        # if pressed escape exit program
        if key == 27:
            cv2.destroyAllWindows()
            break
except RuntimeError:
    print("No more frames left")

finally:
    # Stop streaming
    pipeline.stop()

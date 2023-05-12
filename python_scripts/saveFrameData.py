import pyrealsense2 as rs
import numpy as np
import cv2
import datetime
today = datetime.date.today()
outDir = '../outputs/'
try:
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    pipeline.start(config)
    # cv2.namedWindow("Color & Depth Stream", cv2.WINDOW_AUTOSIZE)
    # Create colorizer object
    colorizer = rs.colorizer(3)
    align_to = rs.stream.color
    align = rs.align(align_to)
    # Streaming loop
    frames = pipeline.wait_for_frames()
    frames = align.process(frames)
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()

    depth_image = np.asanyarray(depth_frame.get_data())
    np.save('depthMartix.npy', depth_image)

    depth_color_frame = colorizer.colorize(depth_frame)

    # Convert depth_frame to numpy array to render image in opencv
    depth_color_image = np.asanyarray(depth_color_frame.get_data())
    color_image = np.asanyarray(color_frame.get_data())
    images = np.hstack((color_image, depth_color_image))
    fused = color_image*0.5+depth_color_image*0.5
    color_depth_fused = np.hstack((color_image, depth_color_image,  fused))
    # Render image in opencv window
    cv2.imwrite(outDir + str(today)+"_Color.png", color_image)
    cv2.imwrite(outDir + str(today)+"_Depth.png", depth_color_image)
    cv2.imwrite(outDir + str(today)+"_Color_Depth_Frame.png", images)
    cv2.imwrite(outDir + str(today)+"_Fused_Frame.png", fused)
    cv2.imwrite(outDir + str(today)+"_color_depth_fused.png", color_depth_fused)

except RuntimeError:
    print("No more frames left")

finally:
    # Stop streaming
    pipeline.stop()

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
outdir = '../outputs/'+ os.path.basename(filename).split('.')[0]
rgb = outdir+'/rgb/'
depth = outdir+'/depth/'
fused_dir = outdir+'/fused/'
if not os.path.exists(outdir):
    os.makedirs(outdir)
if not os.path.exists(rgb):
    os.makedirs(rgb)
if not os.path.exists(depth):
    os.makedirs(depth)
if not os.path.exists(fused_dir):
    os.makedirs(fused_dir)
try:
    # Create pipeline
    pipeline = rs.pipeline()

    # Create a config object
    config = rs.config()

    # Tell config that we will use a recorded device from file to be used by the pipeline through playback.
    rs.config.enable_device_from_file(config, file_name=filename, repeat_playback=False)


    # Configure the pipeline to stream the color and depth stream
    # Change this parameters according to the recorded bag file resolution
    config.enable_stream(rs.stream.depth)
    config.enable_stream(rs.stream.color)

    # Get stream profile and camera intrinsics
#********************************************************************************************************************************************************************
# color_profile = <pyrealsense2.video_stream_profile: Color(0) 640x480 @ 30fps RGB8>
# color_intrinsics = [ 640x480  p[317.637 245.76]  f[384.712 384.275]  Inverse Brown Conrady [-0.0553511 0.0643904 7.83417e-05 4.54708e-05 -0.0205691] ]
# depth_profile = <pyrealsense2.video_stream_profile: Depth(0) 640x480 @ 30fps Z16>
# depth_intrinsics = [ 640x480  p[319.044 242.822]  f[392.093 392.093]  Brown Conrady [0 0 0 0 0] ]
#********************************************************************************************************************************************************************
    profile = pipeline.start(config)

    profile = pipeline.get_active_profile()
    color_profile = rs.video_stream_profile(profile.get_stream(rs.stream.color))
    print(f'color_profile = {color_profile}')
    color_intrinsics = color_profile.get_intrinsics()
    print(f'color_intrinsics = {color_intrinsics}')    
    depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
    print(f'depth_profile = {depth_profile}')
    depth_intrinsics = depth_profile.get_intrinsics()
    print(f'depth_intrinsics = {depth_intrinsics}')
    # w, h = depth_intrinsics.width, depth_intrinsics.height

    # Start streaming from file
    # profile = pipeline.start(config)
    playback = profile.get_device().as_playback()  # get playback device
    playback.set_real_time(True)  # disable real-time playback

    # Create colorizer object
    colorizer = rs.colorizer(3)
    
    align_to = rs.stream.depth
    align = rs.align(align_to)
    print("Finished Setup")

    # Streaming loop
    while True:
        # Get frameset of depth
        frames = pipeline.wait_for_frames()
        frames = align.process(frames)
        # Get depth frame
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        depth_image = np.asanyarray(colorizer.colorize(depth_frame).get_data())
        color_image = np.asanyarray(color_frame.get_data())
        color_image = cv2.cvtColor(color_image,cv2.COLOR_BGR2RGB)
        fused = color_image+depth_image
        # np.save(depth+str(i)+'.npy', depth_image)
        # np.save(rgb+str(i)+'.npy', color_image)
        np.save(fused_dir+str(i)+'.npy', fused)
        # cv2.imwrite(depth+str(i)+'.png', depth_image)
        # cv2.imwrite(rgb+str(i)+'.png', color_image)
        # cv2.imwrite(fused_dir+str(i)+'.png', fused)
        # color_depth_fused = np.hstack((color_image, depth_image,  fused))
        i += 1

except RuntimeError:
    print("No more frames left")
    print("Total Number of Frames in the bag file = ", i)

finally:
    # Stop streaming
    pipeline.stop()
    print("pipeline stopped streaming")




import pyrealsense2 as rs
import numpy as np
import cv2
import os
from PIL import Image

filepath = '../inputs/20230525_202423.bag'   
filename =  os.path.basename(filepath).split('.')[0]
outdir = '../outputs/'+ os.path.basename(filepath).split('.')[0]

# Possible values for color_scheme
COLOR_SCHEMES = {
    'Jet': 0,
    'Classic': 1,
    'WhiteToBlack': 2,
    'BlackToWhite': 3,
    'Bio': 4,
    'Cold': 5,
    'Warm': 6,
    'Quantized': 7,
    'Pattern': 8
}

# Global list to store color_depth_fused frames
frames_list = []

def create_output_directories(outdir):
    rgb_dir = os.path.join(outdir, 'rgb')
    depth_dir = os.path.join(outdir, 'depth')
    aligned_rgbd_dir = os.path.join(outdir, 'aligned_rgbd')

    rgb_npy_dir = os.path.join(rgb_dir, 'npy')
    depth_npy_dir = os.path.join(depth_dir, 'npy')
    aligned_rgbd_npy_dir = os.path.join(aligned_rgbd_dir, 'npy')

    rgb_png_dir = os.path.join(rgb_dir, 'png')
    depth_png_dir = os.path.join(depth_dir, 'png')
    aligned_rgbd_png_dir = os.path.join(aligned_rgbd_dir, 'png')

    os.makedirs(outdir, exist_ok=True)

    os.makedirs(rgb_dir, exist_ok=True)
    os.makedirs(depth_dir, exist_ok=True)
    os.makedirs(aligned_rgbd_dir, exist_ok=True)

    os.makedirs(rgb_npy_dir, exist_ok=True)
    os.makedirs(depth_npy_dir, exist_ok=True)
    os.makedirs(aligned_rgbd_npy_dir, exist_ok=True)

    os.makedirs(rgb_png_dir, exist_ok=True)
    os.makedirs(depth_png_dir, exist_ok=True)
    os.makedirs(aligned_rgbd_png_dir, exist_ok=True)

    return outdir, rgb_npy_dir, depth_npy_dir, aligned_rgbd_npy_dir, rgb_png_dir, depth_png_dir, aligned_rgbd_png_dir


def save_frame_as_npy(frame, output_dir, frame_idx):
    npy_file = os.path.join(output_dir, f'{frame_idx+1}.npy')
    np.save(npy_file, frame)

def save_frames_as_npy(frames, output_dir):
    for frame_idx, frame in enumerate(frames):
        save_frame_as_npy(frame, output_dir, frame_idx)

def save_frame_as_png(frame, output_dir, frame_idx, type):
    png_file = os.path.join(output_dir, filename + '_C1_' + type + '_' + str(frame_idx+1).zfill(3) + '.png')
    image = Image.fromarray(frame)
    image.save(png_file)

def save_frames_as_png(frames, output_dir, type):
    for frame_idx, frame in enumerate(frames):
        save_frame_as_png(frame, output_dir, frame_idx, type)

def read_bag_file(filename, output_dir, save_npy=True, save_png=True, stream_frames=False):
    if not stream_frames:
        out_dir, rgb_npy_dir, depth_npy_dir, aligned_rgbd_npy_dir, rgb_png_dir, depth_png_dir, aligned_rgbd_png_dir = create_output_directories(output_dir)

    # Create pipeline
    pipeline = rs.pipeline()

    # Create a config object
    config = rs.config()

    # Tell config that we will use a recorded device from file to be used by the pipeline through playback.
    rs.config.enable_device_from_file(config, file_name=filename, repeat_playback=False)

    # Configure the pipeline to stream the depth stream
    config.enable_stream(rs.stream.depth)
    config.enable_stream(rs.stream.color)

    # Get stream profile and camera intrinsics
    profile = pipeline.start(config)

    profile = pipeline.get_active_profile()
    color_profile = rs.video_stream_profile(profile.get_stream(rs.stream.color))
    # print(f'color_profile = {color_profile}')
    color_intrinsics = color_profile.get_intrinsics()
    # print(f'color_intrinsics = {color_intrinsics}')    
    depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
    depth_intrinsics = depth_profile.get_intrinsics()
    # print(f'depth_intrinsics = {depth_intrinsics}')
    
    if not stream_frames:
        # Save the values in a text file
        output_file = os.path.join(out_dir, 'camera_intrinsics.txt')
        with open(output_file, 'w') as file:
            file.write(f'Color Profile: {color_profile}\n')
            file.write(f'Color Intrinsics: {color_intrinsics}\n')
            file.write(f'Depth Profile: {depth_profile}\n')
            file.write(f'Depth Intrinsics: {depth_intrinsics}\n')
        
    # Start streaming from file
    playback = profile.get_device().as_playback()
    playback.set_real_time(True)

    # Create opencv window to render image in if streaming frames
    if stream_frames:
        cv2.namedWindow("Fused Stream", cv2.WINDOW_AUTOSIZE)

    # Create colorizer object
    colorizer = rs.colorizer(COLOR_SCHEMES['BlackToWhite'])

    align_to = rs.stream.depth
    align = rs.align(align_to)
    print("Finished Setup")
            
    # Local list to store color,depth,fused frames
    depthColorizedFrames = []
    colorFrames = []
    depthFrames = []
    alignedRgbdFrames = []        
    
    # Counter for loop iterations
    loop_counter = 0
    print("Processing frames from the bag file ...")
    try:
        while True:
            # Get frameset of depth and color
            frames = pipeline.wait_for_frames()
            alignedFrames = align.process(frames)
            color_frame_unaligned = frames.get_color_frame() #unaligned
            depth_frame = alignedFrames.get_depth_frame()
            color_frame = alignedFrames.get_color_frame()

            depth_image_colorized = np.asanyarray(colorizer.colorize(depth_frame).get_data())
            depth_frame = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            color_image_unaligned = np.asanyarray(color_frame_unaligned.get_data())
            depth_frame = depth_frame.copy()
            depth_image_colorized = depth_image_colorized.copy()
            color_image = color_image.copy()
            color_image_unaligned = color_image_unaligned.copy()
            # color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
            color_image_u_cvt = cv2.cvtColor(color_image_unaligned, cv2.COLOR_BGR2RGB)
            fused = color_image + depth_image_colorized
            color_depth_fused = np.hstack((color_image_u_cvt, depth_image_colorized, fused))
            
            if not stream_frames:
                # Append the color_depth_fused frame to the list
                frames_list.append(color_depth_fused)
                colorFrames.append(color_image_unaligned)
                depthFrames.append(depth_frame)
                depthColorizedFrames.append(depth_image_colorized)
                alignedRgbdFrames.append(color_image)
                # frames_list.append(color_depth_fused.copy())
                # colorFrames.append(color_image.copy())
                # depthFrames.append(depth_frame.copy())
                # depthColorizedFrames.append(depth_image_colorized.copy())
                # fusedFrames.append(fused.copy())
            else:
                # Render image in opencv window
                cv2.imshow("Fused Stream", color_depth_fused)
                key = cv2.waitKey(1)

                # If pressed escape, exit the program
                if key == 27:
                    cv2.destroyAllWindows()
                    break           
            # Increment the loop counter
            loop_counter += 1

    except RuntimeError:
        print("No more frames left")
        print("Total Number of Frames in the bag file = ", loop_counter)
        cv2.destroyAllWindows()


    finally:
        # Stop streaming
        pipeline.stop()
        print("Pipeline stopped streaming")

        if save_npy:
            print("Downloading NPY & PNG files to the output directory")
            save_frames_as_npy(alignedRgbdFrames, aligned_rgbd_npy_dir)
            save_frames_as_npy(colorFrames, rgb_npy_dir)
            save_frames_as_npy(depthFrames, depth_npy_dir)

        if save_png:
            save_frames_as_png(alignedRgbdFrames, aligned_rgbd_png_dir, type = 'rgbd')
            save_frames_as_png(colorFrames, rgb_png_dir, type = 'rgb')
            save_frames_as_png(depthColorizedFrames, depth_png_dir, type = 'depth')


def write_frames_to_video(frames, output_file):
    color_depth_fused = frames_list[0]  # Get the first frame from the list
    height, width, _ = color_depth_fused.shape

    # Define the video writer
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_file, fourcc, 30.0, (width, height))

    # Write each frame to the video file
    for frame in frames:
        out.write(frame)

    # Release the video writer
    out.release()

def main():

    # Prompt the user to choose streaming or saving frames
    # choice = input("Enter '1' to stream frames or '2' to save frames: ")
    choice = '1'

    if choice == '1':
    # Stream frames
        read_bag_file(filepath, outdir, save_npy=False, save_png=False, stream_frames=True)
    elif choice == '2':
        # Save frames
        read_bag_file(filepath, outdir, save_npy=True, save_png=True, stream_frames=False)

        # Write the frames from the list to a video file
        output_file = outdir+'/color_depth_fused.avi'
        print(f"Writing video, wait for completion! ")
        write_frames_to_video(frames_list, output_file)
        print(f"Output Video available at {output_file} \nDONE")
    else:
        print("Invalid choice. Exiting...")

if __name__ == '__main__':
    main()

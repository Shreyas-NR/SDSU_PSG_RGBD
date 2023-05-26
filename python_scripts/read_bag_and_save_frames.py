import os
import pyrealsense2 as rs
import numpy as np
import cv2

# Global list to store color_depth_fused frames
frames_list = []

def read_bag_file(filename, output_dir, stream_frames):
    try:
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
        print(f'color_profile = {color_profile}')
        color_intrinsics = color_profile.get_intrinsics()
        print(f'color_intrinsics = {color_intrinsics}')    
        depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
        depth_intrinsics = depth_profile.get_intrinsics()
        print(f'depth_intrinsics = {depth_intrinsics}')
        
        # Save the values in a text file
        output_file = os.path.join(output_dir, 'camera_intrinsics.txt')
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
        colorizer = rs.colorizer(3)

        align_to = rs.stream.depth
        align = rs.align(align_to)
        print("Finished Setup")
        
        # Counter for loop iterations
        loop_counter = 0
        
        while True:
            # Get frameset of depth and color
            frames = pipeline.wait_for_frames()
            frames = align.process(frames)
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            frame = depth_frame
            colorized_depth = np.asanyarray(colorizer.colorize(frame).get_data())
            color_image = np.asanyarray(color_frame.get_data())
            color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
            fused = color_image + colorized_depth
            color_depth_fused = np.hstack((color_image, colorized_depth, fused))
            
            # Append the color_depth_fused frame to the list
            frames_list.append(color_depth_fused)

            if stream_frames:
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
        print("Total number of Frames:", loop_counter)
        cv2.destroyAllWindows()


    finally:
        # Stop streaming
        pipeline.stop()
        print("Pipeline stopped streaming")

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
    filename = '../inputs/20230512_151113.bag'    
    outdir = '../outputs/'+ os.path.basename(filename).split('.')[0]
    
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # Prompt the user to choose streaming or saving frames
    choice = input("Enter '1' to stream frames or '2' to save frames: ")

    if choice == '1':
        # Stream frames
        read_bag_file(filename, outdir, stream_frames=True)
    elif choice == '2':
        # Save frames
        read_bag_file(filename, outdir, stream_frames=False)

        # Write the frames from the list to a video file
        output_file = outdir+'/color_depth_fused.avi'
        write_frames_to_video(frames_list, output_file)
    else:
        print("Invalid choice. Exiting...")

if __name__ == '__main__':
    main()
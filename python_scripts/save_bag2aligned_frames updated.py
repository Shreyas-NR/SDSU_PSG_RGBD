import pyrealsense2 as rs
import numpy as np
import cv2
import os
from PIL import Image
import tqdm

def create_output_directories(outdir):
    rgb_dir = os.path.join(outdir, 'rgb')
    depth_dir = os.path.join(outdir, 'depth')
    fused_dir = os.path.join(outdir, 'fused')

    rgb_npy_dir = os.path.join(rgb_dir, 'npy')
    depth_npy_dir = os.path.join(depth_dir, 'npy')
    fused_npy_dir = os.path.join(fused_dir, 'npy')

    rgb_png_dir = os.path.join(rgb_dir, 'png')
    depth_png_dir = os.path.join(depth_dir, 'png')
    fused_png_dir = os.path.join(fused_dir, 'png')

    os.makedirs(outdir, exist_ok=True)

    os.makedirs(rgb_dir, exist_ok=True)
    os.makedirs(depth_dir, exist_ok=True)
    os.makedirs(fused_dir, exist_ok=True)

    os.makedirs(rgb_npy_dir, exist_ok=True)
    os.makedirs(depth_npy_dir, exist_ok=True)
    os.makedirs(fused_npy_dir, exist_ok=True)

    os.makedirs(rgb_png_dir, exist_ok=True)
    os.makedirs(depth_png_dir, exist_ok=True)
    os.makedirs(fused_png_dir, exist_ok=True)

    return outdir, rgb_npy_dir, depth_npy_dir, fused_npy_dir, rgb_png_dir, depth_png_dir, fused_png_dir


def save_frame_as_npy(frame, output_dir, frame_idx):
    npy_file = os.path.join(output_dir, f'{frame_idx}.npy')
    np.save(npy_file, frame)

def save_frame_as_png(frame, output_dir, frame_idx):
    png_file = os.path.join(output_dir, f'{frame_idx+1}.png')
    image = Image.fromarray(frame)
    image.save(png_file)

def save_frames_as_png(frames, output_dir):
    for frame_idx, frame in tqdm(enumerate(frames)):
        save_frame_as_png(frame, output_dir, frame_idx)

def read_bag_file(filename, outdir, save_npy=True, save_png=True):
    out_dir, rgb_npy_dir, depth_npy_dir, fused_npy_dir, rgb_png_dir, depth_png_dir, fused_png_dir = create_output_directories(outdir)

    pipeline = rs.pipeline()
    config = rs.config()
    rs.config.enable_device_from_file(config, file_name=filename, repeat_playback=False)
    config.enable_stream(rs.stream.depth)
    config.enable_stream(rs.stream.color)

    profile = pipeline.start(config)
    playback = profile.get_device().as_playback()
    playback.set_real_time(True)

    colorizer = rs.colorizer(3)
    align_to = rs.stream.depth
    align = rs.align(align_to)

    colorFrames = []
    depthFrames = []
    fusedFrames = []
    try:
        while True:
            frame_set = pipeline.wait_for_frames()
            frame_set = align.process(frame_set)
            depth_frame = frame_set.get_depth_frame()
            color_frame = frame_set.get_color_frame()

            depth_image = np.asanyarray(colorizer.colorize(depth_frame).get_data())
            color_image = np.asanyarray(color_frame.get_data())
            color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
            fused = color_image + depth_image

            colorFrames.append(color_image)
            depthFrames.append(depth_image)
            fusedFrames.append(fused)

            if save_npy:
                save_frame_as_npy(depth_image, depth_npy_dir, len(depthFrames))
                save_frame_as_npy(color_image, rgb_npy_dir, len(colorFrames))
                save_frame_as_npy(fused, fused_npy_dir, len(fusedFrames))

    except RuntimeError:
        print("No more frames left")
        print("Total Number of Frames in the bag file = ", len(fusedFrames))

    finally:
        pipeline.stop()
        print("pipeline stopped streaming")
        print("Downloading PNG files to the output directory")

        if save_png:
            save_frames_as_png(fusedFrames, fused_png_dir)
            save_frames_as_png(colorFrames, rgb_png_dir)
            save_frames_as_png(depthFrames, depth_png_dir)

def main():
    filename = '../inputs/20230512_151113.bag'    
    outdir = '../outputs/' + os.path.basename(filename).split('.')[0]
    read_bag_file(filename, outdir, save_npy=True, save_png=True)

if __name__ == '__main__':
    main()

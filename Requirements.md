# Dataset Requirement Documentation:
## Required Tools:
### Hardware:
1. Intel RealSense D455 - 2
2. USB-C
3. Windows PC

### Software:
1. Intel Realsense Viewer - https://github.com/IntelRealSense/librealsense/releases/download/v2.49.0/Intel.RealSense.Viewer.exe

## Camera view point options:
1. C1 at 0&deg; and C2 at 90&deg;.
2. C1 at -25&deg; and C2 at 25&deg;.
3. C1 front view and C2 Top view.

## Video Stream Settings:
1. Synchronize C1 and C2 RGBD frames. (ref. hardware timestamp) https://dev.intelrealsense.com/docs/frame-management#frame-syncer
2. Synchronize/Aligned RGB and Depth frames of each camera. https://dev.intelrealsense.com/docs/projection-in-intel-realsense-sdk-20#frame-alignment
3. Frame Dimensions: 640x480 (WxH) @ 60fps
4. Internal queue size = 1  (attempt to reduce the frame drops)
5. use

## Camera Parameters:
1. Intrinsic camera parameters: https://dev.intelrealsense.com/docs/projection-in-intel-realsense-sdk-20#intrinsic-camera-parameters
2. Extrinsic camera parameters: https://dev.intelrealsense.com/docs/projection-in-intel-realsense-sdk-20#extrinsic-camera-parameters
3. focal length
4. 

## Key details to be recorde:
1. The actual distance between the camera and the participant should be recorded.
2. 

## Action Classes:
1. Normal Walking
2. Sitting on a couch
3. Getting off the couch
4. Stumble
5. Faint
6. Fall
7. Hazardous Pose in workplace environment
8. 

## Data:
1. Data should be divided into Train, Validation adn Test.
2. 

## Annotation:
1. Tool: TBD (openVino)
2. Boundary box per person in frame [Xmin, Ymin, Xmax, Ymax]
3. 15 keypoints = 
 `{
    0: 'Head',
    1: 'Neck',
    2: 'RShoulder',
    3: 'LShoulder',
    4: 'RElbow',
    5: 'LElbow',
    6: 'RHand',
    7: 'LHand',
    8: 'Torso',
    9: 'RHip',
    10: 'LHip',
    11: 'RKnee',
    12: 'LKnee',
    13: 'RFoot',
    14: 'LFoot',
}`
3. 2D and 3D coordinates
4. json file with the following format
`{
    "00164619.npy": [
        {
            "2d_joints": [
                [
                    190.61955933681884,
                    145.41395092378787
                ],
                	          :
                [
                    214.73146019386365,
                    443.0391164643001
                ]
            ],
            "3d_joints": [
                [
                    -0.17909864807128906,
                    -0.7632066040039063,
                    2.195555908203125
                ],
    	                      :
                [
                    -0.08426995849609376,
                    0.6065158081054688,
                    2.497370361328125
                ]
            ],
            "bbox": [
                21,
                76,
                331,
                486
            ],            
        }
    ],
}
`
4. TBD
5. 

## Naming Convention:
- TBD





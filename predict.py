from cog import BasePredictor, Input, Path
import os
import math
import zipfile
import tempfile
from pathlib import Path as PathLib
from moviepy.editor import VideoFileClip

class Predictor(BasePredictor):
    def setup(self):
        """Load the model into memory to make running multiple predictions efficient"""
        # Initialize any required variables

    def predict(
        self,
        input_video: Path = Input(description="Input video file (MP4 or MOV)"),
        target_duration: float = Input(
            description="Target duration for each segment in seconds",
            default=2.0,
            ge=1.0,
            le=10.0,
        ),
        target_width: int = Input(description="Target width for each segment", default=848, ge=320, le=1920),
        target_height: int = Input(description="Target height for each segment", default=480, ge=240, le=1080),
        target_fps: int = Input(description="Target FPS for each segment", default=30, ge=1, le=60),
        create_captions: bool = Input(
            description="Create empty caption files for each segment",
            default=False,
        ),
    ) -> Path:
        """Run video preprocessing and return a zip file containing processed segments"""
        # Create temporary directories for processing
        with tempfile.TemporaryDirectory() as output_dir:
            output_path = PathLib(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            try:
                # Load video
                video = VideoFileClip(str(input_video))
                
                # Skip if video is too short
                if video.duration < target_duration:
                    raise ValueError(f"Video too short ({video.duration:.1f}s < {target_duration}s)")
                
                # Calculate number of segments
                num_segments = math.floor(video.duration / target_duration)
                print(f"Splitting video into {num_segments} segments")
                
                # Process each segment
                for segment_idx in range(num_segments):
                    # Calculate segment time range
                    start_time = segment_idx * target_duration
                    end_time = start_time + target_duration
                    
                    # Setup output paths for this segment
                    segment_name = f"segment{segment_idx+1}.mp4"
                    output_file = output_path / segment_name
                    
                    # Extract segment
                    segment = video.subclip(start_time, end_time)
                    
                    # Calculate dimensions to maintain aspect ratio
                    target_ratio = target_width / target_height
                    current_ratio = video.w / video.h
                    
                    if current_ratio > target_ratio:
                        # Video is wider - crop width
                        new_width = int(video.h * target_ratio)
                        x1 = (video.w - new_width) // 2
                        final = segment.crop(x1=x1, width=new_width)
                    else:
                        # Video is taller - crop height
                        new_height = int(video.w / target_ratio)
                        y1 = (video.h - new_height) // 2
                        final = segment.crop(y1=y1, height=new_height)
                    
                    # Resize to target resolution
                    final = final.resize((target_width, target_height))
                    final = final.set_fps(target_fps)
                    
                    # Configure output settings
                    output_params = {
                        "codec": "libx264",
                        "audio": False,
                        "preset": "medium",
                        "bitrate": "5000k",
                    }
                    
                    # Save processed segment
                    final.write_videofile(str(output_file), **output_params)
                    
                    # Create placeholder caption file if requested
                    if create_captions:
                        caption_file = output_path / f"segment{segment_idx+1}.txt"
                        caption_file.touch()
                    
                    # Cleanup segment
                    segment.close()
                    final.close()
                
                # Cleanup original video
                video.close()
                
                # Create zip file
                zip_path = "/tmp/processed_videos.zip"
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Add all files from the output directory
                    for root, dirs, files in os.walk(output_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, output_dir)
                            zipf.write(file_path, arcname)
                
                return Path(zip_path)
                
            except Exception as e:
                raise Exception(f"Error processing video: {str(e)}")
# MushroomFleet/Mochi1-Video-Dataset-BuilderCog Model

This is an implementation of [MushroomFleet/Mochi1-Video-Dataset-Builder](https://github.com/MushroomFleet/Mochi1-Video-Dataset-Builder) as a [Cog](https://github.com/replicate/cog) model for LoRA inference.

## Development

Follow the [model pushing guide](https://replicate.com/docs/guides/push-a-model) to push your own model to [Replicate](https://replicate.com).


## How to use

Make sure you have [cog](https://github.com/replicate/cog) installed.

To run a prediction:

    cog predict -i input_video=@vhs.mp4


## Output

    processed_videos.zip
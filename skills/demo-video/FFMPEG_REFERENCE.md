# ffmpeg & Audio Reference

Critical rules and lessons learned for assembling demo video segments.

## Audio

1. **NEVER overlap music and voice.** Music plays only during intro/outro slides. Voice-only during video acts. No background music under narration.

2. **Intro music structure:** Music fades in and fades out within its duration (e.g., 5s), THEN voice starts. Use `atrim` to cut music to exact duration, `afade` for fade in/out, then `amix` with the delayed VO. Since music ends before VO starts, there is no overlap.
   ```
   [music]atrim=0:5,afade=t=in:st=0:d=2.5,afade=t=out:st=2.5:d=2.5,volume=0.35[music];
   [vo]adelay=5000|5000[vo];
   [music][vo]amix=inputs=2:duration=longest:normalize=0[aout]
   ```

3. **All segments MUST output stereo audio (2 channels).** ElevenLabs outputs mono MP3. If some segments are mono and others stereo, concatenation produces audio glitches (voice from one side, artifacts on the other). Fix with `pan=stereo|c0=c0|c1=c0` in the filter chain and `-ac 2` in output flags.

4. **Add 300ms voice delay in video segments.** Without a delay, the voice starts slightly before the visual transition at act boundaries. Use `adelay=300|300` at the start of the VO filter chain.

5. **Full audio filter chain for video segments:**
   ```
   [1:a]adelay=300|300,aresample=async=1,apad=pad_dur={duration},pan=stereo|c0=c0|c1=c0[aout]
   ```

## Video

6. **Freeze-frame extension.** When VO is longer than the video segment, pad with last frame using `tpad=stop_mode=clone:stop_duration={pad_time}`.

7. **Scale and pad to target resolution.** Source video may not be 1920x1080:
   ```
   scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2
   ```

8. **Consistent encoding across all segments.** Every segment must use:
   ```
   -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -r 25
   -c:a aac -ac 2 -b:a 192k
   ```

## Concatenation

9. **Always re-encode on concat.** Using `-c copy` with concat causes audio/video sync drift at segment boundaries. Always re-encode:
   ```
   ffmpeg -y -f concat -safe 0 -i concat.txt \
     -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -r 25 \
     -c:a aac -ac 2 -b:a 192k output.mp4
   ```

## Slides

10. **Use PIL (Pillow) for slide generation, not ffmpeg drawtext.** macOS ffmpeg often lacks the freetype/drawtext filter. PIL with system fonts (`/System/Library/Fonts/Helvetica.ttc`) works reliably.

11. **Logo color inversion for outro.** If the source logo is colored on transparent, iterate pixels and set all non-transparent pixels to white (or desired color) while preserving alpha.

import bpy
import os
from pathlib import Path


def get_camera_frame_range(camera):
    """
    Determine the animation frame range for a camera.
    Returns (start, end) if keyframes exist, otherwise None.
    """
    frames = []
    anim_data = camera.animation_data
    if anim_data and anim_data.action:
        for fcurve in anim_data.action.fcurves:
            for kp in fcurve.keyframe_points:
                frames.append(int(kp.co.x))
    if frames:
        return min(frames), max(frames)
    return None


def render_all_cameras():
    scene = bpy.context.scene

    # Backup original settings
    original_camera = scene.camera
    original_filepath = scene.render.filepath
    original_start = scene.frame_start
    original_end = scene.frame_end

    # Resolve user output directory
    user_path = bpy.path.abspath(original_filepath)
    output_root = Path(os.path.dirname(user_path))

    # Create main folder for camera renders
    main_folder = output_root / "Camera_Renders"
    main_folder.mkdir(parents=True, exist_ok=True)

    try:
        for cam_obj in (obj for obj in bpy.data.objects if obj.type == 'CAMERA'):
            if cam_obj.hide_render:
                continue  # Skip cameras marked not to render

            frame_range = get_camera_frame_range(cam_obj)
            if frame_range is None:
                continue  # Skip cameras with no keyframes

            start_frame, end_frame = frame_range

            # Create folder per camera
            cam_folder = main_folder / cam_obj.name
            cam_folder.mkdir(exist_ok=True)

            # Apply settings for this camera
            scene.camera = cam_obj
            scene.frame_start = start_frame
            scene.frame_end = end_frame
            scene.render.filepath = str(cam_folder / f"{cam_obj.name}_")

            print(f"Rendering camera '{cam_obj.name}' from frame {start_frame} to {end_frame}...")
            bpy.ops.render.render(animation=True)

    finally:
        # Restore original settings
        scene.camera = original_camera
        scene.render.filepath = original_filepath
        scene.frame_start = original_start
        scene.frame_end = original_end
        print("Restored original scene settings.")


if __name__ == '__main__':
    render_all_cameras()

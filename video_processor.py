from polars import dataframe
from cProfile import label
from torch._inductor.codegen.cpp import OuterLoopFusedKernel
from networkx.algorithms.bipartite import color
import cv2
import imageio_ffmpeg
import pandas as pd 
import os 
import subprocess
import tempfile

from detectionm import pee_dection
from tracker import PersonTracker
from violation_checker import check_ppe

def process_video(input_path , output_path):
    output_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_dir, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    detector = pee_dection("models/best.pt")
    tracker = PersonTracker("models/best.pt")

    cap  = cv2.VideoCapture(input_path)
    if not cap .isOpened():
        raise ValueError("could not open uploaded video")
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if fps <= 0:
        fps = 25
    with tempfile.NamedTemporaryFile(
        dir=output_dir,
        suffix=".mp4",
        delete=False
    ) as temp_file:
        intermediate_path = temp_file.name
    os.remove(intermediate_path)
    with tempfile.NamedTemporaryFile(
        dir=output_dir,
        suffix=".mp4",
        delete=False
    ) as temp_file:
        converted_path = temp_file.name
    os.remove(converted_path)

    writer = cv2.VideoWriter(
        intermediate_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height)
    )

    if not writer.isOpened():
        cap.release()
        os.remove(intermediate_path)
        os.remove(converted_path)
        raise ValueError("Could not create the intermediate output video.")
    records = []
    max_people =0
    frame_number = 0 

    try:
        try:
            while True:
                succes , frame = cap.read()
                if not succes:
                    break

                frame_number += 1 
                detectio = detector.detect_object(frame)
                people, total_seen, current_count = tracker.track(frame)
                max_people = max(max_people , current_count)
                for person in people: 
                    person_id = person["id"]
                    box = tuple(map(int , person["box"]))
                    status = check_ppe(box , detectio)
                    helmet = status["helmet"]
                    vest = status["vest"]

                    if "Violation" in [helmet , vest]:
                        overall = "Violation"
                        color = (0,0,255)
                    elif "Needs Review" in [helmet , vest]:
                        overall = "Needs Review"
                        color = (0,165,255)
                    else: 
                        overall = "Compliant"
                        color = (0,255,0)
                    x1 , y1, x2, y2 = box 
                    cv2. rectangle(
                        frame,
                        (x1,y1),
                        (x2 , y2),
                        color,
                        2
                    )

                    label = (
                        f"ID {person_id} | "
                        f"H:{helmet} | V:{vest}"
                    )

                    cv2. putText(
                        frame,
                        label,
                        (x1, max(20, y1-10)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color , 2
                    )
                    records.append({
                        "frame":frame_number,
                        "person_id":person_id,
                        "helmet":helmet,
                        "vest":vest,
                        "overall_status":overall
                    })
                cv2.putText(
                    frame,
                    f"people in farms : {current_count}",
                    (20,35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (255, 255, 0),
                    2
                )
                writer.write(frame)
        finally:
            cap.release()
            writer.release()

        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-i", intermediate_path,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                converted_path,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        os.replace(converted_path, output_path)
    except subprocess.CalledProcessError as error:
        details = error.stderr.strip() if error.stderr else str(error)
        raise RuntimeError(f"FFmpeg could not encode the H.264 output: {details}") from error
    finally:
        if os.path.exists(intermediate_path):
            os.remove(intermediate_path)
        if os.path.exists(converted_path):
            os.remove(converted_path)

    dataframe = pd.DataFrame(records)
    return dataframe,{
        "unique_tracked_ids":len(tracker.unique_id),
        "maximum_people_in_frame":max_people,
        "processed_frames":frame_number
    }
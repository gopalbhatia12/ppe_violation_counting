import cv2
from tracker import PersonTracker

# Initialize tracker
tracks = PersonTracker("models/best.pt")

# Open test video
cap = cv2.VideoCapture("Test/5434223-hd_1920_1080_24fps.mp4")

if not cap.isOpened():
    print("ERROR: Cannot open test_video.mp4")
    exit()

frame_number = 0

print("Starting ByteTrack test...")

while True:

    success, frame = cap.read()

    if not success:
        break

    frame_number += 1

    # Run tracking
    people, total_seen, current_count = tracks.track(frame)

    print(
        f"Frame: {frame_number} | "
        f"People: {current_count} | "
        f"Unique IDs: {total_seen}"
    )

    # Display IDs on video
    for person in people:

        x1, y1, x2, y2 = map(int, person["box"])
        person_id = person["id"]

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"ID: {person_id}",
            (x1, max(20, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    # Display video
    cv2.imshow("ByteTrack Person Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

print("\n========== FINAL RESULTS ==========")
print("Frames processed:", frame_number)
print("Unique tracked IDs:", len(tracks.unique_id))
print("ByteTrack test completed!")

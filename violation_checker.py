
def calculate_overlap(box, region):
    """
    Calculate the percentage of the PPE bounding box
    that overlaps with the person's body region.
    """
    x1, y1, x2, y2 = box
    rx1, ry1, rx2, ry2 = region

    ix1 = max(x1, rx1)
    ix2 = max(x2 , rx2)
    iy1 = max(y1, ry1)
    iy2 = max(y1, ry2)

    if ix2 <= ix1 or iy2<= iy1:
        return 0.0
    intersection = (ix2-ix1)*(iy2 - iy1)
    box_area = max(1, (x2 - x1) * (y2 - y1))
    return intersection/box_area

def check_ppe(person_box, detections):

    x1, y1, x2, y2 = person_box

    height = y2 - y1
    width = x2 - x1

    if width <= 0 or height <= 0:
        return {
            "helmet": "Needs Review",
            "vest": "Needs Review"
        }
    
    # Approximate head and torso regions
    head_region = (
        x1 - width * 0.10,
        y1 - height * 0.05,
        x2 + width * 0.10,
        y1 + height * 0.40
    )

    torso_region = (
        x1 - width * 0.10,
        y1 + height * 0.20,
        x2 + width * 0.10,
        y1 + height * 0.85
    )

    helmet_found = False
    no_helmet_found = False
    vest_found = False
    no_vest_found = False

    for detection in detections:

        name = detection["class"].lower()
        box = detection["box"]

        if name in ["helmet", "no_helmet"]:
            if calculate_overlap(box, head_region)>= 0.25:
                if name == "helmet":
                    helmet_found = True
                else:
                    no_helmet_found = True

        if name in ["vest", "no_vest"]:
            if calculate_overlap(box, torso_region)>=0.25:
                if name == "vest":
                    vest_found = True
                else:
                    no_vest_found = True

     # Helmet decision
    if helmet_found and not no_helmet_found:
        helmet_status = "Safe"
    elif no_helmet_found and not helmet_found:
        helmet_status = "Violation"
    elif helmet_found and no_helmet_found:
        helmet_status = "Needs Review"
    else:
        helmet_status = "Needs Review"

    # Vest decision
    if vest_found and not no_vest_found:
        vest_status = "Safe"
    elif no_vest_found and not vest_found:
        vest_status = "Violation"
    elif vest_found and no_vest_found:
        vest_status = "Needs Review"
    else:
        vest_status = "Needs Review"

    return {
        "helmet": helmet_status,
        "vest": vest_status
    }
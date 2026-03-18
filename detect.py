from ultralytics import YOLO
import cv2
import easyocr
import re
import mysql.connector



db = mysql.connector.connect(
    host = "127.0.0.1",
    user="root",
    password="route",
    database="vehicle_db"
)

cursor = db.cursor()
# load YOLO model
model = YOLO("best.pt")

# read image
image = cv2.imread(r"E:\DL Datasets\YOLO Number plate\ciaz.jpg")

# run detection
results = model(image)

reader = easyocr.Reader(['en'])

for r in results:
    boxes = r.boxes.xyxy

    for box in boxes:
        x1, y1, x2, y2 = map(int, box)

        # crop plate
        plate = image[y1:y2, x1:x2]

        # resize plate (important for OCR)
        plate = cv2.resize(plate, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

        # preprocessing
        gray = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)

        blur = cv2.GaussianBlur(gray,(5,5),0)

        thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]

        # OCR
        result = reader.readtext(thresh)

        for detection in result:
            plate_number = detection[1]

            # clean plate text
            plate_number = re.sub('[^A-Z0-9]', '', plate_number)

            print("Detected Plate:", plate_number)
            
            query = "SELECT * FROM vehicle_info WHERE registration = %s"

            cursor.execute(query, (plate_number,))

            result_db = cursor.fetchone()

            if result_db:
                print("\nVehicle Owner Details")
                print("----------------------")
                print("Registration:", result_db[0])
                print("Owner Name:", result_db[1])
                print("House Name:", result_db[2])
                print("Place:", result_db[3])
                print("Phone:", result_db[4])
            else:
                print("Vehicle not found in database")

        # draw box
        cv2.rectangle(image,(x1,y1),(x2,y2),(0,255,0),2)

        # show plate
        cv2.imshow("Plate", plate)

cv2.imshow("Detection", image)

cv2.waitKey(0)
cv2.destroyAllWindows()
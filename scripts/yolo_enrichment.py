import os
import json
import glob
import psycopg2
from ultralytics import YOLO
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

RAW_IMAGE_PATH = "data/raw/telegram_images"

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )

def create_image_detections_table(conn):
    """Creates the fct_image_detections table if it doesn't exist."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE SCHEMA IF NOT EXISTS marts;
            CREATE TABLE IF NOT EXISTS marts.fct_image_detections (
                detection_id SERIAL PRIMARY KEY,
                message_id BIGINT NOT NULL,
                detected_object_class TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                bounding_box JSONB,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
    print("Fact table 'marts.fct_image_detections' ensured.")

def run_yolo_detection(image_path):
    """Runs YOLOv8 detection on an image and returns results."""
    model = YOLO('yolov8n.pt')  # Load a pre-trained YOLOv8n model
    results = model(image_path)

    detections = []
    for r in results:
        for box in r.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            xyxy = box.xyxy[0].tolist() # Bounding box coordinates [x1, y1, x2, y2]

            # Get class name
            class_name = model.names[class_id]

            detections.append({
                "detected_object_class": class_name,
                "confidence_score": confidence,
                "bounding_box": {
                    "x1": xyxy[0], "y1": xyxy[1], "x2": xyxy[2], "y2": xyxy[3]
                }
            })
    return detections

def process_image_for_detection(image_file_path, message_id):
    """Processes a single image file, runs YOLO, and loads results to DB."""
    conn = None
    try:
        conn = get_db_connection()
        create_image_detections_table(conn)

        print(f"Processing image: {image_file_path} for message ID: {message_id}")
        detections = run_yolo_detection(image_file_path)

        with conn.cursor() as cur:
            for det in detections:
                cur.execute("""
                    INSERT INTO marts.fct_image_detections (
                        message_id, detected_object_class, confidence_score, bounding_box
                    ) VALUES (%s, %s, %s, %s);
                """, (
                    message_id,
                    det['detected_object_class'],
                    det['confidence_score'],
                    json.dumps(det['bounding_box'])
                ))
            conn.commit()
        print(f"Loaded {len(detections)} detections for message ID {message_id}.")
    except Exception as e:
        print(f"Error processing image {image_file_path}: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def main():
    """Scans for new images and runs YOLO detection."""
    print("Starting YOLOv8 image enrichment...")
    # This is a simplified glob. In a real scenario, you'd track processed images
    # or use a more robust way to find 'new' images.
    # Assuming image files are named like message_id.jpg
    image_files = glob.glob(os.path.join(RAW_IMAGE_PATH, '**/*.jpg'), recursive=True)

    for img_path in image_files:
        try:
            # Extract message_id from filename (e.g., 12345.jpg -> 12345)
            message_id_str = os.path.splitext(os.path.basename(img_path))[0]
            message_id = int(message_id_str)
            process_image_for_detection(img_path, message_id)
        except ValueError:
            print(f"Could not extract message ID from filename: {img_path}")
        except Exception as e:
            print(f"Failed to process {img_path}: {e}")
    print("YOLOv8 image enrichment complete.")

if __name__ == "__main__":
    main()

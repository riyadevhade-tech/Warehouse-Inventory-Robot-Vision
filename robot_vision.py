import pandas as pd
import cv2
from pathlib import Path
from datetime import datetime


class RobotVisionSystem:

    def __init__(self):
        self.system_name = "Smart Warehouse Robot Vision"
        self.status = "ONLINE"

    def load_image(self, image_path):

        image_path = Path(image_path)

        if not image_path.exists():
            return None, "Image not found"

        image = cv2.imread(str(image_path))

        if image is None:
            return None, "Unable to read image"

        return image, "Image loaded successfully"

    def analyze_image(self, image):

        if image is None:
            return {
                "status": "ERROR",
                "message": "No image available"
            }

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        blurred = cv2.GaussianBlur(
            gray,
            (5, 5),
            0
        )

        edges = cv2.Canny(
            blurred,
            50,
            150
        )

        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        detected_objects = 0

        for contour in contours:

            area = cv2.contourArea(contour)

            if area > 500:
                detected_objects += 1

        height, width = image.shape[:2]

        return {
            "status": "SUCCESS",
            "detected_objects": detected_objects,
            "image_width": width,
            "image_height": height,
            "detection_time": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

    def process_image(self, image_path):

        image, message = self.load_image(
            image_path
        )

        if image is None:
            return {
                "status": "ERROR",
                "message": message
            }

        result = self.analyze_image(image)

        result["message"] = message
        result["system"] = self.system_name

        return result


def main():

    print("=" * 55)
    print("       SMART WAREHOUSE ROBOT VISION SYSTEM")
    print("=" * 55)

    robot = RobotVisionSystem()

    print("Robot Status :", robot.status)
    print("System Ready.")
    print("Waiting for warehouse image...")

    print("=" * 55)


if __name__ == "__main__":
    main()
    # =========================================================
# VISION HISTORY
# =========================================================

import sqlite3


def create_history_database():

    connection = sqlite3.connect(
        "robot_vision_history.db"
    )

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vision_history (
            scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            detected_objects INTEGER,
            stock_quantity REAL,
            warehouse_section TEXT,
            status TEXT,
            scan_time TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_detection(
    product_name,
    detected_objects,
    stock_quantity,
    warehouse_section,
    status
):

    create_history_database()

    connection = sqlite3.connect(
        "robot_vision_history.db"
    )

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO vision_history (
            product_name,
            detected_objects,
            stock_quantity,
            warehouse_section,
            status,
            scan_time
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        product_name,
        detected_objects,
        stock_quantity,
        warehouse_section,
        status,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    connection.commit()
    connection.close()


def get_detection_history():

    create_history_database()

    connection = sqlite3.connect(
        "robot_vision_history.db"
    )

    history = pd.read_sql_query(
        "SELECT * FROM vision_history "
        "ORDER BY scan_id DESC",
        connection
    )

    connection.close()

    return history
    # =========================================================
# SAVE VISION DETECTION
# =========================================================

import sqlite3


def save_detection(
    product_name,
    detected_objects,
    stock_quantity,
    warehouse_section,
    status
):

    connection = sqlite3.connect(
        "robot_vision_history.db"
    )

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vision_history (
            scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            detected_objects INTEGER,
            stock_quantity REAL,
            warehouse_section TEXT,
            status TEXT,
            scan_time TEXT
        )
    """)

    cursor.execute("""
        INSERT INTO vision_history (
            product_name,
            detected_objects,
            stock_quantity,
            warehouse_section,
            status,
            scan_time
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        product_name,
        detected_objects,
        stock_quantity,
        warehouse_section,
        status,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    connection.commit()
    connection.close()
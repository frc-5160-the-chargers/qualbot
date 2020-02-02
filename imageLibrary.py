import cv2, os, json
from time import sleep

team = input("Enter team number\n> ")
key = cv2.waitKey(1)
webcam = cv2.VideoCapture(1)
sleep(2)
while True:
    try:
        check, frame = webcam.read()
        cv2.imshow("Capturing", frame)
        key = cv2.waitKey(1)
        if key == ord('s'): 
            filename = f'images\{team}_saved_img.jpg'
            cv2.imwrite(filename=filename, img=frame)
            webcam.release()
            print("Processing image...")
            img_ = cv2.imread('saved_img.jpg', cv2.IMREAD_ANYCOLOR)
            print("Converting RGB image to grayscale...")
            gray = cv2.cvtColor(img_, cv2.COLOR_BGR2GRAY)
            print("Converted RGB image to grayscale...")
            print("Resizing image to 1920x1080 scale...")
            img_ = cv2.resize(gray,(1920,1080))
            print("Resized...")
            img_resized = cv2.imwrite(filename='saved_img-final.jpg', img=img_)
            print("Image saved!")
            break
        
        elif key == ord('q'):
            webcam.release()
            cv2.destroyAllWindows()
            break
    
    except(KeyboardInterrupt):
        print("Turning off camera.")
        webcam.release()
        print("Camera off.")
        print("Program ended.")
        cv2.destroyAllWindows()
        break

teamDirectory = {team: filename}
with open("imageDirectory.json", "w") as json_file:
    json.dump(json_file)
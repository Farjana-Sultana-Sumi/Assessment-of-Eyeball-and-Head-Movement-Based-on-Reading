import cv2
import csv
import datetime
import tkinter as tk
import random
import keyboard

from eyeball_movement import EyeballMovement

gaze = EyeballMovement()
webcam = cv2.VideoCapture(0)
count_left = 0
count_right = 0

datet = str(datetime.datetime.now())

minute_counter = 0
last_save = datetime.datetime.now()
last_save = last_save.minute
total_movement = "counting within 1 min"
total_movement_final = 0
head_total_movement = 0


# print('Enter Id:')
# id = input()


def show_entry_fields():
    print("ID: %s" % (e1.get()))
    global id
    id = e1.get()


master = tk.Tk()
tk.Label(master,
         text="Enter ID: ").grid(row=0)
# tk.Label(master,
#          text="Last Name").grid(row=1)

e1 = tk.Entry(master)
# e2 = tk.Entry(master)

e1.grid(row=0, column=1)
# e2.grid(row=1, column=1)

tk.Button(master,
          text='Start reading',
          command=master.quit).grid(row=3,
                                    column=0,
                                    sticky=tk.W,
                                    pady=4)
tk.Button(master,
          text='Set ID', command=show_entry_fields).grid(row=3,
                                                         column=1,
                                                         sticky=tk.W,
                                                         pady=4)
master.title("Set_id")
tk.mainloop()

# id = random.randint(0, 2000)
name = "saad"
age = "30"
gender = "male"

# HEAD MOVEMENT START


color = {"blue": (255, 0, 0), "red": (0, 0, 255), "green": (0, 255, 0), "white": (255, 255, 255)}


# Method to detect nose
def detect_nose(img, faceCascade):
    # convert image to gray-scale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # detecting features in gray-scale image, returns coordinates, width and height of features
    features = faceCascade.detectMultiScale(gray_img, 1.1, 8)
    nose_cords = [ ]
    # drawing rectangle around the feature and labeling it
    for (x, y, w, h) in features:
        #         cv2.rectangle(img, (x,y), (x+w, y+h),  color['green'], 2)  #uncomment if you want to see face boundary
        cv2.circle(img, ((2 * x + w) // 2, (2 * y + h) // 2), 10, color[ 'green' ], 2)
        nose_cords = ((2 * x + w) // 2, (2 * y + h) // 2)
    return img, nose_cords


def draw_controller(img, cords):
    size = 40
    x1 = cords[ 0 ] - size
    y1 = cords[ 1 ] - size
    x2 = cords[ 0 ] + size
    y2 = cords[ 1 ] + size
    cv2.circle(img, cords, size, color[ 'blue' ], 2)
    return [ (x1, y1), (x2, y2) ]


def keyboard_events(nose_cords, cords, cmd):
    try:
        [ (x1, y1), (x2, y2) ] = cords
        xc, yc = nose_cords
    except Exception as e:
        print(e)
        return
    if xc < x1:
        cmd = "left"

    elif (xc > x2):
        cmd = "right"

    elif (yc < y1):
        cmd = "up"
    elif (yc > y2):
        cmd = "down"
    if cmd:
        print("Detected movement: ", cmd, "\n")
        keyboard.press_and_release(cmd)
    return frame, cmd


def reset_press_flag(nose_cords, cords, cmd):
    try:
        [ (x1, y1), (x2, y2) ] = cords
        xc, yc = nose_cords
    except:
        return True, cmd
    if x1 < xc < x2 and y1 < yc < y2:
        return True, None
    return False, cmd


# Loading classifiers
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Capturing real time video stream.
# video_capture = cv2.VideoCapture(0)

# get vcap property
width = webcam.get(3)  # float
height = webcam.get(4)  # float
press_flag = False
cmd = ""

# HEAD MOVEMENT END======================#

hl = 0
hr = 0
hkey = 'right'
key = "right"
while True:
    # We get a new frame from the webcam
    _, frame = webcam.read()

    # We send this frame to GazeTracking to analyze it
    gaze.refresh(frame)

    frame = gaze.annotated_frame()
    text = ""

    if gaze.is_blinking():
        text = "Blinking"
    elif gaze.is_right():
        text = "Looking right"
        if key == "left":
            count_right = count_right + 1
            key = "right"

    elif gaze.is_left():
        text = "Looking left"
        if key == "right":
            key = "left"
            count_left = count_left + 1
    elif gaze.is_center():

        text = "Looking center"
        # if (key == "center"):
        #     key ="center"

    # detect nose and draw
    frame, nose_cords = detect_nose(frame, faceCascade)

    if str(cmd) == "left":

        if hkey == "right":
            hkey = "left"
            hl = hl + 1
    if str(cmd) == "right":

        if hkey == "left":
            hkey = "right"
            hr = hr + 1
    head_total_movement = hl + hr
    print('head movement count : ' + str(head_total_movement))

    cv2.putText(frame, 'Head Position: ' + str(cmd) + 'movement count : ' + str(head_total_movement), (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color[ 'red' ], 1,
                cv2.LINE_AA)
    # draw boundary circle
    cords = draw_controller(frame, (int(width / 2), int(height // 2)))
    if press_flag and len(nose_cords):
        frame, cmd = keyboard_events(nose_cords, cords, cmd)
    press_flag, cmd = reset_press_flag(nose_cords, cords, cmd)
    # nose detect end=========

    cv2.putText(frame, text, (20, 70), cv2.FONT_HERSHEY_DUPLEX, 0.8, (147, 58, 31), 2)

    left_pupil = gaze.pupil_left_coords()
    right_pupil = gaze.pupil_right_coords()

    now = datetime.datetime.now()

    movement_time = now.minute

    if movement_time > last_save:
        last_save = now.minute
        minute_counter = minute_counter + 1
        total_movement = round((count_right + count_left))
        # print (str(last_save)+" - "+str(total_movement))
        count_left = 0
        count_right = 0

        time_forcsv = datetime.datetime.now().date()
        filename = str(id) + '_' + '_' + str(time_forcsv)
        fullpath = str(filename) + ".csv"
        with open(fullpath, mode='a') as csv_file:
            # fieldnames = [ 'name', 'age', 'gender', 'left_eye', 'right_eye' ]
            # writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            #
            # writer.writeheader()
            # writer.writerow({'name': name, 'age': age, 'gender': gender, 'left_eye': str(left_pupil), 'right_eye': str(right_pupil)})
            #
            #
            # # writer.writerow({'emp_name': 'Erica Meyers', 'dept': 'IT', 'birth_month': 'March'})

            fieldnames = ['id', 'total_eye_movement', 'total_head_movement', 'time(min)']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerow({'id': id,
                             'total_eye_movement': str(total_movement),
                             'total_head_movement': str(head_total_movement),
                             'time(min)': str(minute_counter)})

            # writer.writerow({'emp_name': 'Erica Meyers', 'dept': 'IT', 'birth_month': 'March'})

    cv2.putText(frame, "time: " + str(minute_counter) + " min", (10, 100), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 255), 2,
                cv2.LINE_AA)
    # cv2.putText(frame, datet, (10, 100), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
    # cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    # cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    cv2.putText(frame, "id: " + str(id), (10, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    # cv2.putText(frame, "Left count:  " + str(count_left), (90, 230), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    # cv2.putText(frame, "Right count: " + str(count_right), (90, 265), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    # cv2.putText(frame, "Left count:  " + str(count_left), (90, 230), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    cv2.putText(frame, "Total Movement: " + str(total_movement), (10, 200), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31),
                1)

    # print("Left pupil:  " + str(left_pupil))
    # print("Right pupil: " + str(right_pupil))

    # if(left_pupil!="None" or right_pupil!="None"):

    # i=1
    #
    # time_forcsv = datetime.datetime.now().date()
    # filename = str(id)+'_'+name+'_'+str(time_forcsv)
    # fullpath = str(filename) + ".csv"
    # with open(fullpath, mode='a') as csv_file:
    #
    #
    #     # fieldnames = [ 'name', 'age', 'gender', 'left_eye', 'right_eye' ]
    #     # writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    #     #
    #     # writer.writeheader()
    #     # writer.writerow({'name': name, 'age': age, 'gender': gender, 'left_eye': str(left_pupil), 'right_eye': str(right_pupil)})
    #     #
    #     #
    #     # # writer.writerow({'emp_name': 'Erica Meyers', 'dept': 'IT', 'birth_month': 'March'})
    #
    #
    #     fieldnames = [ 'id','total_eye_movement','time' ]
    #     writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    #
    #     writer.writeheader()
    #     writer.writerow({'id': id,
    #
    #                      'total_eye_movement': str(total_movement),
    #                      'time':str(minute_counter)})
    #
    #
    #     # writer.writerow({'emp_name': 'Erica Meyers', 'dept': 'IT', 'birth_month': 'March'})

    cv2.imshow("PC Eyeball Tracker", frame)

    if cv2.waitKey(1) == 27:
        break

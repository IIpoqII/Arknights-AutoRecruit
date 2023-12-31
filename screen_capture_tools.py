import numpy as np
import cv2
import os
import pytesseract
import time
import pyautogui
import win32gui
from pynput.keyboard import Key, Listener


# Uses pytesseract to recognize text in images
# Uses pyautogui to take screenshots
# Uses win32gui (from pywin32) to get window details


def get_window_titles():
    """Returns a list of visible window titles"""
    def callback(win_handle, win_titles_list):
        if win32gui.IsWindowVisible(win_handle):
            window_title = win32gui.GetWindowText(win_handle)
            win_titles_list.append(window_title)
    win_titles_list = []
    win32gui.EnumWindows(callback, win_titles_list)
    return win_titles_list


class Tools:
    def __init__(self, window_name="", img_width=800, img_height=450, exit_key="q", pytesseract_directory=r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
        # pytesseract directory
        pytesseract.pytesseract.tesseract_cmd = pytesseract_directory
        self.width = img_width
        self.height = img_height
        self.screen_cap_name = "Screen Capture"
        self.window_cap_name = "Capture: " + window_name
        self.window_handle = win32gui.FindWindow(None, window_name)
        self.file_dir = os.path.dirname(__file__)
        self.file_dir = os.path.dirname(self.file_dir)

    def get_window_titles(self):
        """
        Returns a list of visible window titles
        """
        def callback(win_handle, win_titles_list):
            if win32gui.IsWindowVisible(win_handle):
                window_title = win32gui.GetWindowText(win_handle)
                win_titles_list.append(window_title)

        win_titles_list = []
        win32gui.EnumWindows(callback, win_titles_list)
        return win_titles_list

    def get_window_handle(self):
        """
        Returns the window's handle
        """
        return self.window_handle

    def show_screen(self):
        """
        Show the screen in a feed\n
        Enter a keyboard input to exit the feed and the program
        """
        cv2.namedWindow(self.screen_cap_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.screen_cap_name, self.width, self.height)
        while True:
            image = pyautogui.screenshot()
            image = np.asarray(image)
            cv2.imshow(self.screen_cap_name, image)
            cv2.waitKey(1)

    def show_window(self, print_position=False):
        """
        Preview the window for taking screenshots of it\n
        Enter a keyboard input to exit the feed and the program\n
        Notes:\n
        Issue: The window cannot be brought to foreground if it is minimized\n
        Fix: un-minimize the window before running\n
        Issue: The program crashes if the capture window is brought in front of the input window\n
        Fix: Try dragging or repositioning the capture window ahead of time
        """
        cv2.namedWindow(self.window_cap_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_cap_name, self.width, self.height)
        while True:
            win32gui.SetForegroundWindow(self.window_handle)
            image = pyautogui.screenshot()
            window_pos = self.get_window_position(print_position=print_position)
            image = image.crop((window_pos[0][0], window_pos[0][1], window_pos[1][0], window_pos[1][1]))
            image = np.asarray(image)
            cv2.imshow(self.window_cap_name, image)
            cv2.waitKey(1)

    def get_window_position(self, print_position=False):
        """
        Returns the top-left and bottom-right points of the window
        """
        x1, y1, x2, y2 = win32gui.GetWindowRect(self.window_handle)
        pt1 = x1, y1
        pt2 = x2, y2
        if print_position:
            print(pt1, pt2)
        return pt1, pt2

    def draw_rectangle_on_screen(self, pt1, pt2, border_thickness=2):
        """
        Preview the screen with a rectangle from pt1 to pt2\n
        Enter a keyboard input to exit the feed and the program
        """
        cv2.namedWindow(self.screen_cap_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.screen_cap_name, self.width, self.height)
        while True:
            image = pyautogui.screenshot()
            image = np.asarray(image)
            image = cv2.rectangle(image, pt1, pt2, (0, 0, 255), border_thickness)
            cv2.imshow(self.screen_cap_name, image)
            cv2.waitKey(1)

    def account_for_duplicate_name(self, image, path, file_type):
        """
        Accounts for saving images of the same name
        """
        path_temp = path
        path = path + file_type
        if not os.path.exists(path):
            image.save(path)
            return
        # append for duplicates
        for i in range(1, 100):
            path = path_temp + "_(" + str(i) + ").png"
            if not os.path.exists(path):
                image.save(path)
                return
            if i == 100:
                print("Too many screenshots of the same name")
                print("Please delete some")
                return

    def open_image_file(self, path):
        return cv2.imread(path, 0)

    def save_image(self, image, directory="Screenshots", file_name="image", file_type=".png"):
        # setup path
        path = os.path.join(self.file_dir, directory, file_name)
        self.account_for_duplicate_name(image, path, file_type)

    def take_screenshot(self, save_screenshot=True, screenshot_dir="Screenshots", screenshot_name="screenshot"):
        """
        Takes a screenshot of the entire screen
        """
        img = pyautogui.screenshot()
        if save_screenshot:
            self.save_image(img, screenshot_dir, screenshot_name, file_type=".png")
        return img

    def take_windowed_screenshot(self, save_screenshot=True, screenshot_dir="Screenshots", screenshot_name="screenshot"):
        """
        Takes a screenshot of the window
        """
        win32gui.SetForegroundWindow(self.window_handle)
        img = pyautogui.screenshot()
        pt1, pt2 = self.get_window_position()
        img = img.crop((pt1[0], pt1[1], pt2[0], pt2[1]))
        if save_screenshot:
            self.save_image(img, screenshot_dir, screenshot_name, file_type=".png")
        return img

    def take_bounded_screenshot(self, pt1, pt2, save_screenshot=True, screenshot_dir="Screenshots", screenshot_name="screenshot"):
        """
        Takes a screenshot of the bounded area
        """
        # pt1 is top-left
        # pt2 is bottom-right
        img = pyautogui.screenshot()
        img = img.crop((pt1[0], pt1[1], pt2[0], pt2[1]))
        if save_screenshot:
            self.save_image(img, screenshot_dir, screenshot_name, file_type=".png")
        return img

    def skew_image(self, image, image_pts, output_pts, save_image=False, folder_dir="Screenshots", file_name="deskewed", file_type=".png"):
        """
        image_pts are three corner points\n
        output_pts are the desired position after the transformation
        """
        img = np.asarray(image)
        rows, cols, ch = img.shape
        pts1 = np.float32(image_pts)
        pts2 = np.float32(output_pts)
        # apply affine transformation
        warp_mat = cv2.getAffineTransform(pts1, pts2)
        img_skewed = cv2.warpAffine(img, warp_mat, (cols, rows))
        if save_image:
            path = os.path.join(self.file_dir, folder_dir, file_name) + file_type
            cv2.imwrite(path, img_skewed)
        return img_skewed

    def detect_text_in_image(self, image, bound_text=False, color_to_gray=False):
        """
        Returns the detected text and the image in a tuple
        """
        # convert image to numpy array
        img = np.asarray(image)
        if color_to_gray:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if not bound_text:
            return pytesseract.image_to_string(img), image
        else:
            # perform OTSU threshold
            ret, thresh1 = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
            # specify structure shape and kernel size
            rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
            # apply dilation
            dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)
            # find contours
            contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            # extract text in identified contours
            detected_text = ""
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                img_cropped = img[y:(y+h), x:(x+w)]
                detected_text += pytesseract.image_to_string(img_cropped)
            return detected_text, image

    def find_text_in_image(self, image, find_text, print_detected_text=False, show_image=False, bound_text=False):
        """
        Enter a keyboard input to exit the feed and the program
        """
        detected_text, img = self.detect_text_in_image(image, bound_text)
        if print_detected_text:
            print("Detected Text:")
            print("  " + detected_text)
            print("--------------------------------")
            print("--------------------------------")
        text_found = find_text in detected_text
        if text_found:
            print("'" + find_text + "' was detected")
        else:
            print("'" + find_text + "' was not detected")
        if show_image:
            cv2.namedWindow(self.window_cap_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.window_cap_name, self.width, self.height)
            cv2.imshow(self.window_cap_name, img)
            cv2.waitKey(0)
        return text_found

    def find_text_in_window(self, find_text, bound=None, print_detected_text=False, show_window=True, bound_text=False, quick=False):
        """
        When quick==True, runs once and returns
        """
        while True:
            was_text_found = False
            # get image of the window
            img = pyautogui.screenshot()
            pt1, pt2 = self.get_window_position()
            img = img.crop((pt1[0], pt1[1], pt2[0], pt2[1]))
            if bound is not None:
                img = img.crop((bound[0][0], bound[0][1], bound[1][0], bound[1][1]))
            img = np.asarray(img)
            detected_text, img = self.detect_text_in_image(img, bound_text)
            if quick:
                return find_text in detected_text
            if show_window:
                cv2.namedWindow(self.window_cap_name, cv2.WINDOW_NORMAL)
                cv2.resizeWindow(self.window_cap_name, self.width, self.height)
                cv2.imshow(self.window_cap_name, img)
                cv2.waitKey(1)
            if print_detected_text:
                print("Detected Text:")
                print("  " + detected_text)
            text_found = find_text in detected_text
            if text_found:
                was_text_found = True
                print("--------------------------------")
                print("'" + find_text + "' detected")
                print("--------------------------------")
            if cv2.waitKey(1) & 0xFF == ord("q"):
                if was_text_found:
                    print("--------------------------------")
                    print("'" + find_text + "' was detected")
                    print("--------------------------------")
                else:
                    print("--------------------------------")
                    print("'" + find_text + "' was not detected")
                    print("--------------------------------")
                return text_found

    def find_points_on_image(self, image_name=None, directory="Screenshots", quit_key="q", reset_key="r"):
        """
        If image_name=None, takes and uses a screenshot of the window as the image\n
        Shows an image and returns three mouse click positions\n
        (0, 0) is the image's top-left pixel\n
        Default directory is the "Screenshots" folder
        """
        def mouse_click_event(event, x, y, flags, params):
            if event == cv2.EVENT_LBUTTONDOWN:
                if len(pts_list) >= num_pts:
                    pts_list.clear()
                cv2.circle(img, (x, y), 1, (0, 0, 255), cv2.FILLED)
                cv2.circle(img, (x, y), 10, (0, 0, 255), 2)
                pts_list.append([x, y])
                if len(pts_list) == num_pts:
                    print(pts_list)

        def take_screenshot():
            win32gui.SetForegroundWindow(self.window_handle)
            time.sleep(0.5)   # wait for window to be in foreground
            img = pyautogui.screenshot()
            pt1, pt2 = self.get_window_position()
            img = img.crop((pt1[0], pt1[1], pt2[0], pt2[1]))
            img = np.asarray(img)
            return img

        num_pts = 3
        if image_name is None:
            img = take_screenshot()
        else:
            image_path = os.path.join(self.file_dir, directory, image_name)
            img = cv2.imread(image_path)
        pts_list = []
        while True:
            cv2.imshow("Image", img)
            cv2.setMouseCallback("Image", mouse_click_event)
            # reset image and points list
            if cv2.waitKey(1) & 0xFF == ord(reset_key):
                if image_name is None:
                    img = take_screenshot()
                else:
                    img = cv2.imread(image_path)
                pts_list.clear()
            # exit program with "q"
            if cv2.waitKey(1) & 0xFF == ord(quit_key):
                break

### step 1: get images from a camera
url="http://192.168.13.25:5000"
mode="url" # can be opencv, pi, test, url

### step 2: what part of the screen to get and transform to a rectangle?
#(use select.html to get coordinates with your mouse, click to copy to clipboard)
top_left_factor = (0.113,0.012)
top_right_factor =(0.877,0.017)
bottom_left_factor =(0.041,0.806)
bottom_right_factor =(0.96,0.787)

### step 3: look for differences via compare.py

### step 4: enhance image via whiteboardenhance.py
dog_k_size =15


### step 1: get images from a camera
url="http://10.0.0.6:5000"
mode="url" # can be opencv, pi, test, url

### step 2: what part of the screen to get and transform to a rectangle?
#(use select.html to get coordinates with your mouse, click to copy to clipboard)

# top_left_factor = (0.865,0.769)
# top_right_factor = (0.079,0.823)
# bottom_left_factor = (0.785,0.051)
# bottom_right_factor =(0.123,0.091)

top_left_factor = (0.876,0.792)
top_right_factor = (0.068,0.835)
bottom_left_factor = (0.794,0.033)
bottom_right_factor = (0.117,0.082)

### step 3: look for differences via compare.py

### step 4: enhance image via whiteboardenhance.py
dog_k_size =15


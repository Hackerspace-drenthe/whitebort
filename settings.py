### HSD whiteboard

mode="url" # can be opencv, pi, test, url
url="http://10.0.0.6:5000"

# mode="test" # can be opencv, pi, test, url

# mode="url" # can be opencv, pi, test, url
# url="http://localhost:4000"

frame_time=1
last_sent_file="whiteboard.png"

#save images, for testing
save=False

top_left_factor = (0.723,0.83)
top_right_factor = (0.177,0.861)
bottom_left_factor = (0.685,0.27)
bottom_right_factor =(0.187,0.304)

dog_k_size =60


compare_factor=20
compare_dirty_threshold=0.10
compare_clean_threshold=compare_dirty_threshold/2
compare_stable_frames=10
# compare_clean_threshold=compare_dirty_threshold/2


# ### test whiteboard
# mode="test" # can be opencv, pi, test, url
# frame_time=1
#
# #save images, for testing
# save=False
#
# top_left_factor =(0.409,0.398)
# top_right_factor =(0.645,0.171)
# bottom_left_factor =(0.344,0.995)
# bottom_right_factor =(0.711,0.86)
# dog_k_size =25
# min_change_area=100
# min_change_area=1


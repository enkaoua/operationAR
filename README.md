# OPERATION AR

# 1) Clone the repository

# 3) Install the requirements

```
pip install -r requirements.txt
```

# 3) print markers if necessary
I included some code (`cl_generate_aruco_board`) for creating the aruco markers. Their size and scale can be specified in the config.ini file under the section "ARUCO". Each parameter is clearly commented so should be self-explanatory. 

# 2) Make sure physical game is set up

Things to ensure-
- button turned to ON
- batteries are in
- pointer connected to wire
- aruco markers are properly on.
- make sure the aruco marker dimensions are the same as what the config file says

# 4) Run the code


First calibrate camera and add to data/calibration as .txt file 

Then run 

```
python cl_main.py --config config/config.ini
```

# 5) make sure models properly registered
Hopefully when you place the aruco marker in the bottom right of the game it should be registered but if not, move the markers and if really necessary, change the registration.txt file inside the data folder. For the pointer, move the marker until the pointer bit looks aligned with the AR display. 



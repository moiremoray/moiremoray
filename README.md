# MOiRE // MORAY
<!--- TODO: this is very manual, add dependency management and setup script -->
## setup

at project root (~/your-projects/moiremoray/)

```
    ./setup.sh
```

## convert model files (.obj -> .json)

```
    ruby src/moire.rb layouts/moire-full-density.obj
```

## simulation

start opengl simulator

```
    vendor/openpixelcontrol/bin/gl_server -l layouts/moire-full-density.json
```

client test programs

```
    src/moire_test.py -p single # cycle throug one pixel at a time
    src/moire_test.py -p strut # cycle through one strut at a time
    src/moire_test.py -p span # cycle one row of pixels at a time
    src/moire_test.py -p circle # pulse circles of varying stroke width and color through the pixel mesh
    src/moire_test.py -p circle -s 10 # specify how many seconds a complete cycle should take
```

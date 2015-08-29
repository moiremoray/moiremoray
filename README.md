# MOiRE // MORAY
<!--- TODO: this is very manual, add dependency management and setup script -->
## setup

navigate to project root (~/your-projects/moiremoray/)

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
    src/moire_test.py -p circle --count 3 # specify how many circle should be used
    src/moire_test.py -p circle --count 2 --blend add # specify blend mode for shape layer compositing
```

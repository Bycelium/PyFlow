```eval_rst
.. _coding-standards:
```
# Coding Standards

The following rules and guidelines are used throughout the nodeeditor package:

## File naming guidelines

* files in the nodeeditor package start with ```node_```
* files containing graphical representation (PyQt5 overridden classes) start with ```node_graphics_```
* files for window/widget start with ```node_editor_```

## Coding guidelines

* methods use Camel case naming
* variables/properties use Snake case naming

* The constructor ```__init__``` always contains all class variables for the entire class. This is helpful for new users, so they can
  just look at the constructor and read about all properties that class is using in one place. Nobody wants any 
  surprises hidden in the code later
* nodeeditor uses custom callbacks and listeners. Methods for adding callback functions
  are usually named ```addXYListener```
* custom events are usually named ```onXY```
* methods named ```doXY``` usually *do* certain tasks and also take care of low level operations
* classes always contain methods in this order:
    * ```__init__```
    * python magic methods (i.e. ```__str__```), setters and getters 
    * ```initXY``` functions
    * listener functions
    * nodeeditor event fuctions
    * nodeeditor ```doXY``` and ```getXY``` helping functions 
    * Qt5 event functions
    * other functions
    * optionally overridden Qt ```paint``` method
    * ```serialize``` and ```deserialize``` methods at the end    
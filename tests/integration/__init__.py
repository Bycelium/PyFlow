# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

"""
Integration tests for the  package.

We use xvfb to perform the tests without opening any windows.
We use pyautogui to move the mouse and interact with the application.

To pass the tests on windows, you need to not move the mouse.
Use this if you need to understand why a test fails.

To pass the tests on linux, you just need to install xvfb and it's dependencies.
On linux, no windows are opened to the user during the test.
To understand why a test fails, pass the flag "--no-xvfb" and use your own X server
to see the test running live.
"""

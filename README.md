This is a fork of [PyTeapot-Quaternion-Euler-cube-rotation](https://github.com/thecountoftuscany/PyTeapot-Quaternion-Euler-cube-rotation)
by [Nishant Elkunchwar](https://github.com/thecountoftuscany). It has been modified to get data from the [MUGIC](https://mugicmotion.com/) IMU.

This is a quick'n dirty hack but it works reasonably for me. YMMV, though.

To get it working, you'll probably need at least some basic knowledge of the python language. On Linux, this should work:

1) Clone the repos

2) create a virtual environment and activate it

    ```
    $ python -m venv venv
    $ source venv/bin/activate
    ```

3) install dependencies

    ```
    $ pip install -r requirements.txt
    ```

4) launch

    ```
    $ python pymugic.py
    ```

**Note** Please make sure you are using python 3.x. Dependending on your system you might need to replace
`python` with `python3` or `py3` and maybe `pip` with `pip3`.

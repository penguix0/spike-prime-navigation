# A.T.O.M. | Automatic Tracklab Originate Module

A.T.O.M. is our Automatic Tracklab Originate Module. With A.T.O.M. you can simulate the behavior of ill and healthy cows. This repository contains all the things needed to run A.T.O.M. on your own Lego Spike Prime Hub and PC. A.T.O.M. consists of two parts: the on-device program and a pc side program. The program on the device itself simulates the cow itself and mimics the ill and healthy state. It's also capable of navigating around trains itself and shouldn't hit any walls.
The program on the PC is responsible for measuring the distance the robot has driven with an accuracy of 0.2 meters. Our client wanted this feature to compare it to their Tracklab software.

## 🚀 Getting started

### 1. Requirements

To use A.T.O.M. yourself you need a few things:
- A PC supporting Bluetooth 5.0 with:
    - Linux
    - Mac OS (Big Sur or later recommended)
    - Windows 7 or later
- A [Lego Mindstorms 51515](https://www.lego.com/en-us/product/robot-inventor-51515) set
- Something which functions the same as our lego build which is based on the M.V.P.:
<p align="center">
    <a href="https://www.lego.com/cdn/product-assets/product.bi.additional.main.pdf/51515_MVP.pdf">
        <img src="https://github.com/penguix0/spike-prime-navigation/blob/main/pictures/robot_1.png?raw=true" alt="Picture of the robot used with A.T.O.M." width="423" height="382">
    </a>
</p>

### 2. Downloading

Select the way you want to install spike-prime-navigation

<details>
<summary>GitHub CLI</summary>

To install spike-prime-navigation with GitHub CLI you need to execute the following command in terminal:

```sh
gh repo clone penguix0/spike-prime-navigation
```

</details>

<details>
<summary>Browser</summary>

To install spike-prime-navigation through you're browser you need to do the following:
1. Head over to the [repository](https://github.com/penguix0/spike-prime-navigation)
2. Click on releases ![releases page picture](./pictures/releases.png)
3. Download the latest release

</details>

### 3. Execute the program!

Unzip your downloaded release and click on the .exe file to start the app.

## Useful stuff

### Connecting to the hub

Here is a [YouTube video](https://www.youtube.com/watch?v=MEj1_pS3esw) that shows how to connect to the Spike Prime Hub.

### ⚙️ Changing the Bluetooth MAC address of the Lego Spike Prime Hub

If you want to use this program with your own Lego Spike Prime Hub, you're in luck, because you can! The only thing you have to do is change the MAC address in the config file. Navigate to <code>/App/lego_hub.yaml</code> and open it with a text editor such as NotePad. Next scroll down until you see this piece of text:

<p align="center">
    <a href="https://github.com/penguix0/spike-prime-navigation/blob/main/App/lego_hub.yaml">
        <img src="https://github.com/penguix0/spike-prime-navigation/blob/main/pictures/yaml_to_edit.png?raw=true" alt="Picture of the YAML to edit">
    </a>
</p>

The MAC address seen in the picture is the one for my Lego Spike Prime HUB, you're MAC address is different from mine, however. To get the MAC address of you're Lego Spike Prime Hub you first need to [pair](https://education.lego.com/en-us/product-resources/spike-prime/troubleshooting/bluetooth-connectivity) it with your system. Now you can get the MAC address of you are hub and replace the current MAC address with your own.

### 🧱 Building from source

This guide assumes that you have already [installed](
https://phoenixnap.com/kb/how-to-install-python-3-windows) python3.

Before we start we need to install the dependencies. Navigate to <code>source</code> and execute the following command to install all the necessary dependencies:

```sh
pip3 install -r requirements.txt
```

First, install [pyinstaller](https://pypi.org/project/pyinstaller/):

```sh
pip install pyinstaller
```

Next, navigate to the directory containing <code>App.py</code> and execute the following command:

```sh
pyinstaller App.py -i icon.ico
```


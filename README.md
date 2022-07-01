# spike-prime-navigation
program written using pygame to map the spike prime movement


## Changing the bluetooth MAC address of the Lego Spike Prime Hub

If you want to use this program with your own Lego Spike Prime Hub, you're in luck, because you can! The only thing you have to do is change the MAC address in the config file. Navigate to <code>/App/lego_hub.yaml</code> and open it with a text-editor such as notepad. Next scroll down until you see this piece of text:
![YAML to edit](./pictures/yaml_to_edit.png "The YAML we're going to edit.")

The MAC address seen in the picture is the one for my Lego Spike Prime HUB, you're MAC address is different from mine however. To get the MAC address of you're Lego Spike Prime Hub you first need to [pair](https://education.lego.com/en-us/product-resources/spike-prime/troubleshooting/bluetooth-connectivity) it with your system. Now you can get the MAC address of you're hub and replace the current MAC address with yours.
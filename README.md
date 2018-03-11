# Sensor Data Collection

## Description

Collect data from sensor objects ([SensorTag](http://www.ti.com/ww/en/wireless_connectivity/sensortag2015/?INTC=SensorTag&HQS=sensortag) implemented)  

## Installation

### Prerequisites

#### Local

##### Fabric3
`pip install fabric3`

##### Source Code
`git clone git@github.com:tounnas/sensor-data-collection.git`


#### Remote
* A Linux environment
* Python 3

##### How To prepare the Raspberry

###### Burn Image

* Download [Rasbian](https://downloads.raspberrypi.org/raspbian_latest).
* Follow this [documentation](https://www.raspberrypi.org/documentation/installation/installing-images/) in order to burn the image on the ssd card.

###### Init
Put the ssd card in the raspberry, open a terminal and run the following command :
`sudo raspi-config`

Then :
* Extend the partition
* Change the password
* Go in Advance Settings in order to activate the ssh

###### Some Installs
```
sudo apt-get update
sudo apt-get install screen
```

### Deployment
```
cd path-to-sensor-data-collection
fab -H hostname deploy
```

## Usage

`source /var/sensor_data_collection_env/SENSOR_DATA_COLLECTION_{VERSION}/bin/activate`

### MAC Addr
If you don't know the mac-addr of your device you can run a lescan with hcitool on raspbian/linux os:
`sudo hcitool lescan`

### Sensor Values Extraction
`sensor-data -d mac_addr1,mac_addr2 --log-dir logs`

### Help
`sensor-data -h`

### Extend for other type of sensors
You can extend the Reader class in reader.py then change the SELECTED_READER.  


# Alteryx SDK SystemInfo
Alteryx tool to gather system information from machine

## Installation
Download the yxi file and double click to install in Alteyrx. The tool will be installed in the __Developer__ category.

![alt text](https://github.com/bobpeers/Alteryx_SDK_SystemInfo/blob/master/images/systeminfo.png "Alteryx Developer Category")

## Usage
This tool has no inputs. Place tool on the canvas and optionally configure the tools settings. The tool outputs data on:

- General Information
- Platform Information
- CPU
- Memory
- Disks
- Network
- Processes (optional)
- Services (optional)
- Environment Variables (optional)

## Outputs
Sucessful operations will be output to the O-Output. The output is in three columns, Category, System property and value.

## Usage
This workflow demonstrates the tool in use and the output data.

![alt text](https://github.com/bobpeers/Alteryx_SDK_SystemInfo/blob/master/images/systeminfo_workflow.png "System Info Workflow")

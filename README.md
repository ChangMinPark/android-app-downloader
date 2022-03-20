# Android App Downloader
This tool downloads Android app (.apk) for a target SDK version using either [Google Play API](https://github.com/NoMore201/googleplay-api) or [AndroZoo](https://androzoo.uni.lu/).

- **Google Play API** requires Google account. 

- **AndroZoo** requires API key and csv file containing a list of apps and their information.

Google Play Store does not provide old versions of an app and keeps only a few versions. If a target SDK version is old, a user should be able to download the app using AndroZoo instead in high chance. Thus, if not downloadable by Google Play API, try with AndroZoo. Our tool automatically handles downloading all available apps and checking their SDK versions.

**_Important Point_** - When downloading an app that has separate app versions supporting each ABI type, do not use AndroZoo since it does not provide any information about which ABI an app supports. A user can use Google Play API to download an app supporting specific ABI by providing _GSFID_ of her device. To get the GSFID, the user needs to register her Google account on the device, and the device's ABI should match with the one that she wants to download. 


## How to Use


### 1. Prepare Tools Required & Environmental Variables
> **Google Play API** - No need to be installed. Already included in our source code. 
>  - dd

> **AndroZo** - Download from [link](https://androzoo.uni.lu/api_doc)

### 2. Settings


### 3. Run
Below is code to use our downloader:
```python
d = Downloader(mode, sdk_version, sdk_version_match)
d.download_all(pkg_list, out_path)
```
> _mode_ - 
>
> _sdk_version_ - 
>
> _sdk_version_match_ - 
>
> _pkg_list_ - 
> 

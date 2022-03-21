# Android App Downloader
This tool downloads Android app (.apk) for a target SDK version using either [Google Play API](https://github.com/NoMore201/googleplay-api) or [AndroZoo](https://androzoo.uni.lu/).

- **Google Play API** requires Google account. 

- **AndroZoo** requires API key and csv file containing a list of apps and their information.

Google Play Store does not provide old versions of an app and keeps only a few versions. If a target SDK version is old, a user should be able to download the app using AndroZoo instead in high chance. Thus, if not downloadable by Google Play API, try with AndroZoo. Our tool automatically handles downloading all available apps and checking their SDK versions.

**_Important_** - When downloading an app that has separate app versions supporting each ABI type, do not use AndroZoo since it does not provide any information about which ABI an app supports. A user can use Google Play API to download an app supporting specific ABI by providing _GSFID_ of her device. To get the GSFID, the user needs to register her Google account on the device, and the device's ABI should match with the one that she wants to download. 

<br/>

## App List Dataset

In data/app_rank/ directory, we have an app list dataset (06/16/2021) which size is over 600 MB. 

If anyone wants to use the latest version of dataset, please visit [here](https://github.com/gauthamp10/Google-Playstore-Dataset) and follow the instruction to download the latest version.

<br/>

## How to Use

### 1. Prepare Tools Required & Environmental Variables
> **Google Play API** - No need to be installed. Already included in our source code. 
>  - Downloads an app from Google Play Store
>  - Set environmental variables for login credentials (see _src/config.py_) - [Link](https://developers.google.com/android-publisher/authorization)
>    - **_GPAPI_EMAIL_**: Account email
>    - **_GPAPI_PASSWORD_**: Pass word of the account
>    - **_GPAPI_GSFID_**: Google Services Framework Identifier (GSFID) of your device
>    - **_GPAPI_TOKEN_**: Google Oauth token

> **AndroZoo** - Download from [link](https://androzoo.uni.lu/api_doc)
>  - Set environmental variables
>    - **_AZ_API_KEY_**: API key 
>    - **_AZ_INPUT_FILE_**: Latest input dataset

> **Android Asset Packaging Tool (AAPT)** - Download from [Link](https://androidaapt.com/)
>  - Requires to depackage downloaded app to check target SDK version


### 2. Run
Below is code to use our downloader:
```python
d = Downloader(mode, sdk_version, sdk_version_match)
d.download_all(pkg_list, out_path)
```
> **_mode_** - Choose which tool to use for downloading: (1) GPAPI (Google API) or (2) AZ (AndroZoo).
> 
> **_sdk_version_** - Target SDK version for apps to download.
> 
> **_sdk_version_match_** - Whether to check if downloaded app's target SDK exactly matches or not. 
> If FALSE, look for apps that our target SDK version is within minimum SDK version and target SDK 
> version of the downloaded apps.
>
> **_pkg_list_** - A list of tuples to download, e.g., (package name, app category). 


### 3. Test
Check and run **_main.py_** file how it can be used"
```sh
$ python3 main.py
```


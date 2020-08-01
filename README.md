# Gwent Card Exporter

Download here : https://github.com/pramberg451/gwentCardExporter/releases

### Description and Features ###
The Gwent Card Exporter is an application written in Python using Tkinter and the PIL. It is meant to be a simple program to export both images and card data relative to the current Gwent game instead of using third-party data or images which might take a while to be updated after a new version release. A valid Gwent installation on either Steam or GOG is required.

You can use it to...
 - Export a .json file containing Gwent card data. This can be incredibly useful to use in your own Gwent related projects. You can find all the .json files that you have extracted in the 'card_data' folder in the same directory that the .exe is.
 - Export card art directly from the game files.
 - Generate all cards at once, in batches or individually. Need just one image for a thumbnail or a wallpaper? Just search it in the list!
 - Add card borders, strength, icons or provision numbers to your exported images.
 - Export in Low, Medium, High or Uber (4K) quality. (the Gwent 4K texture DLC must be installed if you wish to export those)

Assets for card icons, borders and numbers can be found in the 'assets' folder either in this repository or where you installed the program.

![example-screenshot](https://github.com/pramberg451/gwentCardImageExporter/blob/master/exporter.png)

### Code ###
The code for GwentUtils and some of the json generating is based on this repository: https://github.com/GwentCommunityDevelopers/gwent-data

I am using both [UnityPy](https://pypi.org/project/UnityPy/) and [texture2ddecoder](https://pypi.org/project/texture2ddecoder/) to extract the card art. Many thanks to the developer for providing fixes so they work with Gwent's DXT1Crunched format.

### Building The Project ###
You can find a standalone executable on the [releases](https://github.com/pramberg451/gwentCardImageExporter/releases) page. Just simply download the zip, extract and run. All the needed assets come with it.

If for some reason you would like to run the program in your own Python environment and not as the standalone executable just make sure you have all the imports that are present in both gwentCardExporter.py and GwentUtils.py installed and it should work fine. I built and tested it using Python 3.8.2. Please let me know if you have any issues.

I am currently using pyinstaller to generate the standalone executable with no additions so if you would like to do that as well than that should be simple enough. 

NOTE: I am looking into using something different to generate the executable as the standalone has a much longer launch time than I would like. Any suggestions would be useful.

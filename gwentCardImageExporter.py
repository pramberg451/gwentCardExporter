import tkinter as tk
import tkinter.ttk as ttk
from pygubu.widgets.pathchooserinput import PathChooserInput
from UnityPy import AssetsManager
import texture2ddecoder
from PIL import Image
import json
from os import listdir, mkdir
from os.path import isfile
from tkinter import messagebox

class GwentCardImageExporter:
    def __init__(self, master=None):
        # Create main window and frame
        mainwindow = tk.Tk()
        mainFrame = ttk.Frame(mainwindow)

        # Add Gwent Installation Path Chooser
        gwentPathFrame = ttk.LabelFrame(mainFrame, text='1. Specify Gwent Installation Path', labelanchor='n')
        gwentPathInfoButton = ttk.Button(gwentPathFrame, text='?', width='3')
        gwentPathInfoButton.pack(side='left', padx='5')
        gwentPathInfoButton.configure(command= lambda: GwentCardImageExporter.showInfo(self, "Specify the folder in which Gwent is installed, usually named 'GWENT The Witcher Card Game' or 'Gwent'.\n\nIf you have the game installed on Steam you can usually find it at:\n  'C:/Program Files (x86)/Steam/steamapps/common/GWENT The Witcher Card Game'\n\nIf you have the game installed on GOG you can usually find it at:\n  'C:/Program Files (x86)/GOG Galaxy/Games/Gwent'"))
        gwentPathChooser = PathChooserInput(gwentPathFrame)
        gwentPathChooser.config(type='directory')
        gwentPathChooser.pack(fill='x', side='left', expand='true', pady='5')
        gwentPathFrame.pack(fill='x', pady='5', padx='5', side='top')

        # Open path file and load saved Gwent installation path
        # Create a file to save paths if one is not already made
        try:
            pathFile = open('savedPaths.txt', 'r')
        except:
            with open('savedPaths.txt', 'w') as pathFile:
                pass
            pathFile = open('savedPaths.txt', 'r')
        gwentPathChooser.configure(path=pathFile.readline().rstrip())

        # Add Card Data File Selector and Export Button
        cardDataFrame = ttk.Labelframe(mainFrame, text='2. Extract or update card data', labelanchor='n')

        # Add Card Data Info Button
        cardDataInfoButton = ttk.Button(cardDataFrame, text='?', width='3')
        cardDataInfoButton.pack(side='left', padx='5')
        cardDataInfoButton.configure(command= lambda: GwentCardImageExporter.showInfo(self, "In order to generate card images you first need to extract the card data from the game files.\n\nTo do so click the 'Export Data' button and save the file as a .json.\n\nIt should appear in the menu here and should load the data into the card list below so you can\nchoose specific cards to generate.\n\nThese .json card data files can be found in the 'card_data' folder in the programs directory\nand can also be used for your own personal Gwent projects.\n\nRight now they only contain the data to generate images but the plan is to format all\nthe card data from the games files so this program can be used as a proper card data exporter as well."))
        
        # Add combobox to select a json file
        self.currentJSON = ttk.Combobox(cardDataFrame)
        self.currentJSON.pack(side='left', fill='x', expand='true')

        # Try and list json files in 'card_data', create empty 'card_data' dir if none exists
        try:
            self.currentJSON['values'] = [x for x in listdir('card_data') if x.endswith(".json")]
        except FileNotFoundError:
            mkdir('card_data')
            self.currentJSON['values'] = [x for x in listdir('card_data') if x.endswith(".json")]
        
        # When a new json is selected load it into the card list view
        self.currentJSON.bind('<<ComboboxSelected>>', self.loadNewJSON)
        
        # Save number of files and set selection to the newest (highest version number)
        self.numberofFiles = len(self.currentJSON['values'])
        if self.numberofFiles != 0:
            self.currentJSON.current(self.numberofFiles - 1)

        # Add a button for exporting new card data
        exportDataButton = ttk.Button(cardDataFrame)
        exportDataButton.config(text='Export Data')
        exportDataButton.pack(side='left', padx='5', pady='5')
        exportDataButton.configure(command= lambda: GwentCardImageExporter.updateJSON(self, gwentPathChooser.cget('path')))

        cardDataFrame.pack(fill='x', pady='5', padx='5', side='top')

        # Add Card Options
        cardOptionsFrame = ttk.Labelframe(mainFrame, text='3. Specify card options', labelanchor='n')

        # Add three checkboxes for image options
        addBordersBox = ttk.Checkbutton(cardOptionsFrame)
        self.addBorders = tk.BooleanVar()
        self.addBorders.set(True)
        addBordersBox.config(text='Add Borders', variable=self.addBorders)
        addBordersBox.pack(anchor='nw', side='top', padx='5')

        addStrengthIconsBox = ttk.Checkbutton(cardOptionsFrame)
        self.addStrengthIcons = tk.BooleanVar()
        self.addStrengthIcons.set(True)
        addStrengthIconsBox.config(text='Add Strength/Icons', variable=self.addStrengthIcons)
        addStrengthIconsBox.pack(anchor='nw', side='top', padx='5')

        addProvisionsBox = ttk.Checkbutton(cardOptionsFrame)
        self.addProvisions = tk.BooleanVar()
        self.addProvisions.set(True)
        addProvisionsBox.config(text='Add Provisions', variable=self.addProvisions)
        addProvisionsBox.pack(anchor='nw', side='top', padx='5')

        # Add dividor
        separator1 = ttk.Separator(cardOptionsFrame)
        separator1.config(orient='horizontal')
        separator1.pack(fill='x', pady='5', side='top', padx='5')

        # Add Card Data File Selector and Export Button
        cardQualityFrame = ttk.Frame(cardOptionsFrame)

        # Add a label for choosing image quality
        qualityLabel = ttk.Label(cardQualityFrame, text='Image Quality:')
        qualityLabel.pack(side='left')

        # Add combobox to select a json file
        self.imageQuality = ttk.Combobox(cardQualityFrame)
        self.imageQuality.pack(side='left', fill='x', expand='true')
        self.imageQuality['values'] = ['Low','Medium', 'High', 'Uber (4K)']
        self.imageQuality.current(2)

        cardQualityFrame.pack(fill='x', pady='5', padx='5', side='top')
        
        # Add dividor
        separator2 = ttk.Separator(cardOptionsFrame)
        separator2.config(orient='horizontal')
        separator2.pack(fill='x', pady='5', side='top', padx='5')

        # Add radio buttons for all or only specfic images
        self.allImages = tk.IntVar()
        self.allImages.set(1)

        allImagesSelector = ttk.Radiobutton(cardOptionsFrame)
        allImagesSelector.config(text='All Images', variable=self.allImages, value=1)
        allImagesSelector.pack(anchor='nw', side='top', padx='5')

        specificImagesSelector = ttk.Radiobutton(cardOptionsFrame)
        specificImagesSelector.config(text='Specified Images', variable=self.allImages, value=0)
        specificImagesSelector.pack(anchor='nw', side='top', padx='5')

        # Add list of cards found in the card data file
        cardListFrame = ttk.Frame(cardOptionsFrame)

        # Set up treeview
        self.cardView = ttk.Treeview(cardListFrame, columns=('Name', 'ID'))
        self.cardView.config(selectmode='extended')
        self.cardView['show'] = 'headings'
        self.cardView.heading("Name", text ="Name", anchor="w") 
        self.cardView.heading("ID", text ="ID", anchor="w")
        self.cardView.bind('<<TreeviewSelect>>', self.selectSpecifiedImages)
        self.cardView.pack(side='left', expand='true')
        # Link a scrollbar to the treeview
        scrollBar = ttk.Scrollbar(cardListFrame, orient="vertical")
        scrollBar.configure(command = self.cardView.yview)
        self.cardView.config(yscrollcommand=scrollBar.set)
        scrollBar.pack(side='left', fill='both')

        cardListFrame.pack(side='top', padx='5')

        # Add a search box to the card list
        cardSearchFrame = ttk.Frame(cardOptionsFrame)

        # label for search box
        searchLabel = ttk.Label(cardSearchFrame, text='Search:')
        searchLabel.pack(side='left')
        # add search box for card list
        self.detachedCards = []
        searchText = tk.StringVar()
        searchText.trace('w', lambda name, index, mode, searchText=searchText: GwentCardImageExporter.filterCardlist(self, searchText.get()))
        self.searchBox = ttk.Entry(cardSearchFrame, textvariable=searchText)
        self.searchBox.pack(side='left', expand='true', fill='x')

        cardSearchFrame.pack(fill='x', side='top', pady='8', padx='5')
        
        # If one is selected load the json file into the card list
        if self.numberofFiles != 0:
            GwentCardImageExporter.loadNewJSON(self, None)

        cardOptionsFrame.pack(fill='x', pady='5', padx='5', side='top')

        # Add Image Path Installation Chooser
        imagePathFrame = ttk.LabelFrame(mainFrame, text='4. Choose where to save', labelanchor='n')
        imagePathInfoButton = ttk.Button(imagePathFrame, text='?', width='3')
        imagePathInfoButton.pack(side='left', padx='5')
        imagePathInfoButton.configure(command= lambda: GwentCardImageExporter.showInfo(self, "Specifiy the folder where you want to save the generated images"))
        imagePathChooser = PathChooserInput(imagePathFrame)
        imagePathChooser.config(type='directory')
        imagePathChooser.pack(fill='x', side='left', expand='true', pady='5')
        imagePathFrame.pack(fill='x', pady='5', padx='5', side='top')

        # Load saved image save path and close path file
        imagePathChooser.configure(path=pathFile.readline().rstrip())
        pathFile.close()

        # Add a button to generate cards
        generateButton = ttk.Button(mainFrame)
        generateButton.config(text='Generate')
        generateButton.pack(side='top', pady='5')
        generateButton.configure(command= lambda: GwentCardImageExporter.generateCards(self, imagePathChooser.cget('path'), gwentPathChooser.cget('path')))

        # Set up final window
        mainFrame.config(height='690', width='400')
        mainFrame.pack(padx='3', pady='3', side='top')
        mainwindow.geometry('450x690')
        mainwindow.resizable(False, False)
        mainwindow.title('Gwent Card Image Exporter')
        mainwindow.iconbitmap('assets/favicon.ico')
        self.mainwindow = mainwindow
    
    # If a selecton is made in the card list, change to generate only specific images
    def selectSpecifiedImages(self, event):
        empty = ()
        # Don't change to specific images if the selection removed the only selection
        if self.cardView.selection() != empty:
            self.allImages.set(0)
    
    # Dialog box to show info for (?) buttons
    def showInfo(self, info):
        pathDialog = tk.Toplevel()
        pathDialog.title("Info")
        dialogFrame = ttk.Frame(pathDialog)
        infoLabel = ttk.Label(dialogFrame, text=info)
        infoLabel.pack(padx='10', pady='5', side='top')
        closeWindow = ttk.Button(dialogFrame, text="Ok", command=lambda: pathDialog.destroy())
        closeWindow.pack(pady='5', side='top')
        dialogFrame.pack(side='top', padx='10', pady='10')
        pathDialog.resizable(False, False)
        pathDialog.iconbitmap('assets/favicon.ico')

    # Loads a JSON file into the card list
    def loadNewJSON(self, event):
        # Load json file specified in the combobox
        with open("card_data/" + self.currentJSON.get(), "r") as json_file:
            self.cardData = json.load(json_file)
            # Clear all items previously listed
            self.cardView.delete(*self.cardView.get_children())
            # If the card is not null or a Leader load it into the list
            for card in self.cardData:
                if(self.cardData[card]['cardType'] is not None and self.cardData[card]['cardType'] != 'Leader' and self.cardData[card]['name']['en-US'] is not None):
                    self.cardView.insert('', 'end', text=self.cardData[card]['name']['en-US'], values=(self.cardData[card]['name']['en-US'],self.cardData[card]['ingameId']))

    # Searches card list, detaching a reattaching items
    def filterCardlist(self, searchText):
        cards = list(self.detachedCards) + list(self.cardView.get_children())
        # Clear detached cards
        self.detachedCards = []
        for card in cards:
            name = self.cardView.item(card, 'text')
            # If name does match move it into place on the list
            if searchText.lower() in name.lower():
                self.cardView.reattach(card, '', int(card[1:], 16) - 1)
            # IF names doesn't match detach and save it in detached cards
            else:
                self.detachedCards.append(card)
                self.cardView.detach(card)

    # Generate card images
    def generateCards(self, imagePath, gwentPath):
        MAX_CARD_STRENGTH = 99
        MAX_CARD_PROVISIONS = 99
        MAX_CARD_ARMOR = 99

        # Save chosen paths to a file
        with open('savedPaths.txt', 'w') as pathFile:
            pathFile.write(gwentPath + '\n')
            pathFile.write(imagePath + '\n')

        # Select all or certain cards
        if self.allImages.get() and self.numberofFiles:
            cardsToGenerate = self.cardData
        else:
            cardsToGenerate = []
            for card in self.cardView.selection():
                cardsToGenerate.append(self.cardView.set(card, column='ID'))

        numberOfCards = len(cardsToGenerate)
        cardsCompleted = 0

        # Raise and error if gwent path, save path, or json file are not valid and if no cards were slected
        if not gwentPath or not (gwentPath.endswith("GWENT The Witcher Card Game") or gwentPath.endswith("Gwent")):
            messagebox.showerror("No Gwent Path", "Path to Gwent installation was invalid or not specified.")
            return
        if not imagePath:
            messagebox.showerror("No Image Path", "No path to save images to was specified.")
            return
        if not self.numberofFiles:
            messagebox.showerror("No JSON Data", "No JSON card data file was selected.")
            return
        if not numberOfCards and not self.allImages.get():
            messagebox.showerror("No Card Selected", "No cards were selected.")
            return
        # Check to see if you have 4K graphics installed
        if (self.imageQuality.get() == "Uber (4K)") and not isfile("".join([gwentPath, "/Gwent_Data/StreamingAssets/bundledassets/cardassets/textures/standard/uber/10000000"])):
            messagebox.showerror("Uber Graphics Not Installed", "You do not have the 4K graphics for Gwent installed.")
            return
        
        # Launch progress bar window
        progressWindow = tk.Toplevel()
        progressWindow.title("Generating...")

        jsonFrame = ttk.Frame(progressWindow)

        # Add a label to show how many cards have been completed
        progressString = tk.StringVar()
        progressString.set(" ".join([str(cardsCompleted), "of", str(numberOfCards), "completed"]))
        progressLabel = ttk.Label(jsonFrame, textvariable = progressString)
        progressLabel.pack(padx='10', pady='5', side='top')

        # Add a progress bar
        progressBar = ttk.Progressbar(jsonFrame)
        progressBar.config(orient='horizontal', maximum=numberOfCards, length=250, mode='determinate')
        progressBar.pack(padx='10', pady='5', side='top')
        
        # Add a cancel button to quit early
        running = tk.BooleanVar()
        running.set(True)
        cancelButton = ttk.Button(jsonFrame, text='Cancel', command = lambda: running.set(False))
        cancelButton.pack(pady='5', side='top')

        jsonFrame.config(height='250', width='200')
        jsonFrame.pack(side='top')

        progressWindow.config(height='250', width='200')
        progressWindow.iconbitmap('assets/favicon.ico')
        progressWindow.resizable(False, False)
        progressWindow.update()

        # Set the dimensions of the final cards based on quality
        dimensions = (992, 1424)
        quality = "uber"
        if (self.imageQuality.get() == "High"):
            dimensions = (497, 713)
            quality = "high"
        elif (self.imageQuality.get() == "Medium"):
            dimensions = (249, 357)
            quality = "medium"
        elif (self.imageQuality.get() == "Low"):
            dimensions = (125, 179)
            quality = "low"

        for card in cardsToGenerate:
            # Exit if cancel was pressed
            if not running.get():
                break

            # if the card is valid and not a leader
            if self.cardData[card]['type'] != 'Leader' and self.cardData[card]['type'] is not None and self.cardData[card]['name']['en-US'] is not None:
                # If the image is low quality, then export and crop it as a medium instead
                # because the low resolution card arts are stored differently in the game files the higher qualities
                if self.imageQuality.get() == "Low":
                    dimensions = (249, 357)
                    quality = "medium"
                
                # Export and crop the card art

                am = AssetsManager("".join([gwentPath, "/Gwent_Data/StreamingAssets/bundledassets/cardassets/textures/standard/", quality, "/", self.cardData[card]['ingameArtId'], "0000"]))
                for asset in am.assets.values():
                    for obj in asset.objects.values():
                        if obj.type == "Texture2D":
                            data = obj.read()
                            img = data.image
                
                newImg = img.crop((0,0,dimensions[0],dimensions[1]))
                
                # Reset the quality specifics back to low if it is low and was exported as a medium
                if self.imageQuality.get() == "Low":
                    dimensions = (125, 179)
                    quality = "low"
                    newImg = newImg.resize(dimensions)

                # Add gold or bronze border based on type (border tier not card type)
                if self.addBorders.get():
                    asset = Image.open("".join(["assets/", self.cardData[card]['type'], ".png"]))
                    if (quality != "uber"):
                        asset = asset.resize(dimensions)
                    newImg = Image.alpha_composite(newImg, asset)

                # Retrieve card type
                cardType = self.cardData[card]['cardType']

                # If the optons said to add strength or type icons
                if self.addStrengthIcons.get():
                    # Get icon diamond based on faction
                    diamond = Image.open("".join(["assets/", self.cardData[card]['faction'], "_diamond.png"]))
                    # Get rarity icon based on rarity
                    rarity = Image.open("".join(["assets/", self.cardData[card]['rarity'], ".png"]))
                    # Combine the two together
                    strengthIcons = Image.alpha_composite(diamond, rarity)
                    
                    # If the card is a unit add strength and potentially armor
                    if cardType == 'Unit':
                        # Check strength and add the corresponding number to the card
                        cardStrength = self.cardData[card]['strength']
                        if cardStrength > MAX_CARD_STRENGTH:
                            cardStrength = MAX_CARD_STRENGTH
                        strengthIcons = GwentCardImageExporter.placeNumber(self, cardStrength, "strength", strengthIcons)

                        # Check if the card has armor and if so add the corresponding symbol and number
                        cardArmor = self.cardData[card]['armor']
                        if cardArmor > MAX_CARD_ARMOR:
                            cardArmor = MAX_CARD_ARMOR
                        if cardArmor > 0:
                            armor = Image.open("assets/Armor.png")
                            strengthIcons = Image.alpha_composite(strengthIcons, armor)
                            strengthIcons = GwentCardImageExporter.placeNumber(self, cardArmor, "armor", strengthIcons)
                    
                    # If the card is a strategem add the banner icon
                    elif cardType == 'Strategem':
                        strategem = Image.open("assets/Strategem.png")
                        strengthIcons = Image.alpha_composite(strengthIcons, strategem)

                    # If the card is a special add the flame icon
                    elif cardType == 'Spell':
                        special = Image.open("assets/Special.png")
                        strengthIcons = Image.alpha_composite(strengthIcons, special)

                    # If the card is an artifact add the goblet icon
                    elif cardType == 'Artifact':
                        artifact = Image.open("assets/Artifact.png")
                        strengthIcons = Image.alpha_composite(strengthIcons, artifact)
                    
                    # Downsize if not generating 4K qualty
                    if (quality != "uber"):
                        strengthIcons = strengthIcons.resize(dimensions)
                    
                    # Add the final composite to the image
                    newImg = Image.alpha_composite(newImg, strengthIcons)

                # If not a strategem and we are adding provisons
                if self.addProvisions.get() and not cardType == 'Strategem':
                    # Get provisons icon
                    provisionIcon = Image.open("assets/Provisions.png")
                    # Get provisions square background based on the faction
                    provisionSquare = Image.open("".join(["assets/", self.cardData[card]['faction'], "_prov.png"]))
                    # Combine the two together
                    provisions = Image.alpha_composite(provisionIcon, provisionSquare)

                    # Check the provisions number and add the corresponding number
                    cardProvisions = self.cardData[card]['provision']
                    if cardProvisions > MAX_CARD_PROVISIONS:
                        cardProvisions == MAX_CARD_ARMOR
                    provisions = GwentCardImageExporter.placeNumber(self, cardProvisions, "provisions", provisions)

                    # Downsize if not generating in 4K quality
                    if (quality != "uber"):
                        provisions = provisions.resize(dimensions)
                    
                    # Add the final composite to the image
                    newImg = Image.alpha_composite(newImg, provisions)
                
                # Save the card using the card's name and id number
                newImg.save("".join([imagePath, "/", self.cardData[card]['name']['en-US'].replace(':', ''), "_", self.cardData[card]['ingameId'], "_", quality, ".png"]))
            
            # Update progress label and progress bar
            cardsCompleted += 1
            progressString.set(" ".join([str(cardsCompleted), "of", str(numberOfCards), "completed"]))
            progressBar.step(1)
            progressWindow.update()
        
        progressWindow.destroy()

    # Add a number to the card image
    def placeNumber(self, value, type, image):
        # Set a default offset to account for centering single digits
        offset = 5

        # Set up base coordinates for placing numbers based on type
        # Save either s or p for use in filename later
        if type == "strength":
            x = 90
            y = 65
            numberType = "s"
        elif type == "provisions":
            x = 800
            y = 1185
            numberType = "p"
            offset += 5
        elif type == "armor":
            x = 800
            y = 65
            numberType = "s"

        # If two digits place the tens digit offset to the left
        if value > 9:
            offset = 40
            tensAsset = Image.open("".join(["assets/", numberType, str(value // 10), ".png"]))
            # Increase the offset again if one of the digits is not 1
            if value > 19 and value % 10 != 1:
                offset += 10
            image.paste(tensAsset, (x - offset, y), tensAsset)
        
        # Add the ones digit and offset to the right
        onesAsset = Image.open("".join(["assets/", numberType, str(value % 10), ".png"]))
        image.paste(onesAsset, (x + offset, y), onesAsset)

        return image

    # Window for updating the card data files
    def updateJSON(self, gwentPath):
        jsonWindow = tk.Toplevel()
        jsonWindow.title("Export new card data...")

        jsonFrame = ttk.Frame(jsonWindow)

        # Add help labels for naming the file
        conventionLabel1 = ttk.Label(jsonFrame, text="Saving as an already generated file will overwrite the current one.")
        conventionLabel1.pack()
        conventionLabel2 = ttk.Label(jsonFrame, text="Game version is a good way to keep track of different data versions.")
        conventionLabel2.pack()
        conventionLabel3 = ttk.Label(jsonFrame, text="Example: 'cards-v7-0-2.json'")
        conventionLabel3.pack()

        # Add filename entry box, button and label
        entryFrame = ttk.Frame(jsonFrame)
        filenameLabel = ttk.Label(entryFrame, text = "Save as:")
        filenameLabel.pack(padx='10', pady='5', side='left')
        filenameEntry = ttk.Entry(entryFrame)
        filenameEntry.pack(side='left', expand='true', fill='x')
        generateJSONbutton = ttk.Button(entryFrame, text="Generate", command= lambda: GwentCardImageExporter.generateCardData(self, filenameEntry.get(), progressBar, jsonWindow, gwentPath))
        generateJSONbutton.pack(side='left', padx='4')
        entryFrame.pack(side='top', padx='5', pady='5')

        # Add progress bar
        progressBar = ttk.Progressbar(jsonFrame)
        progressBar.config(orient='horizontal', length='400', mode='determinate')
        progressBar.pack(padx='10', pady='5', side='bottom')

        jsonFrame.pack(side='top', pady='5', padx='5')

        jsonWindow.config(height='250', width='200')
        jsonWindow.resizable(False, False)
        jsonWindow.iconbitmap('assets/favicon.ico')

    # Generate the card data json file
    def generateCardData(self, filename, progressBar, jsonWindow, gwentPath):
        # Raise an error if filename is not valid
        if not filename or not filename.endswith(".json"):
            messagebox.showerror("No File Name", "File name was not specified or is not a .json")
            return
        # Raise an error if Gwent path is not specified or invalid
        if not gwentPath or not (gwentPath.endswith("GWENT The Witcher Card Game") or gwentPath.endswith("Gwent")):
            messagebox.showerror("No Gwent Path", "Path to Gwent installation was invalid or not specified.")
            return

        cards = {}
        
        # Show progress in the bar for feedback
        progressBar.config(maximum=30)
        progressBar.step(5)
        jsonWindow.update_idletasks()

        # Unzip the data_definitions folder to get xml files
        import zipfile
        with zipfile.ZipFile(gwentPath + "/Gwent_Data/StreamingAssets/data_definitions", 'r') as cardDefinitions:
            cardDefinitions.extractall("data_definitions/")

        progressBar.step(5)
        jsonWindow.update_idletasks()
        
        # Get the card info from the xml file
        import GwentUtils
        gwentDataHelper = GwentUtils.GwentDataHelper("data_definitions/")
        card_templates = gwentDataHelper.card_templates

        progressBar.config(maximum=len(card_templates) + 30)

        # Add each card as a json entry
        for template_id in card_templates:
            template = card_templates[template_id]
            card = {}

            # ID
            card_id = template.attrib['Id']
            
            # In game ID
            card['ingameId'] = card_id
            
            # Strength
            card['strength'] = int(template.find('Power').text)

            # Tier
            tier = int(template.find('Tier').text)
            card['type'] = GwentUtils.TIERS.get(tier)

            # Type
            card_type = int(template.find('Type').text)
            card['cardType'] = GwentUtils.TYPES.get(card_type)

            # Faction and Secondary Faction
            card['faction'] = GwentUtils.FACTIONS.get(int(template.find('FactionId').text))
            secondaryFaction = template.find('SecondaryFactionId')
            if secondaryFaction != None and int(secondaryFaction.text) in GwentUtils.FACTIONS:
                card['secondaryFaction'] = GwentUtils.FACTIONS.get(int(secondaryFaction.text))

            # Provisions
            card['provision'] = int(template.find('Provision').text)
            
            # Card Name
            card['name'] = {}
            card['flavor'] = {}
            for region in GwentUtils.LOCALES:
                card['name'][region] = gwentDataHelper.card_names.get(region).get(card_id)
                card['flavor'][region] = gwentDataHelper.flavor_strings.get(region).get(card_id)

            # Tooltips
            card['info'] = {}
            card['infoRaw'] = {}
            for locale in GwentUtils.LOCALES:
                tooltip = gwentDataHelper.tooltips[locale].get(card_id)
                if tooltip is not None:
                    card['infoRaw'][locale] = tooltip
                    card['info'][locale] = GwentUtils.clean_html(tooltip)

            # Keywords.
            card['keywords'] = gwentDataHelper.keywords.get(card_id)

            # Loyalty
            card['loyalties'] = []
            placement = template.find('Placement')
            if placement.attrib['PlayerSide'] != "0":
                card['loyalties'].append("Loyal")
            if placement.attrib['OpponentSide'] != "0":
                card['loyalties'].append("Disloyal")

            # Categories
            card['categories'] = []
            card['categoryIds'] = []

            # There are 2 category nodes
            for node in ["PrimaryCategory", "Categories"]:
                for multiplier in range(2):
                    # e0, e1
                    e = "e{0}".format(multiplier)
                    categories_sum = int(template.find(node).find(e).attrib['V'])
                    for category, bit in enumerate("{0:b}".format(categories_sum)[::-1]):
                        if bit == '1':
                            # e1 categories are off by 64.
                            adjusted_category = category + (64 * multiplier)
                            card['categoryIds'].append("card_category_{0}".format(adjusted_category))

            categories_en_us = gwentDataHelper.categories["en-US"]
            for category_id in card['categoryIds']:
                if category_id in categories_en_us:
                    card['categories'].append(categories_en_us[category_id])


            # Rarity
            rarity = int(template.find('Rarity').text)
            card['rarity'] = GwentUtils.RARITIES.get(rarity)
            
            # Art ID
            art_id = template.attrib.get('ArtId')
            if art_id != None:
                card['ingameArtId'] = art_id

            # Artist
            artist = gwentDataHelper.artists.get(art_id)
            if artist != None:
                card['artist'] = artist

            # Related Tokens
            tokens = gwentDataHelper.tokens.get(card_id)
            card['related'] = tokens
            
            # Armor
            armor = gwentDataHelper.armor.get(card_id)
            if armor != None and GwentUtils.TYPES.get(card_type) == "Unit":
                card['armor'] = int(armor)

            cards[card_id] = card
            progressBar.step(1)
            jsonWindow.update_idletasks()

        # Save the json file
        GwentUtils.save_json("card_data/" + filename, cards)

        # If the file is new, add it to the file list in the combobox, select it and load it
        if filename not in self.currentJSON['values']:
            self.currentJSON['values'] = (*self.currentJSON['values'], filename)
            self.numberofFiles += 1
        self.currentJSON.current(len(self.currentJSON['values']) - 1)
        GwentCardImageExporter.loadNewJSON(self, "<<ComboboxSelected>>")
        jsonWindow.destroy()

    def run(self):
        self.mainwindow.mainloop()

if __name__ == '__main__':
    app = GwentCardImageExporter()
    app.run()

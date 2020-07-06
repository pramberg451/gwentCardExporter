import tkinter as tk
import tkinter.ttk as ttk
from pygubu.widgets.pathchooserinput import PathChooserInput
from UnityPy import AssetsManager
import texture2ddecoder
from PIL import Image
import json
import GwentUtils
from os import listdir, mkdir
from tkinter import messagebox
import zipfile

class GwentImageGenerator:
    def __init__(self, master=None):
        # build ui
        mainwindow = tk.Tk()
        mainFrame = ttk.Frame(mainwindow)

        pathOptions = ttk.Labelframe(mainFrame)

        # Add Gwent Installation Path Chooser
        gwentPathLabel = ttk.Label(pathOptions, text='Gwent Installation Path')
        gwentPathLabel.pack(side='top')
        gwentPathFrame = ttk.Frame(pathOptions)
        gwentPathInfoButton = ttk.Button(gwentPathFrame, text='?', width='3')
        gwentPathInfoButton.pack(side='left')
        gwentPathInfoButton.configure(command= lambda: GwentImageGenerator.showPathSelectionInfo(self, "Specify the folder in which Gwent is installed, usually named 'GWENT The Witcher Card Game' or 'Gwent'.\n\nIf you have the game installed on Steam you can usually find it at:\n  'C:/Program Files (x86)/Steam/steamapps/common/GWENT The Witcher Card Game'\n\nIf you have the game installed on GOG you can usually find it at:\n  'C:/Program Files (x86)/GOG Galaxy/Games/Gwent'"))
        gwentPathChooser = PathChooserInput(gwentPathFrame)
        gwentPathChooser.config(type='directory')
        gwentPathChooser.pack(fill='x', side='left', expand='true', padx='5')
        gwentPathFrame.pack(fill='x', side='top')

        # Open path file and load saved gwent installation path
        try:
            pathFile = open('savedPaths.txt', 'r')
        except:
            with open('savedPaths.txt', 'w') as pathFile:
                pass
            pathFile = open('savedPaths.txt', 'r')
        gwentPathChooser.configure(path=pathFile.readline().rstrip())

        # Add Image Path Installation Chooser
        imagePathLabel = ttk.Label(pathOptions, text='Image Destination Path')
        imagePathLabel.pack(side='top')
        imagePathFrame = ttk.Frame(pathOptions)
        imagePathInfoButton = ttk.Button(imagePathFrame, text='?', width='3')
        imagePathInfoButton.pack(side='left')
        imagePathInfoButton.configure(command= lambda: GwentImageGenerator.showPathSelectionInfo(self, "Specifiy the folder where you want to save the generated images"))
        imagePathChooser = PathChooserInput(imagePathFrame)
        imagePathChooser.config(type='directory')
        imagePathChooser.pack(fill='x', side='left', expand='true', padx='5')
        imagePathFrame.pack(fill='x', side='top')

        # Load saved image save path and close path file
        imagePathChooser.configure(path=pathFile.readline().rstrip())
        pathFile.close()

        # Set up final pathOptions frame settings
        pathOptions.config(height='200', labelanchor='n', padding='10', text='Path Options')
        pathOptions.config(width='200')
        pathOptions.pack(fill='both', side='top')

        # Make jsonOptionsFrame
        jsonOptions = ttk.Labelframe(mainFrame)

        # label for combobox
        currentJSONLabel = ttk.Label(jsonOptions, text='Card Data File:')
        currentJSONLabel.pack(side='left', padx='8')

        # Combobox for current json file being used
        self.currentJSON = ttk.Combobox(jsonOptions)
        self.currentJSON.pack(side='left', fill='x', expand='true')
        # Try and list json files in 'card_data', create empty 'card_data' dir if none exists
        try:
            self.currentJSON['values'] = [x for x in listdir('card_data') if x.endswith(".json")]
        except FileNotFoundError:
            mkdir('card_data')
            self.currentJSON['values'] = [x for x in listdir('card_data') if x.endswith(".json")]
        
        self.currentJSON.bind('<<ComboboxSelected>>', self.loadNewJSON)
        self.numberofFiles = len(self.currentJSON['values'])
        # Set defualt file to the highest version number (last in the directory)
        if self.numberofFiles != 0:
            self.currentJSON.current(self.numberofFiles - 1)

        # Export new json button
        newJSON = ttk.Button(jsonOptions)
        newJSON.config(text='Update Data')
        newJSON.pack(side='left', padx='8', pady='4')
        newJSON.configure(command= lambda: GwentImageGenerator.updateJSON(self, gwentPathChooser.cget('path')))

        # configure jsonOptions frame
        jsonOptions.config(labelanchor='n', text='JSON Options')
        jsonOptions.pack(expand='true', fill='x', side='top')

        cardOptions = ttk.Labelframe(mainFrame)

        # Add three checkboxes for image options
        addBordersBox = ttk.Checkbutton(cardOptions)
        self.addBorders = tk.BooleanVar()
        self.addBorders.set(True)
        addBordersBox.config(text='Add Borders', variable=self.addBorders)
        addBordersBox.pack(anchor='nw', side='top')

        addStrengthIconsBox = ttk.Checkbutton(cardOptions)
        self.addStrengthIcons = tk.BooleanVar()
        self.addStrengthIcons.set(True)
        addStrengthIconsBox.config(text='Add Strength/Icons', variable=self.addStrengthIcons)
        addStrengthIconsBox.pack(anchor='nw', side='top')

        addProvisionsBox = ttk.Checkbutton(cardOptions)
        self.addProvisions = tk.BooleanVar()
        self.addProvisions.set(True)
        addProvisionsBox.config(text='Add Provisions', variable=self.addProvisions)
        addProvisionsBox.pack(anchor='nw', side='top')

        # Add dividor
        separator = ttk.Separator(cardOptions)
        separator.config(orient='horizontal')
        separator.pack(fill='x', pady='5', side='top')

        # Add radio buttons for all or only specfic images
        self.allImages = tk.IntVar()
        self.allImages.set(1)
        allImagesSelector = ttk.Radiobutton(cardOptions)
        allImagesSelector.config(text='All Images', variable=self.allImages, value=1)
        allImagesSelector.pack(anchor='nw', side='top')
        specificImagesSelector = ttk.Radiobutton(cardOptions)
        specificImagesSelector.config(text='Specified Images', variable=self.allImages, value=0)
        specificImagesSelector.pack(anchor='nw', side='top')

        cardListFrame = ttk.Frame(cardOptions)

        # Set up treeview to display all cards in selected json file
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
        scrollBar.pack(side='left', fill='y')

        cardListFrame.pack(fill='both', side='top')

        cardSearchFrame = ttk.Frame(cardOptions)

        # label for search box
        searchLabel = ttk.Label(cardSearchFrame, text='Search:')
        searchLabel.pack(side='left')

        # add search box for card list
        self.detachedCards = []
        searchText = tk.StringVar()
        searchText.trace('w', lambda name, index, mode, searchText=searchText: GwentImageGenerator.filterCardlist(self, searchText.get()))
        self.searchBox = ttk.Entry(cardSearchFrame, textvariable=searchText)
        self.searchBox.pack(side='left', expand='true', fill='x')

        cardSearchFrame.pack(fill='x', side='top', pady='8')
        
        # If one is selected load the json file into the card list
        if self.numberofFiles != 0:
            GwentImageGenerator.loadNewJSON(self, None)

        cardOptions.config(labelanchor='n', padding='10', text='Card Options')
        cardOptions.pack(fill='both', side='top')

        # Add a button to generate cards
        generateButton = ttk.Button(mainFrame)
        generateButton.config(text='Generate')
        generateButton.pack(side='top', pady='5')
        generateButton.configure(command= lambda: GwentImageGenerator.generateCards(self, imagePathChooser.cget('path'), gwentPathChooser.cget('path')))

        # Set up final window
        mainFrame.config(height='640', width='400')
        mainFrame.pack(padx='3', pady='3', side='top')
        mainwindow.geometry('450x640')
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
    
    # Dialog box to show info on which Gwent and Image paths to select
    def showPathSelectionInfo(self, info):
        pathDialog = tk.Toplevel()
        pathDialog.title("Gwent Path Info")
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
        with open("card_data/" + self.currentJSON.get(), "r") as json_file:
            self.cardData = json.load(json_file)
            self.cardView.delete(*self.cardView.get_children())
            for card in self.cardData:
                if(self.cardData[card]['cardType'] is not None and self.cardData[card]['cardType'] != 'Leader' and self.cardData[card]['name']['en-US'] is not None):
                    self.cardView.insert('', 'end', text=self.cardData[card]['name']['en-US'], values=(self.cardData[card]['name']['en-US'],self.cardData[card]['ingameId']))

    # Searches card list, detaching a reattaching items
    def filterCardlist(self, searchText):
        cards = list(self.detachedCards) + list(self.cardView.get_children())
        self.detachedCards = []
        for card in cards:
            name = self.cardView.item(card, 'text')
            if searchText.lower() in name.lower():
                self.cardView.reattach(card, '', int(card[1:], 16) - 1)
            else:
                self.detachedCards.append(card)
                self.cardView.detach(card)

    # Generate card images
    def generateCards(self, imagePath, gwentPath):
        # Maximum values so a correct file is always chosen
        MAX_CARD_STRENGTH = 13
        MAX_CARD_ARMOR = 10
        MAX_CARD_PROVISIONS = 14

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

        if not gwentPath or not gwentPath.endswith("GWENT The Witcher Card Game") or not gwentPath.endswith("Gwent"):
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

        labelString = tk.StringVar()
        labelString.set(str(cardsCompleted) + " of " + str(numberOfCards) + " completed")
        progressWindow = tk.Toplevel()
        progressWindow.title("Generating...")
        progressFrame = ttk.Frame(progressWindow)
        progressLabel = ttk.Label(progressFrame, textvariable = labelString)
        progressLabel.pack(padx='10', pady='5', side='top')
        progressBar = ttk.Progressbar(progressFrame)
        progressBar.config(orient='horizontal', maximum=numberOfCards, length=250, mode='determinate')
        progressBar.pack(padx='10', pady='5', side='top')
        running = tk.BooleanVar()
        running.set(True)
        cancelButton = ttk.Button(progressFrame, text='Cancel', command = lambda: running.set(False))
        cancelButton.pack(pady='5', side='top')
        progressFrame.config(height='250', width='200')
        progressFrame.pack(side='top')
        progressWindow.config(height='250', width='200')
        progressWindow.iconbitmap('assets/favicon.ico')
        progressWindow.resizable(False, False)
        progressWindow.update()
        # For each card in the file
        for card in cardsToGenerate:
            if not running.get():
                break
            # if the card is collectible and not a leader
            if self.cardData[card]['type'] != 'Leader' and self.cardData[card]['type'] is not None and self.cardData[card]['name']['en-US'] is not None:
                # load and crop the card art
                am = AssetsManager(gwentPath + "/Gwent_Data/StreamingAssets/bundledassets/cardassets/textures/standard/high/" + self.cardData[card]['ingameArtId']  + "0000")
                for asset in am.assets.values():
                    for obj in asset.objects.values():
                        if obj.type == "Texture2D":
                            data = obj.read()
                            img = data.image
                newImg = img.crop((0,0,496,712))

                # add gold or bronze border based on type
                if self.addBorders.get():
                    asset = Image.open("assets/" + self.cardData[card]['type'] + ".png")
                    newImg = Image.alpha_composite(newImg, asset)

                # retrieve card type
                cardType = self.cardData[card]['cardType']

                if self.addStrengthIcons.get():
                    # add icon diamond based on faction
                    asset = Image.open("assets/" + self.cardData[card]['faction'] + "_diamond.png")
                    newImg = Image.alpha_composite(newImg, asset)

                    # add rarity icon based on rarity
                    asset = Image.open("assets/" + self.cardData[card]['rarity'] + ".png")
                    newImg = Image.alpha_composite(newImg, asset)

                    # if the card is a strategem add the banner icon (no provisions needed)
                    if cardType == 'Strategem':
                        asset = Image.open("assets/Strategem.png")
                        newImg = Image.alpha_composite(newImg, asset)
                    # if the card is a unit add strength and potentially armor
                    elif cardType == 'Unit':
                        # Check strength and add the corresponding number to the card
                        cardStrength = self.cardData[card]['strength']
                        if cardStrength > MAX_CARD_STRENGTH:
                            cardStrength = 0
                        asset = Image.open("assets/s_" + str(cardStrength) + ".png")
                        newImg = Image.alpha_composite(newImg, asset)

                        # Check if the card has armor and if so ass the corresponding symbol and number
                        cardArmor = self.cardData[card]['armor']
                        if cardArmor <= MAX_CARD_ARMOR and cardArmor > 0:
                            asset = Image.open("assets/armor.png")
                            newImg = Image.alpha_composite(newImg, asset)
                            asset = Image.open("assets/a_" + str(cardArmor) + ".png")
                            newImg = Image.alpha_composite(newImg, asset)
                    # if the card is a special (no strength or armor needed)
                    elif cardType == 'Spell':
                        # place flame icon
                        asset = Image.open("assets/Special.png")
                        newImg = Image.alpha_composite(newImg, asset)
                    # if the card is an artifact (no strength or armor needed)
                    elif cardType == 'Artifact':
                        # place goblet icon
                        asset = Image.open("assets/Artifact.png")
                        newImg = Image.alpha_composite(newImg, asset)
                
                if self.addProvisions.get() and not cardType == 'Strategem':
                    # add provisons icon
                    asset = Image.open("assets/provisions.png")
                    newImg = Image.alpha_composite(newImg, asset)

                    # add provisions square background based on the faction
                    asset = Image.open("assets/" + self.cardData[card]['faction'] + "_prov.png")
                    newImg = Image.alpha_composite(newImg, asset)

                    # check the provisions number and add the corresponding number
                    cardProvisions = self.cardData[card]['provision']
                    if cardProvisions > MAX_CARD_PROVISIONS:
                        cardProvisions == 0
                    asset = Image.open("assets/p_" + str(cardProvisions) + ".png")
                    newImg = Image.alpha_composite(newImg, asset)
                
                # save the card using the card's id number
                newImg.save(imagePath + "/" + self.cardData[card]['ingameId'] + ".png")
            cardsCompleted += 1
            labelString.set(str(cardsCompleted) + " of " + str(numberOfCards) + " completed")
            progressBar.step(1)
            progressWindow.update()
        
        progressWindow.destroy()

    # Window for updating the card data files
    def updateJSON(self, gwentPath):
        jsonWindow = tk.Toplevel()
        jsonWindow.title("Export new card data...")
        entryFrame = ttk.Frame(jsonWindow)
        filenameLabel = ttk.Label(entryFrame, text = "Save as:")
        filenameLabel.pack(padx='10', pady='5', side='left')
        filenameEntry = ttk.Entry(entryFrame)
        filenameEntry.pack(side='left', expand='true', fill='x')
        generateJSONbutton = ttk.Button(entryFrame, text="Generate", command= lambda: GwentImageGenerator.generateCardData(self, filenameEntry.get(), progressBar, jsonWindow, gwentPath))
        generateJSONbutton.pack(side='left', padx='4')
        progressFrame = ttk.Frame(jsonWindow)
        conventionLabel1 = ttk.Label(progressFrame, text=" - Game version is a good way to keep track of different data versions", justify='left')
        conventionLabel1.pack()
        conventionLabel2 = ttk.Label(progressFrame, text=" - If you save as an already existing filename then the old one will be overwritten", justify='left')
        conventionLabel2.pack()
        conventionLabel3 = ttk.Label(progressFrame, text=" - Must be saved as a .json file", justify='left')
        conventionLabel3.pack()
        progressBar = ttk.Progressbar(progressFrame)
        progressBar.config(orient='horizontal', length='400', mode='determinate')
        progressBar.pack(padx='10', pady='5', side='bottom')
        entryFrame.pack(side='top', padx='5', pady='5')
        progressFrame.pack(side='top')
        jsonWindow.config(height='250', width='200')
        jsonWindow.resizable(False, False)
        jsonWindow.iconbitmap('assets/favicon.ico')

    # Generate the card data json file
    def generateCardData(self, filename, progressBar, jsonWindow, gwentPath):
        if filename == "":
            messagebox.showerror("No File Name", "No file name was specified.")
            return
        if not gwentPath or not gwentPath.endswith("GWENT The Witcher Card Game") or not gwentPath.endswith("Gwent"):
            messagebox.showerror("No Gwent Path", "Path to Gwent installation was invalid or not specified.")
            return
        cards = {}
        
        progressBar.config(maximum=30)

        progressBar.step(5)
        jsonWindow.update_idletasks()

        with zipfile.ZipFile(gwentPath + "/Gwent_Data/StreamingAssets/data_definitions", 'r') as cardDefinitions:
            cardDefinitions.extractall("data_definitions/")

        progressBar.step(5)
        jsonWindow.update_idletasks()

        gwentDataHelper = GwentUtils.GwentDataHelper("data_definitions/")
        card_templates = gwentDataHelper.card_templates
        progressBar.config(maximum=len(card_templates) + 30)

        for template_id in card_templates:
            template = card_templates[template_id]
            card = {}
            card_id = template.attrib['Id']
            card['ingameId'] = card_id
            card['strength'] = int(template.find('Power').text)
            tier = int(template.find('Tier').text)
            card['type'] = GwentUtils.TIERS.get(tier)
            card_type = int(template.find('Type').text)
            card['cardType'] = GwentUtils.TYPES.get(card_type)
            card['faction'] = GwentUtils.FACTIONS.get(int(template.find('FactionId').text))
            secondaryFaction = template.find('SecondaryFactionId')
            if secondaryFaction != None and int(secondaryFaction.text) in GwentUtils.FACTIONS:
                card['secondaryFaction'] = GwentUtils.FACTIONS.get(int(secondaryFaction.text))
            card['provision'] = int(template.find('Provision').text)
            
            #if (tier == LEADER):
                #card['provisionBoost'] = int(template.find('Provision').text)

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



            rarity = int(template.find('Rarity').text)
            card['rarity'] = GwentUtils.RARITIES.get(rarity)

            art_id = template.attrib.get('ArtId')
            if art_id != None:
                card['ingameArtId'] = art_id

            artist = gwentDataHelper.artists.get(art_id)
            if artist != None:
                card['artist'] = artist

            # Add all token cards to the 'related' list.
            tokens = gwentDataHelper.tokens.get(card_id)
            card['related'] = tokens

            armor = gwentDataHelper.armor.get(card_id)
            if armor != None and GwentUtils.TYPES.get(card_type) == "Unit":
                card['armor'] = int(armor)

            cards[card_id] = card
            progressBar.step(1)
            jsonWindow.update_idletasks()

        GwentUtils.save_json("card_data/" + filename, cards)
        if filename not in self.currentJSON['values']:
            self.currentJSON['values'] = (*self.currentJSON['values'], filename)
            self.numberofFiles += 1
        self.currentJSON.current(len(self.currentJSON['values']) - 1)
        GwentImageGenerator.loadNewJSON(self, "<<ComboboxSelected>>")
        jsonWindow.destroy()

    def run(self):
        self.mainwindow.mainloop()

if __name__ == '__main__':
    app = GwentImageGenerator()
    app.run()

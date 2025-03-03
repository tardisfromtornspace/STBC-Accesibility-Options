# THIS FILE IS NOT SUPPORTED BY ACTIVISION
# THIS FILE IS UNDER THE LGPL LICENSE AS WELL
# AccesibilityConfig.py
# 3rd March 2025, by USS Sovereign, and tweaked by Noat and Alex SL Gato (CharaToLoki)
#         Inspired by the Shield Percentages mod by Defiant. It was originally made pre-2010 with the goal of showing lots of accessibility options, such as for colorblind people.
#
# Modify, redistribute to your liking. Just remember to give credit where due.
#################################################################################################################
# 0.13 Update: if your install has the "scripts/FontExtension.py" script (which extends the TGFontManager class with functions which track and return font list and default font) called at the very beginning, now it will fetch Fonts automatically and will ignore manual additions. However, the script still supports 0.12 ("Legacy") manual additions, which the script will fall back to in case of Sovereign's file (or equivalent) not being present.
# This latter method consists on manually importing a font list from files located at the "extraConfigPath" indicated below. From there people can add fonts.
# But remember, before adding a new font to this script (or to all scripts, also applies for >= 0.13):
# 1. The font file must exist beforehand. For new fonts, a new proper file (like those font files at script/Icons) must have already been created first.
# 2. That font must have been registered to the App.g_kFontManager, in a not disimilar way to the line used on scripts/Icons/FontsAndIcons.py: "App.g_kFontManager.RegisterFont("Crillee", 5, "Crillee5", "LoadCrillee5")" (first parameter being the font name, second font size, third the actual file located at scripts/Icons/ and finally the function inside that file that actually takes care of loading the new font for that size).
# Below, we have a legacy example file used for listing the Default fonts that a regular BC Install has into our AccesibiltiyConfig script, on a file called DefaultFonts.py:
"""
# THIS FILE IS NOT SUPPORTED BY ACTIVISION
# THIS FILE IS UNDER THE LGPL LICENSE AS WELL
# DefaultFonts.py
# 1st March 2025, by Alex SL Gato (CharaToLoki)
# Version: 1.0
# Meant to be used alongside the AccesibilityConfig UMM option (located at scripts/Custom/UnifiedMainMenu/ConfigModules/Options/), this file must be under scripts/Custom/UnifiedMainMenu/ConfigModules/Options/AccesibilityConfigFiles
##################################
# This file takes care of listing the default Fonts and Sizes that a regular STBC install supports.
dFont = {
	"Crillee": [5, 6, 9, 12, 15],
	"LCARSText": [5, 6, 9, 12, 15],
	"Tahoma": [8, 14],
	"Arial": [8],
	"Serpentine": [12],
}
"""
# From version 0.2 onwards, we can also modify interface colors at a whim, but may require to abort a mission or to restart to apply fully - exception is menu colors, which may have been already pre-loaded before UMM had a chance to change them and may require a resolution change to apply on the Main Menu.
# As an addition, now we can also link certain pre-defined App.py interface colors (of those defined in scripts/LoadInterface) with additional files, so if, for example, FoundationTech happens to re-use one of those before we had overrode it and prevents us from changing the Hull Gauge colors, we can apply the new changes to those colors too.
# Below there's a file example of the above, on a file called DefaultExtraFileChecks.py
"""
# THIS FILE IS NOT SUPPORTED BY ACTIVISION
# THIS FILE IS UNDER THE LGPL LICENSE AS WELL
# DefaultExtraFileChecks.py
# 2nd March 2025, by Alex SL Gato (CharaToLoki)
# Version: 1.0
# Meant to be used alongside the AccesibilityConfig UMM option (located at scripts/Custom/UnifiedMainMenu/ConfigModules/Options/), this file must be under scripts/Custom/UnifiedMainMenu/ConfigModules/Options/AccesibilityConfigFiles
##################################
# This file takes care of listing the variable colors which are modified in other files and used instead of regular colors, like FoundationTech's Hull Gauge tech
extraVariables = {
	"g_kSubsystemFillColor" : {"kHullFillColor" : "FoundationTech"}, # Variable which is also defined somewhere - attribute name - path to that file 
	"g_kSubsystemEmptyColor" : {"kHullEmptyColor" : "FoundationTech"},
}
# If we were to add extra App. colors, we can also add the following, as long as those colors exist or are registered on App.py
#sDefaultColors = { # Colors from App.py
#	# We could add it to a pre-existing category, like STButton marker colors.
#	"STButton marker colors" : {
#		"variableNameGoesHere": [None, []],
#	},
#	# Or maybe a new one
#	"Extended extra configs" : {
#		"AnotherVariableNameGoesHere": [None, []],
#	},
#}
"""
#
MODINFO = { "Author": "\"USS Sovereign\" (mario0085), Noat (noatblok),\"Alex SL Gato\" (andromedavirgoa@gmail.com)",
	    "Version": "0.21",
	    "License": "LGPL",
	    "Description": "Read the small title above for more info"
	    }
#
#################################################################################################################
#

import App
import Foundation
import string
import nt
import traceback

LCARS = __import__(App.GraphicsModeInfo_GetCurrentMode().GetLcarsModule())

pModule = None
try:
	pModule = __import__("SavedConfigs.AccessibilityConfigVals")
except:
	pModule = None

configPath = "scripts\\Custom\\UnifiedMainMenu\\ConfigModules\\Options\\SavedConfigs\\AccessibilityConfigVals.py"
extraConfigPath = "scripts\\Custom\\UnifiedMainMenu\\ConfigModules\\Options\\AccesibilityConfigFiles"
extraVariables = {
	"g_kSubsystemFillColor" : {"kHullFillColor" : "FoundationTech"}, # Variable which is also defined somewhere - attribute name - path to that file 
	"g_kSubsystemEmptyColor" : {"kHullEmptyColor" : "FoundationTech"},
}

ET_SAVED_CONFIG = App.UtopiaModule_GetNextEventType() # You may wonder, ¿why? Because it is actually possible to play a mission and have access to the Customize configurations on the fly as long as the last Configure Window you opened was Customize
ET_SELECT_BUTTON = App.UtopiaModule_GetNextEventType()

pSaveButton = None
sSaveButton = "Save Config"
sSaveNotSaved = "Save Config: Unsaved changes. Save to apply."
canChangeSave = None
saveMsgDelay = 1 # in seconds
dConfig = {}

issues = 0 # To prevent another case like Galaxy Charts wrong configuration values breaking an entire install - yes, like KCS' case.

def ResetButtonString(pAction, pButton, myName):
	try:
		global pSaveButton
		if pSaveButton and myName != None:
			pSaveButton.SetName(App.TGString(myName))
		else:
			print "AccesibilityConfig.ResetButtonString: ERR.: missing button"
	except:
		pass

	return 0

def SafeConfigStatement(variable, pMyModule, default, issue=0, lowerLimit=None, upperLimit=None):
	myVariable = default
	try:
		if pMyModule != None and hasattr(pMyModule, variable):
			myVariable = getattr(pMyModule, variable)
		else:
			print configPath, " has no ", variable, " attribute. This will be addressed"
			myVariable = default
			issue = issue + 1
	except:
		traceback.print_exc()
		myVariable = default
		issue = issue + 1

	if lowerLimit != None and myVariable < lowerLimit:
		myVariable = lowerLimit
		issue = issue + 1
	elif upperLimit != None and myVariable > upperLimit:
		myVariable = upperLimit
		issue = issue + 1

	return myVariable, issue

dRadixNotation = [
	[",", "Comma (,)"],
	[".", "Lower point (.)"],
	["·", "Middle point (·)"], # TO-DO LOOK FOR ALTERNATIVE
	["'", "Apostrophe (')"], # Apparently "’" cannot be understood by the game
]
dFont = {
#	"Crillee": [5, 6, 9, 12, 15],
#	"LCARSText": [5, 6, 9, 12, 15],
#	"Tahoma": [8, 14],
#	"Arial": [8],
#	"Serpentine": [12],
}

sDefaultColors = { # Colors from App.py, called in LoadInterface.py... should we also look for App.globals ?
	# STButton marker colors.
	"STButton marker colors" : {
		"g_kSTButtonMarkerDefault": [None, []],
		"g_kSTButtonMarkerHighlighted": [None, []],
		"g_kSTButtonMarkerSelected": [None, []],
		"g_kSTButtonCheckmarkOn": [None, []],
		"g_kSTButtonCheckmarkOff": [None, []],
	},
	# Menu colors
	"Menu colors" : {
		"g_kSTMenuArrowColor": [None, []],

		"g_kSTMenu1NormalBase": [None, []],
		"g_kSTMenu1HighlightedBase": [None, []],
		"g_kSTMenu1Disabled": [None, []],
		"g_kSTMenu1OpenedHighlightedBase": [None, []],
		"g_kSTMenu1Selected": [None, []],

		"g_kSTMenu2NormalBase": [None, []],
		"g_kSTMenu2HighlightedBase": [None, []],
		"g_kSTMenu2Disabled": [None, []],
		"g_kSTMenu2OpenedHighlightedBase": [None, []],
		"g_kSTMenu2Selected": [None, []],

		"g_kSTMenu3NormalBase": [None, []],
		"g_kSTMenu3HighlightedBase": [None, []],
		"g_kSTMenu3Disabled": [None, []],
		"g_kSTMenu3OpenedHighlightedBase": [None, []],
		"g_kSTMenu3Selected": [None, []],

		"g_kSTMenu4NormalBase": [None, []],
		"g_kSTMenu4HighlightedBase": [None, []],
		"g_kSTMenu4Disabled": [None, []],
		"g_kSTMenu4OpenedHighlightedBase": [None, []],
		"g_kSTMenu4Selected": [None, []],

		"g_kSTMenuTextColor": [None, []],
		"g_kSTMenuTextSelectedColor": [None, []],
		"g_kSTMenuTextHighlightColor": [None, []],

		"g_kTextEntryColor": [None, []],
		"g_kTextHighlightColor": [None, []],

		"g_kTextEntryBackgroundColor": [None, []],
		"g_kTextEntryBackgroundHighlightColor": [None, []],
	},

	# Tactical Interface Colors
	"Tactical Interface Colors" : {
		"g_kTIPhotonReadyColor": [None, []],
		"g_kTIPhotonNotReadyColor": [None, []],
	},

	# Radar border highlight color
	"Radar border highlight color" : {
		"g_kSTRadarBorderHighlighted": [None, []],
	},

	# General Interface Colors
	"General Interface Colors" : {
		"g_kTitleColor": [None, []],
		"g_kInterfaceBorderColor": [None, []],
		"g_kLeftSeparatorColor": [None, []],
	},

	# Radar colors
	"Radar colors" : {
		"g_kRadarBorder": [None, []],
		"g_kSTRadarIncomingTorpColor": [None, []],
		"g_kRadarFriendlyColor": [None, []],
		"g_kRadarEnemyColor": [None, []],
		"g_kRadarNeutralColor": [None, []],
		"g_kRadarUnknownColor": [None, []],
	},

	# Subsystem colors, used in subsystem menus for fill gauge.
	"Subsystem colors" : {
		"g_kSubsystemFillColor": [None, []],
		"g_kSubsystemEmptyColor": [None, []],
		"g_kSubsystemDisabledColor": [None, []],
	},

	# Color used for header text in the tactical weapons control.
	"Tactical weapons control header text" : {
		"g_kTacWeaponsCtrlHeaderTextColor": [None, []],
	},

	# Damage display colors.
	"Damage display colors" : {
		"g_kDamageDisplayDestroyedColor": [None, []],
		"g_kDamageDisplayDamagedColor": [None, []],
		"g_kDamageDisplayDisabledColor": [None, []],
	},

	# Main menu colors, which are used elsewhere.
	"Main menu colors" : {
		"g_kMainMenuButtonColor": [None, []],
		"g_kMainMenuButtonHighlightedColor": [None, []],
		"g_kMainMenuButtonSelectedColor": [None, []],

		"g_kMainMenuButton1Color": [None, []],
		"g_kMainMenuButton1HighlightedColor": [None, []],
		"g_kMainMenuButton1SelectedColor": [None, []],

		"g_kMainMenuButton2Color": [None, []],
		"g_kMainMenuButton2HighlightedColor": [None, []],
		"g_kMainMenuButton2SelectedColor": [None, []],

		"g_kMainMenuButton3Color": [None, []],
		"g_kMainMenuButton3HighlightedColor": [None, []],
		"g_kMainMenuButton3SelectedColor": [None, []],


		"g_kMainMenuBorderMainColor": [None, []],
		"g_kMainMenuBorderOffColor": [None, []],
		"g_kMainMenuBorderBlock1Color": [None, []],
		"g_kMainMenuBorderTopColor": [None, []],

	},


	# Engineering display colors.
	"Engineering display colors" : {
		"g_kEngineeringShieldsColor": [None, []],
		"g_kEngineeringEnginesColor": [None, []],
		"g_kEngineeringWeaponsColor": [None, []],
		"g_kEngineeringSensorsColor": [None, []],
		"g_kEngineeringCloakColor": [None, []],
		"g_kEngineeringTractorColor": [None, []],

		"g_kEngineeringWarpCoreColor": [None, []],
		"g_kEngineeringMainPowerColor": [None, []],
		"g_kEngineeringBackupPowerColor": [None, []],

		"g_kEngineeringCtrlBkgndLineColor": [None, []],

	},

	# QuickBattle and Multiplayer Colors
	"QuickBattle and Multiplayer Colors" : {
		"g_kQuickBattleBrightRed": [None, []],
		"g_kMultiplayerBorderBlue": [None, []],
		"g_kMultiplayerBorderPurple": [None, []],
		"g_kMultiplayerStylizedPurple": [None, []],
		"g_kMultiplayerButtonPurple": [None, []],
		"g_kMultiplayerButtonOrange": [None, []],

		"g_kMultiplayerRadioPink": [None, []],
		"g_kMultiplayerDividerPurple": [None, []],
	},
}

_g_dExcludeSomePlugins = {
	# Some random plugins that I don't want to risk people attempting to load using this tech
	"__init__": 1,
}

# The original method was huge and could be simplified
def FuseTwoLists(l1, l2):
	
	def gen_dict(*args):
		d = {}
		for k in args:
			if type(k) == type([]):
				for item in k:
					if type(item) == type(1):
						d[item] = item
			elif type(k) == type(1):
				d[item] = item

		return d.keys()
	result = list(gen_dict(l1, l2))
	result.sort()
	return result
"""
def FuseTwoLists(auxA, auxB):
	aux1 = auxA
	if len(aux1) > 1:
		aux1.sort()
	aux2 = []
	if type(auxB) == type ([]):
		for item in auxB:
			if type(item) == type(1):
				aux2.append(item)
		aux2.sort()
	elif type(auxB) == type (1):
		aux2.append(auxB)
	if len(aux2) > 0:
		i = 0
		j = 0
		aux3 = []
		while (i < len(aux1) and j < len(aux2)):
			if aux1[i] < aux2[j]:
				aux3.append(aux1[i])
				i = i + 1
			elif aux1[i] == aux2[j]:
				aux3.append(aux1[i])
				i = i + 1
				j = j + 1
			else:
				aux3.append(aux2[j])
				j = j + 1
		while (i < len(aux1)):
			aux3.append(aux1[i])
			i = i + 1
		while (j < len(aux2)):
			aux3.append(aux2[j])
			j = j + 1
		return aux3
	else:
		return []

"""
# Based on LoadExtraPlugins by Dasher42 and MLeo's, but heavily modified so it only imports a few things
def LoadExtraLimitedPlugins(dir,dExcludePlugins=_g_dExcludeSomePlugins, ignore=[]):
	global dConfig, dRadixNotation, dFont, extraVariables, sDefaultColors
	if dir == None or dir == "":
		print "no dir found, calling default"
		dir="scripts\\Custom\\UnifiedMainMenu\\ConfigModules\\Options\\AccesibilityConfigFiles" # I want to limit any vulnerability as much as I can while keeping functionality
	try:
		list = nt.listdir(dir)
		if not list:
			print "ERROR: Missing scripts/Custom/TravellingMethods folder for AlternateSubModelFTL technology"
			return
	except:
		print "ERROR: Missing scripts/Custom/TravellingMethods folder for AlternateSubModelFTL technology, or other error:"
		traceback.print_exc()
		return		

	list.sort()

	dotPrefix = string.join(string.split(dir, "\\")[1:], ".") + "."

	filesChecked = {} 
	for plugin in list:
		s = string.split(plugin, ".")
		if len(s) <= 1:
			continue
	
		# Indexing by -1 lets us be sure we're grabbing the extension. -Dasher42
		extension = s[-1]
		fileName = string.join(s[:-1], ".")

		# We don't want to accidentally load wrong things
		if (extension == "py") and not fileName == "__init__": # I am not allowing people to just use the .pyc directly, I don't want people to not include source scripts - Alex SL Gato
			#print "AlternateSubModelFTL  script is reviewing " + fileName + " of dir " + dir
			if dExcludePlugins.has_key(fileName):
				debug(__name__ + ": Ignoring plugin" + fileName)
				continue

			try:
				if not filesChecked.has_key(fileName):
					filesChecked[fileName] = 1
					myGoodPlugin = dotPrefix + fileName

					try:
						banana = __import__(myGoodPlugin)
					except:
						banana = None
						traceback.print_exc()

					if hasattr(banana, "dFont") and not "dFont" in ignore:
						for key in banana.dFont.keys():
							if not dFont.has_key(key):
								dFont[key] = []
							aux = FuseTwoLists(dFont[key], banana.dFont[key])
							if len(aux) > 0:
								dFont[key] = FuseTwoLists(dFont[key], banana.dFont[key])

					if hasattr(banana, "extraVariables") and not "extraVariables" in ignore:
						for colorName in banana.extraVariables.keys():
							if type(banana.extraVariables[colorName]) == type({}):
								for attribToOvr in banana.extraVariables[colorName].keys():
									djarin = banana.extraVariables[colorName][attribToOvr]
									if djarin != None and type(djarin) != type([]) and type(djarin) != type({}):
										if not extraVariables.has_key(colorName):
											extraVariables[colorName] = {}
										extraVariables[colorName][attribToOvr] = djarin

					if hasattr(banana, "sDefaultColors") and not "sDefaultColors" in ignore:
						for category in banana.sDefaultColors.keys():
							if type(banana.sDefaultColors[category]) == type({}):
								for colorName in banana.sDefaultColors[category].keys():
									if type(colorName) == type(""):
										if not sDefaultColors.has_key(category):
											sDefaultColors[category] = {}
										sDefaultColors[category][colorName] = []
									

						for colorName in banana.extraVariables.keys():
							if type(banana.extraVariables[colorName]) == type({}):
								for attribToOvr in banana.extraVariables[colorName].keys():
									djarin = banana.extraVariables[colorName][attribToOvr]
									if djarin != None and type(djarin) != type([]) and type(djarin) != type({}):
										if not extraVariables.has_key(colorName):
											extraVariables[colorName] = {}
										extraVariables[colorName][attribToOvr] = djarin

			except:
				print "someone attempted to add more than they should to the AlternateSubModelFTL script"
				traceback.print_exc()

defaultFont = "Crillee"
defaultSize = 5

isTGFontManagerEPresent = hasattr(App.g_kFontManager, "GetFontList") and hasattr(App.g_kFontManager, "GetDefaultFontInfo")
isBCMM = 0

if isTGFontManagerEPresent: # Support for Mario's FontManager extension
	try:
		import bcmm_version
		isBCMM = 1
	except:
		print("No BCMM signature file")
		isBCMM = 0
	# Ok so, we already know if it's BCMM or not. Now, it may be possible someone backported something from BCMM or made changes similar to BCMM for the same functions
	fonts = App.g_kFontManager.GetFontList()
	if not fonts or type(fonts) != type([]) or len(fonts) < 1:
		if isBCMM:
			print "AccesibilityConfig: ERROR: No Fonts detected using BCMM's FontManager extension. Attempting Legacy extra menu support..."
		else:
			print "AccesibilityConfig: ATTENTION: No Fonts detected using a FontManager's extension. Defaulting to Legacy extra menu support..."

		LoadExtraLimitedPlugins(extraConfigPath)
	else:
		errorFree = 0
		strikes = 0
		try:

			fontA = App.g_kFontManager.GetDefaultFontInfo()
			if fontA != None:

				defaultFontA = None
				defaultSizeA = None
				try:
					if hasattr(fontA, name) and type(fontA.name) == type(""):
						defaultFontA = str(fontA.name)
					if hasattr(fontA, size) and type(fontA.size) == type(1):
						defaultSizeA = int(fontA.size)
					errorFree = 1
				except:
					errorFree = 0
					traceback.print_exc()

				if errorFree == 1:
					defaultFont = defaultFontA
					defaultSize = defaultSizeA
				else:
					strikes = strikes + 1

			for fontI in fonts:
				l = []
				if not hasattr(fontI, name) or type(fontI.name) != type("") or not hasattr(fontA, size) or type(fontA.size) != type(1):
					strikes = strikes + 1
					break
				if dFont.has_key(fontI.name):
					l = dFont[fontI.name]
				else:
					dFont[fontI.name] = l
				l.append(fontI.size)

		except:
			strikes = 1
			traceback.print_exc()

		if isBCMM:
			if strikes == 0:
				print "AccesibilityConfig: Using BCMM's FontManager Extension"
				LoadExtraLimitedPlugins(extraConfigPath, ignore=["dFont"])
			else:
				print "AccesibilityConfig: An error ocurred while using BCMM's FontManager Extension. Attempting Legacy extra menu support..."
				LoadExtraLimitedPlugins(extraConfigPath)
		else:
			if strikes == 0:
				print "AccesibilityConfig: Using a FontManager Extension"
				LoadExtraLimitedPlugins(extraConfigPath, ignore=["dFont"])
			else:
				print "AccesibilityConfig: A FontManager Extension seems to be present, but is not compatible with this mod. Defaulting to Legacy extra menu support..."
				LoadExtraLimitedPlugins(extraConfigPath)
else:
	print "AccesibilityConfig: Using Legacy extra menu support"
	LoadExtraLimitedPlugins(extraConfigPath)

listedFonts = list(dFont.keys())
listedFonts.sort()

if dFont == None or len(dFont) <= 0:
	if isTGFontManagerEPresent:
		print "ERROR: No Fonts detected for AccesibilityConfig. This likely means that somehow, the game lacks important files at scripts/Icons, or that important Files that register fonts for the game are missing or modified to such a extent that no fonts are registered. Please read more at ", __name__, " for more information."
	else:
		print "WARNING: No Fonts detected for AccesibilityConfig. If using Legacy menu support, please make sure that a file on ", extraConfigPath, "exists with the example content located between the 3 '\"' seen at ", __name__
	
else:
	if not defaultFont in dFont.keys():
		defaultFont = listedFonts[0]
	if not defaultSize in dFont[defaultFont]:
		defaultSize = dFont[defaultFont][0]


dConfig["ShowPercent"], issues = SafeConfigStatement("ShowPercent", pModule, 0, issues, 0, 1)
dConfig["ShowBar"], issues = SafeConfigStatement("ShowBar", pModule, 1, issues, 0, 1)
dConfig["ShowFraction"], issues = SafeConfigStatement("ShowFraction", pModule, 0, issues, 0, 1)

dConfig["NumberDecimals"], issues = SafeConfigStatement("NumberDecimals", pModule, 0, issues, 0)
dConfig["RadixNotation"], issues = SafeConfigStatement("RadixNotation", pModule, ".", issues)

dConfig["sFont"], issues = SafeConfigStatement("sFont", pModule, defaultFont, issues)
dConfig["FontSize"], issues = SafeConfigStatement("FontSize", pModule, defaultSize, issues, 0)

pFontSubMenu = None
sBaseFMenu = "Font Selection: "
sSeparator = ", size "

def SetupColor(kColor, colorName, fRed, fGreen, fBlue, fAlpha):
	kColor.r = fRed
	kColor.g = fGreen
	kColor.b = fBlue
	kColor.a = fAlpha
	return kColor

def GetAppColorFromName(name):
	kColor = None
	kColorInfo = []
	if hasattr(App, name):
		kColor = getattr(App, name)
		if kColor != None:
			kColorInfo = GetColors(kColor)
	return [kColor, kColorInfo]

def SetAppColorFromName(name):
	kColor = None
	kColorInfo = []
	if hasattr(App, name):
		kColor = getattr(App, name)
		if kColor != None:
			kColor = SetupColor(kColor, name, fRed, fGreen, fBlue, fAlpha)
			kColorInfo = GetColors(kColor)
	return [kColor, kColorInfo]

def GetColors(kColor):
	return [kColor.r, kColor.g, kColor.b, kColor.a]

dConfig["Colors"] = {}
dConfig["ColorsList"] = {}
colorsExtraCon = extraVariables.keys()

def ExtrasColorSafety(colorsExtraCons=colorsExtraCon):
		if colorName in colorsExtraCons:
			try:
				for attribToOvr in extraVariables[colorName].keys():
					try:
						pathToImport = extraVariables[colorName][attribToOvr]
						pear = __import__(pathToImport)
						if pear:
							if hasattr(pear, attribToOvr):
								leAttrib = getattr(pear, attribToOvr)
								if leAttrib != None:
									SetupColor(leAttrib, colorName, dConfig[colorName + "R COLOR"], dConfig[colorName + "G COLOR"], dConfig[colorName + "B COLOR"], dConfig[colorName + "A COLOR"])
					except:
						print "AccesibilityConfig: Error while saving an extra considered color config:"
						traceback.print_exc()
				
			except:
				print "AccesibilityConfig: Error while saving an extra considered color config:"
				traceback.print_exc()

for typeC in sDefaultColors.keys():
	for colorName in sDefaultColors[typeC].keys():
		sDefaultColors[typeC][colorName] = GetAppColorFromName(colorName)

for typeC in sDefaultColors.keys():
	for colorName in sDefaultColors[typeC].keys():
		if sDefaultColors[typeC][colorName] != None and type(sDefaultColors[typeC][colorName]) == type([]) and len(sDefaultColors[typeC][colorName]) >= 2 and sDefaultColors[typeC][colorName][0] != None and type(sDefaultColors[typeC][colorName][1]) == type ([]) and len(sDefaultColors[typeC][colorName][1]) >= 4:
			if not dConfig["ColorsList"].has_key(typeC):
				dConfig["ColorsList"][typeC] = {}
			dConfig["ColorsList"][typeC][colorName] = 1
	
			dConfig["Colors"][colorName] = [sDefaultColors[typeC][colorName][1], sDefaultColors[typeC][colorName][0]]

			dConfig[colorName + "R COLOR"], issues = SafeConfigStatement(colorName + "R", pModule, dConfig["Colors"][colorName][0][0], issues, 0, 1)
			dConfig[colorName + "G COLOR"], issues = SafeConfigStatement(colorName + "G", pModule, dConfig["Colors"][colorName][0][1], issues, 0, 1)
			dConfig[colorName + "B COLOR"], issues = SafeConfigStatement(colorName + "B", pModule, dConfig["Colors"][colorName][0][2], issues, 0, 1)
			dConfig[colorName + "A COLOR"], issues = SafeConfigStatement(colorName + "A", pModule, dConfig["Colors"][colorName][0][3], issues, 0, 1)

			SetupColor(dConfig["Colors"][colorName][1], colorName, dConfig[colorName + "R COLOR"], dConfig[colorName + "G COLOR"], dConfig[colorName + "B COLOR"], dConfig[colorName + "A COLOR"])
			ExtrasColorSafety()

def SaveConfig(pObject, pEvent):
	file = nt.open(configPath, nt.O_WRONLY | nt.O_TRUNC | nt.O_CREAT | nt.O_BINARY)
	nt.write(file, "ShowPercent = " + str(dConfig["ShowPercent"]))
	nt.write(file, "\nShowBar = " + str(dConfig["ShowBar"]))
	nt.write(file, "\nShowFraction = " + str(dConfig["ShowFraction"]))
	nt.write(file, "\nNumberDecimals = " + str(dConfig["NumberDecimals"]))
	nt.write(file, "\nRadixNotation = \"" + str(dConfig["RadixNotation"])+ "\"")
	nt.write(file, "\nsFont = \"" + str(dConfig["sFont"]) + "\"")
	nt.write(file, "\nFontSize = " + str(dConfig["FontSize"]))

	global colorsExtraCon
	colorsExtraCon = extraVariables.keys()
	for colorName in dConfig["Colors"].keys():
		nt.write(file, "\n" + str(colorName) + "R = " + str(dConfig[colorName + "R COLOR"]))
		nt.write(file, "\n" + str(colorName) + "G = " + str(dConfig[colorName + "G COLOR"]))
		nt.write(file, "\n" + str(colorName) + "B = " + str(dConfig[colorName + "B COLOR"]))
		nt.write(file, "\n" + str(colorName) + "A = " + str(dConfig[colorName + "A COLOR"]))

		SetupColor(dConfig["Colors"][colorName][1], colorName, dConfig[colorName + "R COLOR"], dConfig[colorName + "G COLOR"], dConfig[colorName + "B COLOR"], dConfig[colorName + "A COLOR"])

		#Extra support for rare cases where somebody already did something with the colors first - i.e. FoundationTech:	
 		ExtrasColorSafety(colorsExtraCon)


	nt.close(file)

	# Because of shenanigans with menu being available during QB on KM, you can sometimes access modify and save configurations mid-game. We may want to notify other related scripts that this has happened!
	pEvent = App.TGStringEvent_Create()
	pEvent.SetEventType(ET_SAVED_CONFIG)
	#pEvent.SetDestination(None)
	pEvent.SetString("SAVED BC ACCESIBILITY")
	App.g_kEventManager.AddEvent(pEvent)

	print "Calling resolution change event..."
	# TO-DO EXPERIMENTAL
	pEvent1 = App.TGStringEvent_Create()
	pEvent1.SetEventType(App.ET_GRAPHICS_RESOLUTION_REVERT)
	#pEvent1.SetDestination(None)
	pEvent1.SetString("BC ACCESIBILITY")
	App.g_kEventManager.AddEvent(pEvent1)

	# Just some niceties for people
	global pSaveButton, canChangeSave
	currentTime = App.g_kUtopiaModule.GetGameTime()
	if pSaveButton and (canChangeSave == None or currentTime > canChangeSave):
		canChangeSave = currentTime + saveMsgDelay + 0.1
		pSaveButton.SetName(App.TGString("CONFIGURATION SAVED"))
		pSequence = App.TGSequence_Create()
		pAction = App.TGScriptAction_Create(__name__, "ResetButtonString", pSaveButton, sSaveButton)
		pSequence.AddAction(pAction, None, saveMsgDelay)
		pSequence.Play()

if issues > 0:
	print "Re-applying a safe save Accesibility Config"
	try:
		SaveConfig(None, None)
	except:
		traceback.print_exc()

def GetName():
	return "BC Accessibility"


# Builds our menu.  Remember to add the "return App.TGPane_Create(0,0)" command!
def CreateMenu(pOptionsPane, pContentPanel, bGameEnded = 0):
	global pFontSubMenu

	CreateButton("Show Health Bar", pContentPanel, pOptionsPane, pContentPanel, __name__ + ".BarToggle", isChosen=dConfig["ShowBar"], isToggle=1)
	CreateButton("Show Health Percent", pContentPanel, pOptionsPane, pContentPanel, __name__ + ".PercentToggle", isChosen=dConfig["ShowPercent"], isToggle=1)
	CreateButton("Show Health Fraction", pContentPanel, pOptionsPane, pContentPanel, __name__ + ".FractionToggle", isChosen=dConfig["ShowFraction"], isToggle=1)

	CreateTextEntryButton("Number of decimals: ", pContentPanel, pOptionsPane, pContentPanel, "NumberDecimals", __name__ + ".HandleKeyboardGoBetween")
	CreateMultipleChoiceButton("Radix Notation: ", pContentPanel, pOptionsPane, pContentPanel, __name__ + ".SelectNext", "RadixNotation", dRadixNotation, EventInt = 0)

	pFontSubMenu = CreateFontMenu(sBaseFMenu + str(dConfig["sFont"]) + str(sSeparator)+str(dConfig["FontSize"]) , pContentPanel, pOptionsPane, pContentPanel)
	CreateColorsMenu("Interface colors", pContentPanel, pOptionsPane, pContentPanel)

	global pSaveButton
	pSaveButton = CreateButton(sSaveButton, pContentPanel, pOptionsPane, pContentPanel, __name__ + ".SaveConfig")
	return App.TGPane_Create(0,0)

def BarToggle(object, event):
	#global ShowBar
	global dConfig
	dConfig["ShowBar"] = not dConfig["ShowBar"]
	App.STButton_Cast(event.GetSource()).SetChosen(dConfig["ShowBar"]) # Found method to get the button from BridgePlugin.py

	global pSaveButton
	if pSaveButton:
		ResetButtonString(None, pSaveButton, sSaveNotSaved)


def PercentToggle(object, event):
	#global ShowPercent
	global dConfig
	dConfig["ShowPercent"] = not dConfig["ShowPercent"]
	App.STButton_Cast(event.GetSource()).SetChosen(dConfig["ShowPercent"])

	global pSaveButton
	if pSaveButton:
		ResetButtonString(None, pSaveButton, sSaveNotSaved)

def FractionToggle(object, event):
	#global ShowFraction
	global dConfig
	dConfig["ShowFraction"] = not dConfig["ShowFraction"]
	App.STButton_Cast(event.GetSource()).SetChosen(dConfig["ShowFraction"])

	global pSaveButton
	if pSaveButton:
		ResetButtonString(None, pSaveButton, sSaveNotSaved)

def HandleKeyboardGoBetween(pObject, pEvent):
	# Maybe do a cast of the pParent's parent? App.STMenu_Create(sMenuName)
	pPara = App.TGParagraph_Cast(pEvent.GetDestination())
	pParent = App.TGPane_Cast(pPara.GetParent())

	pSubPara = App.TGParagraph_Cast(pParent.GetNthChild(2))
	pString = App.TGString()
	pSubPara.GetString(pString)
	pNewVal = App.TGString()
	pPara.GetString(pNewVal)
	sNewVal = pNewVal.GetCString()
	if string.count(sNewVal, ".") > 1:
		lList = string.split(sNewVal, ".")
		sNewVal = lList[0] + "." + string.join(lList[1:-1], "")
		pPara.SetString(sNewVal)

	if pNewVal.GetCString() != None and pNewVal.GetCString() != "":
		myParam = pString.GetCString()
		myReso = 0
		if len(myParam) > 7:
			fidgement = myParam[-7:]
			if fidgement == "R COLOR" or fidgement == "G COLOR" or fidgement == "B COLOR" or fidgement == "A COLOR":
				myReso = 1
				
		if myReso == 0:	
			dConfig[pString.GetCString()] = int(pNewVal.GetCString())
			if pString.GetCString() == "sFont" or pString.GetCString() == "FontSize":
				UpdateFontSubMenu(0)
		else: # It is a color thing
			newColor = float(pNewVal.GetCString())
			if newColor >= 1.0:
				newColor = 1.0
			dConfig[pString.GetCString()] = newColor

			mainInfo = pString.GetCString()[:-7]

			pGrandparent = App.STMenu_Cast(pParent.GetConceptualParent()) #App.TGPane_Cast(pParent.GetParent())
			newContent = ColorMessageFormat(str(mainInfo), dConfig[str(mainInfo + "R COLOR")], dConfig[str(mainInfo + "G COLOR")], dConfig[str(mainInfo + "B COLOR")], dConfig[str(mainInfo + "A COLOR")])
			
			UpdateSubMenu(0, pGrandparent, newContent)
			
		global pSaveButton
		if pSaveButton:
			ResetButtonString(None, pSaveButton, sSaveNotSaved)

	pObject.CallNextHandler(pEvent)

def ColorMessageFormat(colorName, r, g, b, a):

	r255 = 255 * r
	g255 = 255 * g
	b255 = 255 * b

	myDecimalR = ""
	myDecimalG = ""
	myDecimalB = ""
	if dConfig["NumberDecimals"] > 0:
		rN = dConfig["RadixNotation"]
		myDecimalR = myDecimalR + rN + str(r255%1.0)[2:(1+dConfig["NumberDecimals"])]
		myDecimalG = myDecimalG + rN + str(g255%1.0)[2:(1+dConfig["NumberDecimals"])]
		myDecimalB = myDecimalB + rN + str(b255%1.0)[2:(1+dConfig["NumberDecimals"])]

	newContent = str(colorName) + ": (" + str(int(r255)) + myDecimalR + "; " + str(int(g255)) + myDecimalG + "; " + str(int(b255)) + myDecimalB + "; " + str(a) + ")"
	return newContent

def CreateTextEntryButton(sButtonName, pMenu, pOptionPane, pContentPanel, sVar, sFunction, isChosen = 0, isToggle = 0, EventInt = 0, ET_EVENT = None):
	pTextField  = CreateTextField(App.TGString(sButtonName), sVar, sFunction)
	pMenu.AddChild(pTextField)

# From Custom\UnifiedMainMenu\ConfigModules\Options\Graphics\NanoFX by MLeoDaalder
def CreateTextField(pName, sVar, sFunction):
	pGraphicsMode = App.GraphicsModeInfo_GetCurrentMode()
	LCARS = __import__(pGraphicsMode.GetLcarsModule())
	fMaxWidth = LCARS.MAIN_MENU_CONFIGURE_CONTENT_WIDTH - 0.02
	pPane = App.TGPane_Create (fMaxWidth, 1.0)

	# Create the text tag
	pText = App.TGParagraph_CreateW(pName)
	fWidth = pText.GetWidth ()+0.01
	pTText = App.STButton_CreateW(pName, None)
	del pText

	pPane.AddChild(pTText,0,0)
	pTText.SetUseEndCaps(0)
	pTText.SetJustification(App.STButton.LEFT)
	pTText.SetDisabled(1)
	pTText.SetDisabledColor(App.g_kMainMenuBorderMainColor)
	pTText.SetColorBasedOnFlags()
	pTText.SetVisible()

	pcLCARS = pGraphicsMode.GetLcarsString()

	pTextEntry = App.TGParagraph_Create (str(dConfig[sVar]))
	pTextEntry.SetIgnoreString("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ*?\t\\/,<>\"|:;\'\n-+()&^%$#@!`~\n\r")

	pTextEntry.Resize (fMaxWidth - fWidth, pTextEntry.GetHeight (), 0)
	pTextEntry.SetReadOnly(0)
	pTextEntry.SetColor(App.NiColorA(0,0,0,1))

	pTextEntry.AddPythonFuncHandlerForInstance(App.ET_KEYBOARD, __name__ + ".HandleKeyboardGoBetween")

	pSubEntry = App.TGParagraph_Create(str(sVar))
	pSubEntry.SetNotVisible(1)

	pPane.AddChild (pTextEntry, fWidth + 0.02, 0.002)
	pPane.AddChild(pSubEntry)

	pPane.Resize (fMaxWidth, pTText.GetHeight(), 0)

	return pPane



def SelectNext(pObject, pEvent, variable=None, sButtonName=None):
	if pEvent and hasattr(pEvent, "GetCString"):
		variable = pEvent.GetCString()
		if variable != None and dConfig[variable] != None:
			#print "Called SelectNext for variable ", variable
			global dConfig
			pButton = pEvent.GetSource()
			if not pButton:
				pObject.CallNextHandler(pEvent)
				return

			pButton = App.STButton_Cast(pButton)
			if not pButton or not hasattr(pButton, "GetName"):
				pObject.CallNextHandler(pEvent)
				return

			error = 0
			try:
				if pButton.GetObjID() == App.NULL_ID:
					error = 1
			except:
				error = 1

			if error != 0:
				pObject.CallNextHandler(pEvent)
				return
			
			sButtonName = dConfig[str(variable) + str(" Menu Name")]
			if sButtonName != None:
				lOptions = dConfig[str(variable) + str(" Menu Options")]
				if lOptions != None:
					if type(lOptions) == type([]) and len(lOptions) > 0:
						pNext = 0
						iCounter = 0
						found = 0
						value = "ERROR"
						defaultValue = None
						defaultName = "ERROR"
						for s in lOptions:
							iCounter = iCounter + 1
							if type(s) == type([]):
								if len(s) >= 2:
									if defaultValue == None:
										defaultValue = str(s[0])
										defaultName = str(s[1])
									if dConfig[variable] == str(s[0]):
										found = 1
										break
								elif len(s) == 1:
									if defaultValue == None:
										defaultValue = str(s[0])
										defaultName = str(s[0])
									if dConfig[variable] == str(s[0]):
										found = 1
										break

							elif type(s) == type({}):
								for k in s.keys():
									if defaultValue == None:
										defaultValue = str(k)
										defaultName = str(s[k])
									if dConfig[variable] == str(k):
										found = 1
										break
								if found:
									break

							elif type(s) == type("") or type(s) == type(1) or type(s) == type(1.2):
								if defaultValue == None:
									defaultValue = str(s)
									defaultName = str(s)
								if dConfig[variable] == str(s):
									found = 1
									break


						iCounter = iCounter%len(lOptions)
						changedSetting = 0
						if not found or iCounter == 0:
							dConfig[str(variable)] = defaultValue
							pButton.SetName(App.TGString(sButtonName + str(defaultName)))
							changedSetting = 1
						else:
							pNext = lOptions[iCounter]
							if type(pNext) == type([]):
								if len(pNext) >= 2:
									dConfig[str(variable)] = str(pNext[0])
									pButton.SetName(App.TGString(sButtonName + str(pNext[1])))
									changedSetting = 1
								elif len(pNext) == 1:
									dConfig[str(variable)] = str(pNext[0])
									pButton.SetName(App.TGString(sButtonName + str(pNext[0])))
									changedSetting = 1

							elif type(pNext) == type({}):
								for k in pNext.keys():
									dConfig[str(variable)] = str(k)
									pButton.SetName(App.TGString(sButtonName + str(pNext[k])))
									changedSetting = 1
									break

							elif type(pNext) == type("") or type(pNext) == type(1) or type(pNext) == type(1.2):
								dConfig[str(variable)] = str(pNext)
								pButton.SetName(App.TGString(sButtonName + str(pNext)))
								changedSetting = 1

						if changedSetting:
							global pSaveButton
							if pSaveButton:
								ResetButtonString(None, pSaveButton, sSaveNotSaved)
                
	pObject.CallNextHandler(pEvent)

def CreateMultipleChoiceButton(sButtonName, pMenu, pOptionsPane, pContentPanel, sFunction, variable, lOptions, isChosen= 0, isToggle = 0, EventInt = 0, ET_EVENT = None):

	global dConfig
	pButton = None
	if variable != None:
		pButton = CreateButton(str(variable), pContentPanel, pOptionsPane, pContentPanel, sFunction, isChosen, isToggle, EventInt, ET_EVENT)
	
		if dConfig[variable] != None:
			dConfig[str(variable) + str(" Menu Name")] = sButtonName

			lOptionsProperContructed = []
			if type(lOptions) == type([]):
				for s in lOptions:
					if s != None and (type(s) == type([]) or type(s) == type([]) or type(s) == type("") or type(s) == type(1) or type(s) == type(1.2)):
						lOptionsProperContructed.append(s)
			elif type(lOptions) == type({}):
				for s in lOptions.keys():
					leType = lOptions[s]
					if leType != None and (type(leType) == type([]) or type(leType) == type([]) or type(leType) == type("") or type(leType) == type(1) or type(leType) == type(1.2)):
						lOptionsProperContructed.append(leType)
			else:
				if type(lOptions) == type("") or type(lOptions) == type(1) or type(lOptions) == type(1.2):
					lOptionsProperContructed.append(lOptions)

			dConfig[str(variable) + str(" Menu Options")] = lOptionsProperContructed
			found = 0
			for s in lOptionsProperContructed:
				if s != None:
					if type(s) == type([]):
						if len(s) >= 2:
							if dConfig[variable] == str(s[0]):
								found = 1
								pButton.SetName(App.TGString(sButtonName + str(s[1])))
								break
						elif len(s) == 1:
							if dConfig[variable] == str(s[0]):
								found = 1
								pButton.SetName(App.TGString(sButtonName + str(s[0])))
								break

					elif type(s) == type({}):
						for k in s.keys():
							if dConfig[variable] == str(k):
								found = 1
								pButton.SetName(App.TGString(sButtonName + str(s[k])))
								break
						if found:
							break

					elif type(s) == type("") or type(s) == type(1) or type(s) == type(1.2):
						if dConfig[variable] == str(s):
							found = 1
							pButton.SetName(App.TGString(sButtonName + str(s)))
							break
						
			if found == 0:
				print "ATTENTION: The current configuration is not found on the default select names. It is possible the configuration for ", variable, " has been manually edited for a custom value."
				pButton.SetName(App.TGString(sButtonName + "CUSTOM: " + str(s)))
		else:
			pButton.SetName(App.TGString(sButtonName + " ERROR: No variable " + str(variable) + " found."))
			print "ERROR on ", __name__, ".CreateMultipleChoiceButton: the specified variable for one of our calls is not found on our configuration."
	else:
		print "ERROR on ", __name__, ".CreateMultipleChoiceButton: the specified variable for one of our calls is None."

	return pButton

		


def CreateButton(sButtonName, pMenu, pOptionPane, pContentPanel, sFunction, isChosen = 0, isToggle = 0, EventInt = 0, ET_EVENT = None, myString=None):
	if ET_EVENT == None:		
		ET_EVENT = App.UtopiaModule_GetNextEventType()

	pOptionPane.AddPythonFuncHandlerForInstance(ET_EVENT, sFunction)

	pEvent = App.TGStringEvent_Create()
	pEvent.SetEventType(ET_EVENT)
	pEvent.SetDestination(pOptionPane)
	if myString == None:
		myString = sButtonName
	pEvent.SetString(myString)

	pButton = App.STButton_Create(sButtonName, pEvent)
	pButton.SetChoosable(isToggle)
	pButton.SetChosen(isChosen)

	pEvent.SetSource(pButton)
	pMenu.AddChild(pButton)

	return pButton

def ResetDefaultColors(pObject, pEvent):
	pObject.CallNextHandler(pEvent)
	colorName = pEvent.GetCString()

	if colorName != None and colorName != "" and len(colorName) >= 2:
		global dConfig
		dConfig[colorName + "R COLOR"] = dConfig["Colors"][colorName][0][0]
		dConfig[colorName + "G COLOR"] = dConfig["Colors"][colorName][0][1]
		dConfig[colorName + "B COLOR"] = dConfig["Colors"][colorName][0][2]
		dConfig[colorName + "A COLOR"] = dConfig["Colors"][colorName][0][3]

		pParent = App.STMenu_Cast(pEvent.GetDestination())

		newContent = ColorMessageFormat(str(colorName), dConfig[str(colorName + "R COLOR")], dConfig[str(colorName + "G COLOR")], dConfig[str(colorName + "B COLOR")], dConfig[str(colorName + "A COLOR")])

		UpdateSubMenu(1, pParent, newContent)

def CreateColorsMenu(sMenuName, pMenu, pOptionsPane, pContentPanel):
	pSubMenu = App.STMenu_Create(sMenuName)
	#pSubMenu.AddPythonFuncHandlerForInstance(ET_SELECT_BUTTON, __name__ + ".HandleSelectButton")

	listedTypes = list(dConfig["ColorsList"].keys()) 
	listedTypes.sort()

	for typeC in listedTypes:
		listedColors = list(dConfig["ColorsList"][typeC].keys())
		listedColors.sort()
		pSubSubMenu = None
		for colorName in listedColors:
			if pSubSubMenu == None:
				pSubSubMenu = App.STMenu_Create(typeC) # What type of parameter
			if pSubSubMenu != None:
				colorNameOnM = ColorMessageFormat(str(colorName), dConfig[str(colorName + "R COLOR")], dConfig[str(colorName + "G COLOR")], dConfig[str(colorName + "B COLOR")], dConfig[str(colorName + "A COLOR")])
				pSubSub3Menu = App.STMenu_Create(colorNameOnM) # Name of the color parameter

				# Now we append 3 r, g, b, a and a reset to default.
				# TO-DO MAYBE MAKE THESE 4 BELOW A SLIDING BAR?
				CreateTextEntryButton("r (red): ", pSubSub3Menu, pOptionsPane, pSubSub3Menu, colorName + "R COLOR", __name__ + ".HandleKeyboardGoBetween")
				CreateTextEntryButton("g (green): ", pSubSub3Menu, pOptionsPane, pSubSub3Menu, colorName + "G COLOR", __name__ + ".HandleKeyboardGoBetween")
				CreateTextEntryButton("b (blue): ", pSubSub3Menu, pOptionsPane, pSubSub3Menu, colorName + "B COLOR", __name__ + ".HandleKeyboardGoBetween")
				CreateTextEntryButton("a (opacity): ", pSubSub3Menu, pOptionsPane, pSubSub3Menu, colorName + "A COLOR", __name__ + ".HandleKeyboardGoBetween")

				CreateButton("Reset to default", pSubSub3Menu, pSubSub3Menu, pSubSub3Menu, __name__ + ".ResetDefaultColors", myString=str(colorName))
				#CreateButton("Reset to default", pSubSub3Menu, pOptionsPane, pSubSub3Menu, __name__ + ".ResetDefaultColors", myString=str(colorName))

				pSubSubMenu.AddChild(pSubSub3Menu)

		if pSubSubMenu != None:
			pSubMenu.AddChild(pSubSubMenu)
	
	pMenu.AddChild(pSubMenu)

	return pSubMenu

def CreateFontMenu(sMenuName, pMenu, pOptionsPane, pContentPanel):
	pSubMenu = App.STMenu_Create(sMenuName)
	pSubMenu.AddPythonFuncHandlerForInstance(ET_SELECT_BUTTON, __name__ + ".HandleSelectButton")

	# Done above for default favorite font
	#listedFonts = list(dFont.keys())
	#listedFonts.sort()

	for font in listedFonts:
		for i in range(len(dFont[font])):
			pEvent = App.TGStringEvent_Create()
			pEvent.SetEventType(ET_SELECT_BUTTON)
			pEvent.SetDestination(pSubMenu)
			s = "%s%s%d" % (font, sSeparator, dFont[font][i])
			pEvent.SetString(str(s))
			pButton = App.STButton_Create(s, pEvent)
			pSubMenu.AddChild(pButton)

	CreateTextEntryButton("Custom size (may cause font issues): ", pSubMenu, pOptionsPane, pSubMenu, "FontSize", __name__ + ".HandleKeyboardGoBetween")
	pMenu.AddChild(pSubMenu)

	return pSubMenu

def HandleSelectButton(pObject, pEvent):
	pObject.CallNextHandler(pEvent)
	i = pEvent.GetCString()

	s = string.split(i, sSeparator)
	if len(s) >= 2 and s[0] != None and s[0] != "" and s[1] != None and s[1] != "":
		global dConfig
		dConfig["sFont"] = s[0]
		dConfig["FontSize"] = s[1]
		UpdateFontSubMenu(1)

def UpdateFontSubMenu(close=0, pSTMenu=None):
	UpdateSubMenu(close, pSTMenu)

def UpdateSubMenu(close=0, pSTMenu=None, newString=""):
	if pSTMenu == None:
		global pFontSubMenu
		if pFontSubMenu:
			pFontSubMenu.SetName(App.TGString(sBaseFMenu + str(dConfig["sFont"]) + str(sSeparator)+str(dConfig["FontSize"])))
			if close:
				pFontSubMenu.Close()
	else:
		pSTMenu.SetName(App.TGString(newString))

		if close:
			pSTMenu.Close()

	global pSaveButton
	if pSaveButton:
		ResetButtonString(None, pSaveButton, sSaveNotSaved)



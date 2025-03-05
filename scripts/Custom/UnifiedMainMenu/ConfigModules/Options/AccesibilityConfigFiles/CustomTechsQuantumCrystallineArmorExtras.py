# THIS FILE IS NOT SUPPORTED BY ACTIVISION
# THIS FILE IS UNDER THE LGPL LICENSE AS WELL
# CustomTechsQuantumCrystallineArmorExtras.py
# 5th March 2025, by Alex SL Gato (CharaToLoki)
# Version: 1.1
# Meant to be used alongside the AccesibilityConfig UMM option (located at scripts/Custom/UnifiedMainMenu/ConfigModules/Options/), this file must be under scripts/Custom/UnifiedMainMenu/ConfigModules/Options/AccesibilityConfigFiles
##################################
# This file takes care of listing the variable colors which are modified in other files and used instead of regular colors, like FoundationTech's Hull Gauge tech
extraVariables = {
	"g_kSubsystemFillColor" : {"kEmptyColor": ["Custom.Techs.QuantumCrystallineArmor"]},
	"CustomTechsQuantumCrystallineArmorFill" : {"kFillColor": ["Custom.Techs.QuantumCrystallineArmor"]},
}
# If we were to add extra App. colors, we can also add the following, as long as those colors exist or are registered on App.py
# If they are not registered on App.py then we register them ourselves!
import App
AblativeArmour = None
try:
	AblativeArmour = __import__("Custom.Techs.QuantumCrystallineArmor")
except:
	AblativeArmour = None

if AblativeArmour != None:
	App.CustomTechsQuantumCrystallineArmorFill = AblativeArmour.kFillColor

sDefaultColors = { # Colors from App.py
	# We could add it to a pre-existing category, like STButton marker colors.
	# Or maybe a new one
	"Foundation Technologies' colors" : {
		"CustomTechsQuantumCrystallineArmorFill": [None, []],
	},
}

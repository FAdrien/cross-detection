#!/usr/bin/python3
# -*- coding: utf-8 -*-



# -------------------------------- Introduction --------------------------------
	# -------------------------------- Licence --------------------------------
		# Le programme de masques a pour vocation a automatiser, par un programme
		# le remplissage de fichiers Excel renseignant sur les élèves qui découchent
		# ou mangent à la cantine le soir.

	# -------------------------------------------------------------------------



	# -------------------------------- Description --------------------------------
'''
		Ce programme a pour but d'automatiser les masques. Sur des périodes de 7 jours 
		(typiquement du vendredi au jeudi de la semaine suivante), les élèves d'une même 
		classe remplissent une feuille avec des croix (découché : oui/non, repas les midi et soir).
		Puis, il est nécessaire de passer ces résultats sous format Excel (coloration de cellules 
		suivant ce que chaque élève à inscrit sur le masque).

		L'idée est de fournir au programme une image scannée de chaque masque que ce dernier 
		utilise pour remplir les tableaux Excel (un pour la semaine, l'autre pour le week-end).

		À l'issue du scan, toutes les feuilles sont regroupées au sein d'une même fichier PDF.

		Le programme est composé de trois parties : 
		  -> détection de toutes les cases à cocher de la feuille scannée.

		  -> pour chaque case, détecter si la case en question est vide (type 0), contient une croix 
		(réponse positive - type 1) ou, contient une croix raturée (réponses négative - type 2).

		  -> enfin, colorier la/les case(s) correspondant aux découcher des élèves dans les deux
		fichiers Excel utilisés pour le pointage.

		Tous les chemins utilisés au sein du logiciel sont des objets 'Path' issus de la bibliothèque 
		standard 'pathlib' de Python. Une classe 'Fichier' a été conçue de manière à gérer les erreurs
		liées à des chemins erronées lorsque le programme demande un chemin vers un fichier.

		TODO : Une version graphique du logiciel serait fortement appréciée.

'''

	# -----------------------------------------------------------------------------

# ------------------------------------------------------------------------------



# -------------------------------- Bibliothèques --------------------------------
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from masques.images import lire_masques_scannees, construire_masque
from masques.masques import Eleve, classes, eleves

from excel.excel import Excel, Type, Couleur, FEUILLES_EXCEL_SEMAINE, FEUILLES_EXCEL_WEEKEND, TYPE_FICHIER

from entrainement.neurones import Croix, charger_reseau_de_neurones, detecter_croix, entrainer_reseau_de_neurones, charger_images
from entrainement.tableau_croix import *

# -------------------------------------------------------------------------------



# -------------------------------- Variables globales --------------------------------
# Numéro de version du programme : 
VERSION = '1.0'

# Nom des fichiers fournis par l'utilisateur : 
FICHIER_PDF = 'masques/fichiers/Classes.pdf'
FICHIER_POINTAGE_SEMAINE = 'excel/fichiers/Pointage semaine du 0602 au 0902.xlsm'
FICHIER_POINTAGE_WEEKEND = 'excel/fichiers/Pointage week end du 0302 au 0602.xlsm'

# ------------------------------------------------------------------------------------



# -------------------------------- Fonctions --------------------------------
def construire_classe(_fichiers_excel):
	'''
	'''
	for nom in FEUILLES_EXCEL_SEMAINE.keys():
		classe = classes[nom]
		classe.feuilles_excel = [fichier.feuilles[TYPE_FICHIER[fichier.type][nom]] for fichier in _fichiers_excel]
		feuille = classe.feuilles_excel[0]

		ligne = 0
		cellule = feuille['A' + str(ligne + feuille.fichier_excel.ligne)]
		nom_eleve = cellule.value
		while nom_eleve != None:
			eleve = Eleve(nom_eleve, classe, cellule.fill == Couleur.GRIS.value, [f.fichier_excel.ligne + ligne for f in classe.feuilles_excel])
			eleve.position = ligne
			classe.ajouter_eleve(eleve)

			ligne += 1
			cellule = feuille['A' + str(ligne + feuille.fichier_excel.ligne)]
			nom_eleve = cellule.value

# ---------------------------------------------------------------------------



# -------------------------------- Instructions --------------------------------
images = lire_masques_scannees(FICHIER_PDF)

excel_pointage_semaine = Excel(FICHIER_POINTAGE_SEMAINE, Type.SEMAINE)
excel_pointage_weekend = Excel(FICHIER_POINTAGE_WEEKEND, Type.WEEKEND)

construire_classe([excel_pointage_semaine, excel_pointage_weekend])

masques = list(map(construire_masque, images))

#reseau_de_neurones = construire_reseau_de_neurone()

# Pour entraîner le réseau de neurones : 
#tableau_croix = charger_tableau_croix(['entrainement/tableau/x3.pdf'])
#croix = extraire_croix(tableau_croix)
#enregistrer_croix(croix, Croix.CROIX_RAYEE)

#images_entrainement, images_validation = charger_images('entrainement/reseau_de_neurones/images_entrainement'), charger_images('entrainement/reseau_de_neurones/images_validation')
#entrainer_reseau_de_neurones(reseau_de_neurones, images_entrainement, images_validation)
#sauvegarder_reseau_de_neurones(reseau_de_neurones)

# Charger le réseau de neurones et faire les découchers : 
reseau_de_neurones = charger_reseau_de_neurones()

for eleve in eleves.values():
	eleve.decouche(reseau_de_neurones)

excel_pointage_semaine.workbook.save('pointage_semaine.xlsm')
excel_pointage_weekend.workbook.save('pointage_weekend.xlsm')

# ------------------------------------------------------------------------------

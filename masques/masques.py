#!/usr/bin/python3
# -*- coding: utf-8 -*-



# -------------------------------- Introduction --------------------------------
	# -------------------------------- Licence --------------------------------
		# Le programme de masques a pour vocation a automatiser, par un programme
		# le remplissage de fichiers Excel renseignant sur les élèves qui découchent
		# ou mangent à la cantine.

	# -------------------------------------------------------------------------



	# -------------------------------- Description --------------------------------
'''
		Ce fichier est un utilitaire pour la manipulation des masques.
'''

	# -----------------------------------------------------------------------------

# ------------------------------------------------------------------------------



# -------------------------------- Bibliothèques --------------------------------
import numpy as np

from openpyxl.styles import PatternFill

from excel.excel import Couleur, Type, intersection_lignes_colonnes, colonnes_consecutives_non_cachees

from entrainement.neurones import detecter_croix

import masques.images as images

# -------------------------------------------------------------------------------



# -------------------------------- Classes --------------------------------
class Eleve:
	'''
	'''

	def __init__(self, _nom, _classe, _est_mineur = None, _lignes = []):
		'''
			TODO : - revoir la pertinence de certains champs.
		'''
		self.nom = _nom
		self.classe = _classe
		self.est_mineur = _est_mineur
		self.lignes = _lignes
		self.position = 0

	def decouche(self, _reseau_de_neurones):
		'''
			TODO : - Vérifier que la date est dans la plage des dates du masque.
			       - Vérifier que l'élève peut découcher à la date donnée (lancer une erreur sinon)
			       - Vérifier que l'élève n'a pas coché simultanément 'découcher' et 'ne pas découcher'.
			       - Colorier la / les cellule(s) en vert.
		'''
		tableau = self.classe.masque.tableau
		image_binaire = self.classe.masque.image_binaire.image_binaire
		decouchers = [detecter_croix(_reseau_de_neurones, np.rot90(images.extraire_rectangle(image_binaire, tableau[3 + self.position][numero]))) for numero in [1, 5, 9, 17]]

		for (ligne, feuille) in zip(self.lignes, self.classe.feuilles_excel):
			decoucher_vendredi, decoucher_samedi, decoucher_dimanche, decoucher_mercredi = decouchers
			cellules_a_colorier = []

			if feuille.fichier_excel.type == Type.WEEKEND:
				cellules_disponibles = intersection_lignes_colonnes(colonnes_consecutives_non_cachees(feuille.feuille, 'C', 12), [ligne])

				if decoucher_vendredi == 1:
					cellules_a_colorier.extend(cellules_disponibles[ : 3])

				if decoucher_samedi == 1:
					cellules_a_colorier.extend(cellules_disponibles[3 : 8])

				if decoucher_dimanche == 1:
					cellules_a_colorier.extend(cellules_disponibles[8 : ])

			elif feuille.fichier_excel.type == Type.SEMAINE:
				cellules_disponibles = intersection_lignes_colonnes(colonnes_consecutives_non_cachees(feuille.feuille, 'G', 4), [ligne])

				if decoucher_mercredi == 1:
					cellules_a_colorier.extend(cellules_disponibles)

			for cellule in cellules_a_colorier:
				feuille.feuille[cellule].fill =  PatternFill(fgColor = '9BBB59', fill_type = 'solid')#Couleur.VERT.value

class Classe:
	'''
	'''

	def __init__(self, _nom, _liste_eleves = [], _masque = None, _feuilles_excel = []):
		'''
			TODO : - liste des élèves, sous quel format ? Que faire si seulement le nombre d'élèves est connu ?
		'''
		self.nom = _nom
		self.masque = _masque
		self.liste_eleves = _liste_eleves
		self.feuilles_excel = _feuilles_excel

	def ajouter_eleve(self, _eleve):
		self.liste_eleves.append(_eleve)
		eleves[_eleve.nom] = _eleve

class Masque:
	'''
	'''

	def __init__(self, _image, _classe):
		'''
		'''
		self.image = _image
		self.image_binaire = self.image.binariser()
		self.classe = _classe

		self.composantes_connexes = []
		self.tableau = []

		self.reponses = []

# -------------------------------------------------------------------------



# -------------------------------- Variables --------------------------------
# Dictionnaire de correspondance entre le nom de la classe et l'objet 'Classe' associé.
classes = {'CPES' : Classe('CPES'), 'MPSI' : Classe('MPSI'), 'PCSI' : Classe('PCSI'), 'MP' : Classe('MP'), 'PSI' : Classe('PSI')}

# Dictionnaire de correspondance entre le nom de l'élève et l'objet 'Eleve' associé.
eleves = dict()
# ---------------------------------------------------------------------------

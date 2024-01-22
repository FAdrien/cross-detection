#!/usr/bin/python3
# -*- coding: utf-8 -*-



# -------------------------------- Introduction --------------------------------
	# -------------------------------- Licence --------------------------------
		# Le programme de masques a pour vocation a automatiser, par un programme
		# le remplissage de fichiers Excel renseignant sur les élèves qui découchent
		# ou mangent à la cantine.
		#
		# Copyright (C) 2023  FRADIN Adrien.
		# Here is how you can contact the author:
		#				- e-mail (recommended): f_adrien@outlook.fr
		#				- paper mail: [Intentionally not specified for privacy reasons]
		#
		# Ce fichier fait parti du programme de masques.
		#
		# This program is free software: you can redistribute it and/or modify
		# it under the terms of the GNU General Public License as published by
		# the Free Software Foundation, either version 3 of the License, or
		# (at your option) any later version.
		#
		# This program is distributed in the hope that it will be useful,
		# but WITHOUT ANY WARRANTY; without even the implied warranty of
		# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
		# GNU General Public License for more details.
		#
		# You should have received a copy of the GNU General Public License
		# along with this program.  If not, see <https://www.gnu.org/licenses/>.

	# -------------------------------------------------------------------------



	# -------------------------------- Description --------------------------------
'''
		Ce fichier permet de charger, découper et préparer les images des croix

'''

	# -----------------------------------------------------------------------------

# ------------------------------------------------------------------------------



# -------------------------------- Bibliothèques --------------------------------
import cv2
import numpy as np

from pdf2image import convert_from_path

from random import shuffle

from masques.images import Image, extraire_tableau, extraire_rectangle

from entrainement.neurones import *

# -------------------------------------------------------------------------------



# -------------------------------- Variables --------------------------------

# ---------------------------------------------------------------------------



# -------------------------------- Fonctions --------------------------------
def charger_tableau_croix(_chemins):
	pages_pdf = [convert_from_path(chemin, dpi = 300, hide_annotations = True)[0] for chemin in _chemins]
	return [Image(cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)) for page in pages_pdf]

def extraire_croix(_images):
	images_binaires = [image.binariser().image_binaire for image in _images]
	cases = []

	for image_binaire, image in zip(images_binaires, _images):
		composantes_connexes = extraire_tableau(image, 60, False, False)[1]

		for composante in composantes_connexes:
			case = extraire_rectangle(image_binaire, composante)
			case_niveau_de_gris = cv2.cvtColor(case, cv2.COLOR_GRAY2BGR)
			case_ajustee = cv2.resize(case, dsize = TAILLE_IMAGE, interpolation = cv2.INTER_NEAREST)
			cases.append(case_ajustee)

	return cases

def enregistrer_croix(_croix, _type, _ratio = 0.2):
	shuffle(_croix)
	taille = len(_croix)

	n = int(0.2 * taille)
	validation, entrainement = _croix[ : n], _croix[n : ]

	for (i, image) in enumerate(entrainement):
		cv2.imwrite('entrainement/reseau_de_neurones/images_entrainement/' + _type.value + '/' + str(i) + '.png', image)
	for (i, image) in enumerate(validation):
		cv2.imwrite('entrainement/reseau_de_neurones/images_validation/' + _type.value + '/' + str(i) + '.png', image)

# ---------------------------------------------------------------------------



# -------------------------------- Instructions --------------------------------

# ------------------------------------------------------------------------------

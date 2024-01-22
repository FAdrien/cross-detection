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
		

'''

	# -----------------------------------------------------------------------------

# ------------------------------------------------------------------------------



# -------------------------------- Bibliothèques --------------------------------
import os

import cv2

# Pour l'énumération des types de croix : 
from enum import Enum

import keras
from keras import backend as K
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras.preprocessing.image import ImageDataGenerator

from utils.fichiers import Fichier
# -------------------------------------------------------------------------------


# -------------------------------- Variables --------------------------------
FICHIER_RESEAU = Fichier('entrainement/reseau_de_neurones/reseau_detection_croix_3.h5', _fonction_lecture = lambda fichier: keras.models.load_model(fichier.chemin))
TAILLE_IMAGE = (120, 50)
FORMAT_IMAGE = (1, TAILLE_IMAGE[0], TAILLE_IMAGE[1]) if K.image_data_format() == 'channels_first' else (TAILLE_IMAGE[0], TAILLE_IMAGE[1], 1)

DOSSIER_IMAGES_ENTRAINEMENT = 'reseau_de_neurones/images_entrainement'
DOSSIER_IMAGES_VALIDATION = 'reseau_de_neurones/images_validation'

EPOCHS = 10
TAILLE_BATCH = 50
# ---------------------------------------------------------------------------


# -------------------------------- Fonctions --------------------------------
def construire_reseau_de_neurone():
	'''
		TODO : - Être capable de configurer le réseau de neurones en dehors (cf. configuration + architecture).
	'''
	reseau_de_neurones = Sequential()
	reseau_de_neurones.add(Conv2D(32, (3, 3), input_shape = FORMAT_IMAGE))
	reseau_de_neurones.add(Activation('relu'))
	reseau_de_neurones.add(MaxPooling2D(pool_size = (2, 2)))

	reseau_de_neurones.add(Conv2D(32, (2, 2)))
	reseau_de_neurones.add(Activation('relu'))
	reseau_de_neurones.add(MaxPooling2D(pool_size = (2, 2)))

	reseau_de_neurones.add(Conv2D(64, (2, 2)))
	reseau_de_neurones.add(Activation('relu'))
	reseau_de_neurones.add(MaxPooling2D(pool_size = (2, 2)))

	reseau_de_neurones.add(Conv2D(64, (2, 2)))
	reseau_de_neurones.add(Activation('relu'))
	reseau_de_neurones.add(MaxPooling2D(pool_size = (2, 2)))

	reseau_de_neurones.add(Flatten())
	reseau_de_neurones.add(Dense(64))
	reseau_de_neurones.add(Activation('relu'))
	reseau_de_neurones.add(Dropout(0.5))
	reseau_de_neurones.add(Dense(1))
	reseau_de_neurones.add(Activation('sigmoid'))

	reseau_de_neurones.compile(loss = keras.losses.categorical_crossentropy, optimizer = keras.optimizers.Adadelta(), metrics = ['accuracy'])
	return reseau_de_neurones

def charger_images(_dossier):
	'''
	'''
	donnees = ImageDataGenerator(rescale = 1. / 255)
	nombre_images = 0

	for racine, repertoires, fichiers in os.walk(_dossier):
		for fichier in fichiers:
			nombre_images += 1

	generateur = donnees.flow_from_directory(
		_dossier,
		color_mode = 'grayscale', 
		target_size = TAILLE_IMAGE,
		batch_size = TAILLE_BATCH,
		class_mode = 'binary')

	return (nombre_images, generateur)

def entrainer_reseau_de_neurones(_reseau_de_neurones, _images_entrainement, _images_validation):
	'''
	'''
	_reseau_de_neurones.fit_generator(
		_images_entrainement[1], 
		steps_per_epoch = _images_entrainement[0] // TAILLE_BATCH, 
		epochs = EPOCHS, 
		validation_data = _images_validation[1], 
		validation_steps = _images_validation[0] // TAILLE_BATCH)

def sauvegarder_reseau_de_neurones(_reseau_de_neurones, _fichier = FICHIER_RESEAU):
	'''
	'''
	_reseau_de_neurones.save(_fichier.chemin)

def charger_reseau_de_neurones(_fichier = FICHIER_RESEAU):
	'''
	'''
	return _fichier.lecture()

def detecter_croix(_reseau_de_neurones, _case, _message = 0):
	'''
		TODO : - Vérifier que la case a les bonnes dimensions.
	'''
	#case_traitee = keras.utils.img_to_array(_case)
	case_retaillee = cv2.resize(_case, TAILLE_IMAGE).reshape(1, TAILLE_IMAGE[0], TAILLE_IMAGE[1], 1)
	case_normalisee = case_retaillee / 255.0
	#case_retaillee = case_normalisee.reshape(1, TAILLE_IMAGE[0], TAILLE_IMAGE[1], 1)

	reponse = _reseau_de_neurones.predict(case_normalisee, verbose = _message)[0][0]
	return 0 if reponse < 0.5 else 1

# ---------------------------------------------------------------------------


# -------------------------------- Classes --------------------------------
class Croix(Enum):
	'''
		Énumération des types de croix que l'on peut rencontrer lors de la détection.
	'''
	VIDE = '0'
	CROIX = '1'
	#CROIX_RAYEE = '2'

# -------------------------------------------------------------------------

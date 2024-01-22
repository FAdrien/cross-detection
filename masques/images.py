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
		Ce fichier sert à l'importation d'images, à leur manipulation et à leur 
		sauvegarde.
'''

	# -----------------------------------------------------------------------------

# ------------------------------------------------------------------------------



# -------------------------------- Bibliothèques --------------------------------
# Pour la manipulation d'images : 
import cv2
import numpy as np

# Pour la reconnaissance optique de caractères : 
import pytesseract as ocr

# Pour ouvrir, parcourir et convertir des fichiers .pdf en tableau NumPy : 
from pdf2image import convert_from_path

# Pour trier des listes : 
from operator import itemgetter

from masques.masques import Masque, classes

# -------------------------------------------------------------------------------


# -------------------------------- Variables --------------------------------

# ---------------------------------------------------------------------------


# -------------------------------- Fonctions --------------------------------
# def importer_masques_scannees(_donnees_json):
	# '''
		# TODO : - Être plus souple sur la présence ou non de l'attribut "classes" ?
	# '''
	# pass

def lire_masques_scannees(_chemin, _resolution = 300, _nombre_de_classes = 5):
	'''
		TODO : - Que faire si les masques ne sont pas tous regroupés en un seul fichier .pdf ?
		       - Que faire si l'extension n'est pas un .pdf ? Format d'entrée des masques ?
		       - Détecter la rotation des masques -> faire une fonction pour détecter s'il y a besoin de faire des rotations, si oui, combien ?
		       - Détecter si la page est au format portrait ou paysage ?
	'''

	# Conversion de chaque page du pdf en une image PIL.
	pages = convert_from_path(_chemin, dpi = _resolution, hide_annotations = True)
	# Fixe le pas dans le cas où les images ont été scannées recto-verso.
	pas = 2 if len(pages) == 2 * _nombre_de_classes else 1

	# On renvoie la liste des masques de chaque classe (sous forme d'images OpenCV).
	return [Image(cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)) for page in pages[0::pas]]

def extraire_rectangle(_image, _rectangle, _reverse = False):
	'''
	'''
	x, y, w, h = _rectangle
	return _image[y : y + h, x : x + w] if not _reverse else _image[x : x + w, y : y + h]

def trier_liste(_liste, _fonction_comparaison = itemgetter(0, 1), _order_inverse = True):
	'''
		Une fonction pour trier une liste (typiquement, une liste de composantes connexes, ces
		dernières étant représentées par des tableaux NumPy).
	'''
	return list(sorted(_liste, key = _fonction_comparaison, reverse = _order_inverse))

def reparer_lignes(_lignes_horizontales, _lignes_verticales):
	'''
	'''

	# Réparer les lignes horizontales 'brisées' (avec du blanco/souris par exemple).
	lignes_horizontales_allongees = cv2.dilate(_lignes_horizontales.image_binaire, np.ones((100, 1), np.uint8), iterations = 10)
	lignes_horizontales = cv2.dilate(lignes_horizontales_allongees, np.ones((1, 6), np.uint8), iterations = 1)

	# Allongement des lignes verticales
	lignes_verticales = cv2.dilate(_lignes_verticales.image_binaire, np.ones((1, 50), np.uint8), iterations = 10)

	return ImageBinaire(lignes_horizontales), ImageBinaire(lignes_verticales)

def combiner_lignes(_lignes_horizontales, _lignes_verticales):
	return ImageBinaire(_lignes_horizontales.image_binaire | _lignes_verticales.image_binaire)

def filtrer_composantes_connexes(_composantes_connexes):
		return _composantes_connexes[(10 < _composantes_connexes[:, 2]) & (_composantes_connexes[:, 2] < 80)]

def traitement_composantes_connexes(_image_binaire, _ajuster_taille, _fonction_filtrage = filtrer_composantes_connexes):
	'''
	'''

	def ajuster_taille_composante_connexe(_composante_connexe, _dx = -5, _dy = -5, _dw = 8, _dh = 5):
		'''
		'''
		x_0, y_0, w_0, h_0, _ = _composante_connexe
		x_1, y_1, w_1, h_1 = x_0 + _dx, y_0 + _dy, w_0 + _dw, h_0 + _dh
		return np.array([x_1, y_1, w_1, h_1])

	def liste_composantes_connexes(_filtrer_composantes = True):
		'''
			Renvoie les composantes connexes de l'image binaire 
			fournie en entrée. Les deux premières composantes
			connexes sont la feuille entière et le tableau.
		'''
		_, labels, composantes_connexes, _ = cv2.connectedComponentsWithStats(~_image_binaire, connectivity = 8, ltype = cv2.CV_32S)

		# On filtre les composantes connexes pour enlever les 'imperfections'.
		if _filtrer_composantes:
			composantes_connexes = _fonction_filtrage(composantes_connexes)

		# On ajuste légèrement la taille des composantes connexes (rectangulaires).
		if _ajuster_taille:
			return list(map(ajuster_taille_composante_connexe, composantes_connexes))

		# On renvoie les composantes connexes de l'image (les deux premières composantes connexes sont l'image et le tableau entier).
		return composantes_connexes[:, : -1]

	return liste_composantes_connexes()

def dessiner_composantes_connexes(_masque, _couleur = (0, 0, 255), _epaisseur = 2):
	'''
		TODO : - Vérifier que c'est un masque.
	'''
	image = _masque.image_binaire.copy()

	for x, y, w, h in _masque.composantes_connexes:
		cv2.rectangle(image, (x, y), (x + w, y + h), _couleur, _epaisseur)

	return Image(image)

def construire_tableau(_composantes_connexes, _ecart, _ajouter_derniere_colonne):
	tableau, colonne = [], [_composantes_connexes[0]]

	for composante in _composantes_connexes[1:]:
		if abs(colonne[-1][1] - composante[1]) < _ecart:
			colonne.append(composante)
		else:
			tableau.append(trier_liste(colonne))
			colonne = [composante]

	# Attention aux causes d'inhomogénéité dans le nombre de lignes : 
	if _ajouter_derniere_colonne:
		tableau.append(trier_liste(colonne))

	return np.array(tableau).transpose(1, 0, 2)

# TODO : - est-ce pertinent de dégager cette fonction et d'opter pour une fonction plus générale de reconnaissance de caractères ?
def detecter_classe(_image, _tableau, _rotation = 1, _caracteres = 'CEIMPS', _langue = 'eng'):
	'''
		TODO : - que faire si la détection n'aboutie pas ?
		       - passer la liste des caractères dans le fichier de configuration ? Automatiser sa construction via le nom des classes ?
	'''
	image = np.rot90(extraire_rectangle(_image, _tableau[1][0]), k = _rotation)
	return ocr.image_to_string(image, config = '--oem 1 --psm 7 -l ' + _langue +' -c tessedit_char_whitelist=' + _caracteres)[:-2]

# TODO : - à mettre ailleurs ? -> fichier neurones.py ?
def verifier_coherence_resultats(_tableau_reponses):
	'''
		TODO : - vérifier que chaque élève découche ou non
			   - pas de découcher OUI et NON pour un élève donné.
	'''
	pass

def extraire_tableau(_image, _ecart = 60, _ajouter_derniere_colonne = False, _ajuster_taille = True):
	image_normalisee = _image.normaliser()
	image_binaire = image_normalisee.binariser()

	lignes_horizontales, lignes_verticales = image_binaire.extraction_lignes()
	lignes_horizontales_reparees, lignes_verticales_reparees = reparer_lignes(lignes_horizontales, lignes_verticales)
	lignes = combiner_lignes(lignes_horizontales_reparees, lignes_verticales_reparees)

	masque_image = image_binaire.plus_grand_contour()
	tableau_binaire = ImageBinaire(cv2.bitwise_and(lignes.image_binaire, lignes.image_binaire, mask = masque_image.image_binaire))

	composantes_connexes = traitement_composantes_connexes(tableau_binaire, _ajuster_taille)
	tableau = construire_tableau(composantes_connexes, _ecart, _ajouter_derniere_colonne)

	return tableau, composantes_connexes

def construire_masque(_image):
	'''
	'''
	tableau, composantes_connexes = extraire_tableau(_image, _ajuster_taille = False)

	nom_classe = detecter_classe(_image, tableau)

	classe = classes[nom_classe]
	classe.masque = Masque(_image, classe)
	classe.masque.composantes_connexes = composantes_connexes
	classe.masque.tableau = tableau

	return classe.masque
# ---------------------------------------------------------------------------


# -------------------------------- Classes --------------------------------
class Image:
	'''
	'''

	def __init__(self, _image):
		'''
		'''

		self.image = _image

		# Extraction des trois canaux (Rouge, Vert et Bleu) de l'image.
		self.canaux = cv2.split(self.image)

	def normaliser(self):
		'''
		'''
		canaux_normalises = []

		for canal in self.canaux:
			canal_dilate = cv2.dilate(canal, np.ones((7, 7), np.uint8))
			canal_filtre = cv2.medianBlur(canal_dilate, 21)
			difference = 255 - cv2.absdiff(canal, canal_filtre)
			canal_normalise = cv2.normalize(difference, None, alpha = 0, beta = 255, norm_type = cv2.NORM_MINMAX, dtype = cv2.CV_8UC1)

			canaux_normalises.append(canal_normalise)

		return Image(cv2.merge(canaux_normalises))

	def niveau_de_gris(self):
		'''
		'''
		return Image(cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY))

	def binariser(self, _limite = 200, _valeur_maximale = 255):
		'''
			TODO : (- Traiter le cas où l'image n'est pas en niveau de gris... ?) ???
		'''
		# On applique un filtre gaussien pour lisser l'image.
		niveau_de_gris_lisse = cv2.GaussianBlur(self.niveau_de_gris().image, (7, 7), 0)
		# On convertit l'image en image binaire avec comme barrière _limite (en anglais : 'threshold').
		_, image_binaire = cv2.threshold(niveau_de_gris_lisse, _limite, _valeur_maximale, cv2.THRESH_BINARY)

		return ImageBinaire(~image_binaire)

	def __getitem__(self, item):
		return self.image[item]


class ImageBinaire:
	'''
	'''

	def __init__(self, _image_binaire):
		'''
			TODO : - Vérifier que l'image d'entrée est bien une image binaire.
		'''

		self.image_binaire = _image_binaire


	def extraction_lignes(self):
		def extractions_lignes_verticales(_taille = 100):
			noyau = cv2.getStructuringElement(cv2.MORPH_RECT, (_taille, 1))
			# On applique un noyau vertical sur l'image binaire pour ne conserver que les lignes verticales de l'image.
			return ImageBinaire(cv2.morphologyEx(self.image_binaire, cv2.MORPH_OPEN, noyau))

		def extractions_lignes_horizontales(_taille = 450):
			noyau = cv2.getStructuringElement(cv2.MORPH_RECT, (1, _taille))
			# On applique un noyau horizontal sur l'image binaire pour ne conserver que les lignes horizontales de l'image.
			return ImageBinaire(cv2.morphologyEx(self.image_binaire, cv2.MORPH_OPEN, noyau))

		# On renvoie les images contenant les lignes horizontales et verticales de l'image binaire initiale.
		return extractions_lignes_horizontales(), extractions_lignes_verticales()

	def plus_grand_contour(self):
		'''
		'''
		image_binaire_dilatee = cv2.dilate(self.image_binaire, np.ones((5, 5), np.uint8), iterations = 5)
		contours, _ = cv2.findContours(image_binaire_dilatee, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

		# Extraction du contour d'aire maximale.
		contour_tableau = max(contours, key = cv2.contourArea)
		image_noire = np.zeros(image_binaire_dilatee.shape, np.uint8)

		# On renvoie une image binaire dont le contour le plus grand a été remplis en blanc.
		return ImageBinaire(cv2.drawContours(image_noire, [contour_tableau], 0, 255, -1))

	def __invert__(self):
		return ~self.image_binaire

	def __getitem__(self, item):
		return self.image_binaire[item]

# -------------------------------------------------------------------------

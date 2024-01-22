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
		Ce fichier est un utilitaire pour la manipulation de fichiers.
'''

	# -----------------------------------------------------------------------------

# ------------------------------------------------------------------------------



# -------------------------------- Bibliothèques --------------------------------
# Pour la manipulation des chemins / système de fichiers : 
from pathlib import Path

# -------------------------------------------------------------------------------



# -------------------------------- Classes --------------------------------
class Fichier:
	'''
	'''

	def __init__(self, _chemin_vers_fichier, _extension_demandee = None, _creation_automatique = False, _fonction_lecture = None):
		'''
			TODO : - Faciliter la lecture / écriture dans un fichier : 
						* en fournissant une / des fonctions prévues à cette effet ?
						* autres ?
				   - 'self.repertoire' est-ce un nom adéquat ?
		'''
		self.chemin = Path(_chemin_vers_fichier)
		self.repertoire = self.chemin.parent
		self.extension = _extension_demandee

		resultat = self._verifier_chemin()

		self.fonction_lecture = _fonction_lecture

		# Création du fichier et des répertoires parents si demandé et, s'ils n'existent pas : 
		if _creation_automatique and not self.chemin.is_file():
			self.chemin.parent.mkdir(exist_ok = True, parents = True)

	def _verifier_chemin(self):
		'''
			TODO : - Vérifier la validité du chemin fourni : chemin correct + fichier comme 
			composante finale + extension (si fournie).
			       - Mettre à jour l'extension du fichier si elle vaut 'None' à ce stade.
			       - Mettre en place un code pour la valeur de renvoie (l'uniformiser à 
			l'ensemble du programme).
			       - Détecter si l'extension est vide ou n'est pas reconnue.
			liste des extensions utilisées : json, png, jpg, jpeg, pdf...)
				   - Cas non conformes : * le chemin ne pointe pas vers un fichier,
									     * la composante finale n'est pas un fichier et / ou contient un point.
		'''
		composante_finale = self.chemin.name
		if isinstance(self.extension, str):
			if not composante_finale.endswith('.' + self.extension):
				# TODO : Cas où l'extension a été fournie mais, n'est pas trouvée dans la composante finale.
				pass
			else:
				self.nom = '.'.join(composante_finale.split('.')[ : -1])
				return 0
		else:
			# TODO : Cas où l'extension n'a pas été fournie (entre autre : la mettre à jour !!).
			pass

	def lecture(self):
		'''
			TODO : - Améliorer pour disposer de fonctions d'ouvertures personnalisées.
			       - Que faire si la fonction de lecture est à None ?
		'''
		return self.fonction_lecture(self)
# -------------------------------------------------------------------------

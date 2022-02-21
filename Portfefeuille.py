# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 13:13:52 2022

@author: PC
"""
from curses.ascii import SO
from re import M
from Actifs import Actifs
from VaRCov import VaRCov
from Connexion import Connexion
import  random

#pour copier la liste d'actif et pas faire de doublons
import copy
import math
import numpy as np
class Portefeuille():

    def __init__(self, liste_Actifs, valeur, volatilite, rendement, score):
        self.liste_Actifs = liste_Actifs
        self.valeur = valeur
        self.volatilite = volatilite
        self.rendement = rendement
        self.score = score


    # Calcul le prix de l'actif avec le plus faible 
    def plus_petit_prix(liste_Actif):
        min = liste_Actif[0].valeur
        for asset in liste_Actif:
            if asset.valeur < min:
                min = asset.valeur
        return min 

   

    #Créé un portefeuil composé d'une liste d'action aléatoire
    def Creation_Portefeuille(self, MaxInvesti):

        #pour copier la liste d'actif et pas faire de doublons
        liste_Actif = copy.deepcopy(self.liste_Actifs)

        prix_min = Portefeuille.plus_petit_prix(liste_Actif) 
        action = list(range(len(liste_Actif))) # liste des index de tous les actifs du portefeuille   

        for i in range(len(liste_Actif)):
            liste_Actif[i].nb_shares = 0

        while (MaxInvesti > prix_min and len(action) !=0 ):
        # Tant que la valeur a investir (MaxInvest) est superieur au prix de l'actif le moins cher
        # Et tant que la liste des index des actifs du portefeuil n'est pas vide
        # on ajoute une action au portefeuill

            # Selection aléatoire d'une action via son index dans la liste d'actif
            choix_action = random.choice(action)
            action.remove(choix_action) # On retire l'index de la liste pour ne pas tomber deux fois sur le même actif

            # Nombre maximal de shares que l'on peut acheter pour cet actif
            max_nb = MaxInvesti//(liste_Actif[choix_action].valeur)
            # Selection du nombre de shares entre 0 et nb_max 

            #self.liste_nbr_shares[choice_asset] = random.randint(0,max_nb)
            rnd = random.randint(0,max_nb)
            liste_Actif[choix_action].nb_shares = rnd
            # On reduit la valeur a investir en lui retirant la valeur des parts de l'actif choisi
            MaxInvesti = MaxInvesti - liste_Actif[choix_action].nb_shares*liste_Actif[choix_action].valeur
            #MaxInvesti = MaxInvesti - int(self.liste_nbr_shares[choice_asset])*self.liste_Actifs[choice_asset].valeur

        self.Valeur_Portefeuille(liste_Actif) #calule les poids
        self.Poid_dans_portefeuille(liste_Actif) # calcule la valeur finale du portefeuille
        self.VolPortefeuille(liste_Actif)
        self.RendementsPF(liste_Actif)
        self.RatioSharpe()
        self.liste_Actifs = liste_Actif
        
        return self


    # Calcul la valeur d'un portefeuille
    def Valeur_Portefeuille(self,liste_Actifs):
        #Fonction qui prend en argument un portefeuille et qui calcule
        #la valeur associée à ce portefeuille 
        for i in range(len( liste_Actifs)):
            #valeur=valeur asset*poids
            self.valeur = self.valeur + liste_Actifs[i].valeur*int( liste_Actifs[i].nb_shares)
            #self.valeur = self.valeur +  self.liste_Actifs[i].valeur*int( self.liste_nbr_shares [i])


    #################################################################################################################################
    #Defini le poids qu'a l'action dans le portefeuille
    def Poid_dans_portefeuille(self,liste_Actif):
        for i in range(len(liste_Actif)):
            poids = liste_Actif[i].valeur * liste_Actif[i].nb_shares
            liste_Actif[i].poids  = round(poids / self.valeur,5)
    ####################################################################################################################################
    
    def VolPortefeuille(self,listeActif):
        Listepoids=[]
        for i in listeActif:
            Listepoids.append(i.poids)
        Listepoids=np.array(Listepoids)
        #print(Listepoids)
        mat = VaRCov([]) 
        connection = Connexion('CAC40','root','Petruluigi0405@!')
        connection.initialisation()
        mat.CalculMatrice(connection,"2018-11-01","2018-11-30")
        matrice=mat.matrice
        #print(matrice)
        connection.close_connection()
        vol=math.sqrt((np.transpose(Listepoids))@matrice@Listepoids)
        print("vol   ",vol)
        self.volatilite=vol
    
    def RendementsPF(self, liste_Actif):
        RendementPF =0
        Liste=[]
        SommePF=1
        for j in range(len(liste_Actif[1].ListeRendementsValeurs)):
            RendementPF =0
            for i in liste_Actif:
                Liste=i.ListeRendementsValeurs
                RendementPF+=Liste[j][0]*i.nb_shares*Liste[j][1]/self.valeur
            SommePF*=(1+RendementPF)
        self.rendement = SommePF-1
        
    def RatioSharpe(self):
        ratio = self.rendement/self.volatilite
        self.score = ratio
        
    def Contrainte(portefeuille):
        connexion = Connexion('CAC40','root','Petruluigi0405@!')
        contrainte_limite = 0
        for i in self:
            contrainte_limite += i.rendements * i.nb_shares
        contrainte_limite = (contrainte_limite - 1)**2
        for i in self.liste_Actifs:
            requete = "Select rendements from CAC40 where noms ='"+ i.noms +"';"
            rendements_actif = connexion.execute(requete)
            for row in self.liste_Actifs:
                contrainte_limite += max(0,row['rendements']-1)**2 +  max(0,row['rendements'])**2
        return contrainte_limite
    
    def CAGR_pf(self, liste_Actif, date1, date2):
        cagr_pf = 0
        for i in liste_Actif:
            cagr_pf += i.CAGR(self,date1, date2, Connexion('BDD','root','PetruLuigi0405@!'))*i.nb_shares  #J'ai consideré que le CAGR d'un portefeuille était la somme des CAGR de chaque actif pondéré par leurs poids
        self.score = cagr_pf
        
    
    def mutation(self,MaxInvest):
    
        r = random.randrange(0,len(self.liste_Actifs))
        while (self.liste_Actifs[r].nb_shares == 0):
            r = random.randrange(0,len(self.liste_Actifs))

        # retire la valeur de l'actif au portefeuille
        self.valeur -= MaxInvest
        self.liste_Actifs[r].nb_shares = 0
        print("Nom de l'action Mutée : "+self.liste_Actifs[r].nom)

        prix_min = Portefeuille.plus_petit_prix(self.liste_Actifs) 
        action = list(range(len(self.liste_Actifs))) # liste des index de tous les actifs du portefeuille   

        action.remove(r) #On retire l'actif qu'on vient de retirer du portefeuille de la liste

        #On realise la même manipulation que pour creation_portefeuille
        while (MaxInvest > prix_min and len(action) !=0 ):

            choix_action = random.choice(action)
            action.remove(choix_action) 

            max_nb = MaxInvest//(self.liste_Actifs[choix_action].valeur)

            rnd = random.randint(0,max_nb)
            self.liste_Actifs[choix_action].nb_shares = rnd
            
            valeur = self.liste_Actifs[choix_action].nb_shares*self.liste_Actifs[choix_action].valeur
            MaxInvest = MaxInvest - valeur

            self.valeur += valeur #On ajoute la valeur des actions a la valeur du portefeuille

        return self
        
    def __repr__(self):
        #return "{0}\nValeur du portefeuille :  {2}\nScore du portefeuille : {3}\nVol du portefeuille : {4}\nRendementPF : {1}\n\n".format(self.liste_Actifs,self.volatilite,self.valeur,self.score) 
        return "\nListe Actifs : {0}, \nValeur portefeuille : {1}, \nSharpe : {2}, \nVol : {3}\nRendementPF : {4}".format(self.liste_Actifs,self.valeur, self.score, self.volatilite,self.rendement)
  

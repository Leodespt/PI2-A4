#Classe d'actifs
class Actifs():

    def __init__(self, nom, valeur, volume, date,nb_shares,rendement,poids,ListeRendementsValeurs):
        self.nom = nom
        self.valeur = valeur
        self.volume = volume
        self.date = date
        self.nb_shares = nb_shares
        self.rendement = rendement
        self.poids=poids 
        self.ListeRendementsValeurs=ListeRendementsValeurs



    def creationActifs(connexion):
        #Fonction qui prend en argument la connexion avec la base de données
        #La fonction retourne une liste d'actifs avec le nom de chaque actif 
        #Tout les autres attributs sont initialisée à 0     
        requete = 'Select distinct name from cac'
        curseur = connexion.execute(requete)
        liste_Actifs = []

        for row in curseur:
            action = Actifs(row['name'],0,0,0,0,0,0,0)
            liste_Actifs.append(action)
            
        return liste_Actifs



    def Valeur_Actifs(self, date1, date2, connection):
        #Fonction  qui prend en arguments une liste d'actifs, la date du jour (date1), 
        #la date jusqu'à laquelle on souhaite etudier la performance de l'actif (date2)
        #et la connexion avec la base de données

        #La fonction retourne une liste d'actifs, chacun asocié à une liste contenant
        #toutes les informations le concernant
        requete = "Select value,volume,Rendements from cac where date = '"+date1+"' and name = '"+str(self.nom)+"';"
        curseur = connection.execute(requete)
        row = curseur.fetchone()
        
        self.valeur = row['value']
        self.volume = row['volume']
        self.date = date1
        self.rendement=row['Rendements']
        self.poids=0
        self.RendementsPourPF(date1,date2,connection)
        
        return self
    


    #Creation d'une liste de (rendements actif,valeur actif) par jour pour un actif sur la période donnée (date1 à date2)
    def RendementsPourPF(self,date1,date2,connection):
        Liste=[]
        requete2="select Rendements,value from cac where name='"+str(self.nom)+"' and date between '"+date1+"' and '"+date2+"';"
        #on récupère la liste des Rendements de chaque actif
        curseur2=connection.execute(requete2)    
        for row in curseur2:
            Liste.append([row['Rendements'],row['value']])

        #On ajoute la liste (rendements,valeur) aux parametres de l'actif
        self.ListeRendementsValeurs=Liste



    #Fonction qui retourne les informations concernant une action sous forme de chaine de caratères
    def __repr__(self):
        return "Nom : {0}, Valeur : {1}, Nbr d'Actions : {2}, \nDate : {3}\n".format(self.nom,self.valeur, self.nb_shares, self.date)



    ##################################  FONCTION PAS UTILISEE ################################################
    
    def MoyenneRendements(self,date1,date2,connection):
        Liste=[]
        requete1="Select distinct name from cac;"
        curseur=connection.execute(requete1)
        ListeNoms=[]
        #on récupère la liste des noms des actifs
        for row in curseur:
            ListeNoms.append(row['name'])
        for name in ListeNoms:
            somme=0
            requete2="select Rendements from cac where name='"+name+"' and date between '"+date1+"' and '"+date2+"';"
            #on récupère la liste des Rendements de chaque actif
            curseur2=connection.execute(requete2)    
            nbrow=0
        for row in curseur2:
            somme+=(row['Rendements'])
            nbrow+=1
        moyenne=round(somme,6)
        if(self.nom==name):
            self.moyenneRendements=moyenne



    def CAGR(self, date1, date2, connexion):
        requete1 = "Select value from cac where name = '"+self.nom+"';"
        requete2 = "Select value from cac where name = '" + self.nom + "' and date = '"+ date1 +"';"  # Récupération de P_initial
        requete3 = "Select value from cac where name ='" + self.nom + "' and date = '"+ date2 +"';" # Récupération de P_final
        requete4 = "Select count(value) from cac where name = '" + self.nom + "' and date between '" + date1 + "' and '" +date2 + "';"
        P_init = connexion.execute(requete2)
        P_final = connexion.execute(requete3)
        nb_jours = connexion.execute(requete4)
        cagr = ((P_final / P_init) **(1/nb_jours))
        return cagr

    #############################################################################################################
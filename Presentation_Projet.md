# Contenu de Présentation Professionnelle
## Analyse de Sentiment en Temps Réel sur les Flux X

---

## 📄 Slide 1 – Page de garde

**Titre Principal:**
# Analyse de Sentiment en Temps Réel sur les Flux X

**Sous-titre:**
Real-Time Sentiment Analysis on X Streams

**Domaine:**
Intelligence Artificielle | Big Data | Machine Learning | Streaming en Temps Réel

**Réalisé par:**
- ELHADJI Oussama
- BEN ACHA Yassine
- CHAKOR Abdellatif
- MENACH Achraf

**Année:** 2024-2025

---

## 📄 Slide 2 – Plan de Présentation

**Titre:** Axes de la Présentation

**Déroulement de la soutenance :**

**I. Introduction**
- 📌 Contexte général et motivation
- 📌 Problématique identifiée
- 📌 Objectifs et périmètre du projet

**II. Analyse et Conception**
- 📌 Analyse fonctionnelle
- 📌 Architecture globale du système
- 📌 Description des données utilisées
- 📌 Méthodologie adoptée

**III. Développement et Implémentation**
- 📌 Modèles d'Intelligence Artificielle
- 📌 Stack technologique
- 📌 Architecture du code et organisation

**IV. Résultats et Validation**
- 📌 Résultats quantitatifs et qualitatifs
- 📌 Évaluation et performances
- 📌 Démonstration de l'application

**V. Retour d'Expérience**
- 📌 Difficultés rencontrées et solutions
- 📌 Perspectives et améliorations futures

**VI. Conclusion**
- 📌 Bilan du projet
- 📌 Questions & Réponses

---

## 📄 Slide 3 – Contexte général

**Titre:** Contexte et Motivation du Projet

**Contenu:**
- **Contexte académique :** Projet Big Data et Machine Learning
- **Évolution des réseaux sociaux :** X génère des millions de tweets par jour
- **Besoin croissant :** Analyser en temps réel l'opinion publique sur des événements, produits ou personnalités
- **Applications pratiques :**
  - Veille stratégique pour les entreprises
  - Détection de tendances émergentes
  - Gestion de crise et e-réputation
  - Analyse marketing et comportementale
- **Enjeu technologique :** Traiter des flux massifs de données non structurées en temps réel

---

## 📄 Slide 4 – Problématique

**Titre:** Problématique Identifiée

**Contenu:**
- **Problème principal :** Comment analyser automatiquement le sentiment de milliers de tweets en temps réel ?

- **Défis techniques identifiés :**
  - Volume massif de données textuelles non structurées
  - Besoin de traitement en streaming (latence minimale)
  - Hétérogénéité du langage (argot, fautes, emojis, abréviations)
  - Classification multi-classes : Positif, Négatif, Neutre, Irrelevant

- **Limites des solutions traditionnelles :**
  - Traitement batch : temps de réponse trop long
  - Modèles simples : faible précision
  - Absence d'infrastructure scalable pour le temps réel

**Question centrale :** Comment concevoir un pipeline intelligent capable d'ingérer, traiter et classifier automatiquement des tweets en temps réel avec une haute précision ?

---

## 📄 Slide 5 – Objectifs du projet

**Titre:** Objectifs du Projet

**Objectif principal :**
Développer une application web intelligente pour l'analyse automatique de sentiment en temps réel sur des flux X utilisant le Machine Learning et les technologies Big Data.

**Objectifs spécifiques :**
1. **Ingestion de données :** Capturer des flux X en temps réel via Apache Kafka
2. **Prétraitement :** Nettoyer et transformer les données textuelles (tokenization, stop words removal)
3. **Modélisation ML :** Entraîner et optimiser des modèles de classification de sentiment
4. **Prédiction temps réel :** Classifier chaque tweet en 4 catégories (Negative, Positive, Neutral, Irrelevant)
5. **Stockage intelligent :** Sauvegarder les résultats dans une base MongoDB
6. **Visualisation :** Créer une interface web interactive pour monitorer les résultats en temps réel
7. **Scalabilité :** Assurer la capacité de traiter des milliers de tweets/seconde

---

## 📄 Slide 6 – Périmètre du projet

**Titre:** Périmètre du Projet

**Ce qui est INCLUS ✅**
- Collecte de données X via fichiers CSV et simulation
- Pipeline de streaming temps réel avec Kafka et Spark
- Entraînement de modèles ML (Logistic Regression, Naive Bayes)
- Classification automatique en 4 classes de sentiment
- Interface web Flask pour visualisation et interaction
- Architecture conteneurisée avec Docker
- Stockage persistant dans MongoDB

**Ce qui est EXCLU ❌**
- Connexion directe à l'API X temps réel (utilisation de données simulées)
- Analyse multi-langues (focus sur l'anglais)
- Analyse d'images ou de vidéos dans les tweets
- Détection de sarcasme ou d'ironie
- Analyse des métadonnées utilisateur (localisation, followers, etc.)
- Déploiement en production sur cloud

---

## 📄 Slide 7 – Analyse fonctionnelle

**Titre:** Analyse Fonctionnelle

**Acteurs du système :**
1. **Utilisateur final :** Analyste, marketeur, data scientist
2. **Producteur Kafka :** Simule l'ingestion de tweets
3. **Moteur Spark :** Traite et classifie les tweets
4. **Application Flask :** Interface utilisateur

**Cas d'utilisation principaux :**

| ID | Cas d'usage | Description |
|----|-------------|-------------|
| UC1 | Soumettre un tweet manuel | L'utilisateur saisit un texte et obtient le sentiment prédit |
| UC2 | Lancer le streaming | Diffuser automatiquement des tweets depuis le fichier de validation |
| UC3 | Visualiser les prédictions | Consulter en temps réel les résultats d'analyse |
| UC4 | Consulter l'historique | Accéder aux 50 dernières prédictions stockées |
| UC5 | Entraîner le modèle | Lancer l'entraînement sur le dataset de formation |

**Flux principal :**
Ingestion → Prétraitement → Feature Engineering → Prédiction → Stockage → Visualisation

---

## 📄 Slide 8 – Architecture globale

**Titre:** Architecture Globale du Système

**Architecture en 4 couches :**

**1. Couche Ingestion (Data Source)**
- Fichiers CSV : `X_training.csv`, `X_validation.csv`
- Producteur Kafka : Envoie les tweets au topic `tweets`

**2. Couche Messaging (Stream Processing)**
- **Zookeeper** : Coordination des services Kafka
- **Apache Kafka** : Broker de messages pour streaming temps réel
- Topics : `tweets` (entrée des messages)

**3. Couche Traitement (Processing & ML)**
- **Apache Spark Streaming** : Consommation des messages Kafka
- **Spark MLlib** : Application du modèle de ML pré-entraîné
- Pipeline : Tokenization → Stop Words Removal → Hashing TF → IDF → Prédiction

**4. Couche Présentation & Stockage**
- **MongoDB** : Base NoSQL pour stockage des prédictions
- **Flask Application** : Interface web pour interaction et visualisation
- **API REST** : Endpoints pour produire/consommer des tweets

**Conteneurisation :**
- Docker Compose pour orchestration (Kafka, Zookeeper, MongoDB)

---

## 📄 Slide 9 – Données utilisées

**Titre:** Description des Données

**Source principale :**
- **Dataset Kaggle :** X Entity Sentiment Analysis
- **Lien :** https://www.kaggle.com/datasets/jp797498e/X-entity-sentiment-analysis

**Fichiers de données :**

| Fichier | Utilisation | Taille | Nombre de lignes |
|---------|-------------|--------|------------------|
| `X_training.csv` | Entraînement du modèle | ~10 MB | ~74,000 tweets |
| `X_validation.csv` | Test temps réel | ~165 KB | ~1,000 tweets |

**Structure du dataset :**
```
Colonnes : [TweetID, Entity, Sentiment, Content]
- TweetID : Identifiant unique
- Entity : Entité mentionnée (produit, marque, personne)
- Sentiment : Label (Positive, Negative, Neutral, Irrelevant)
- Content : Texte du tweet
```

**Prétraitement effectué :**
1. Nettoyage : suppression des valeurs nulles
2. Normalisation : conversion en minuscules
3. Suppression : balises HTML, URLs, chiffres, caractères spéciaux
4. Tokenization : découpage en mots
5. Filtrage : suppression des stop words (and, the, is, etc.)

---

## 📄 Slide 10 – Méthodologie

**Titre:** Méthodologie Adoptée

**Approche globale :** Architecture Lambda adaptée pour le streaming temps réel

**Étapes du projet :**

**Phase 1 : Préparation des données**
1. Exploration et analyse du dataset Kaggle
2. Nettoyage et prétraitement du texte
3. Feature engineering (TF-IDF)

**Phase 2 : Développement du modèle ML**
4. Entraînement de modèles avec Spark MLlib
5. Optimisation des hyperparamètres (Grid Search + Cross-Validation)
6. Sauvegarde des modèles entraînés

**Phase 3 : Pipeline de streaming**
7. Configuration de l'infrastructure Kafka + Zookeeper
8. Développement du consumer Spark Streaming
9. Intégration du modèle ML dans le pipeline

**Phase 4 : Application web**
10. Développement de l'interface Flask
11. Connexion à MongoDB pour stockage
12. API REST pour interaction utilisateur

**Phase 5 : Conteneurisation et déploiement**
13. Dockerisation de l'environnement
14. Tests et validation end-to-end

---

## 📄 Slide 11 – Modèles / Algorithmes

**Titre:** Modèles d'Intelligence Artificielle Utilisés

**Modèles entraînés :**

**1. Logistic Regression (Régression Logistique) ✅ Modèle retenu**
- **Type :** Classification multi-classes
- **Hyperparamètres optimisés :**
  - `regParam` : 0.01 (régularisation)
  - `elasticNetParam` : 0.0 (L2 penalty)
  - `maxIter` : 10 (itérations)
- **Performance :** **86.64% d'accuracy**
- **Justification du choix :** Meilleure performance, bon équilibre biais-variance

**2. Naive Bayes (Classificateur bayésien naïf)**
- **Type :** Classification probabiliste
- **Hyperparamètres optimisés :**
  - `smoothing` : 1.0 (Laplace smoothing)
- **Performance :** **82.51% d'accuracy**
- **Avantages :** Rapide, efficace sur texte

**Optimisation :**
- **Technique :** Grid Search avec Cross-Validation (3-5 folds)
- **Métrique :** Accuracy (précision globale)

**Feature Engineering :**
- TF-IDF (Term Frequency - Inverse Document Frequency)
- Hashing TF : 262,144 features

---

## 📄 Slide 12 – Outils et technologies

**Titre:** Stack Technologique

**Langages de programmation :**
- **Python 3.x** : Langage principal (ML, streaming, web)
- **JavaScript** : Frontend interactif
- **SQL** : Requêtes MongoDB

**Frameworks Big Data :**
- **Apache Spark 3.1.2** : Traitement distribué
- **Spark MLlib** : Machine Learning
- **Spark Structured Streaming** : Streaming temps réel

**Streaming & Messaging :**
- **Apache Kafka** : Broker de messages
- **Zookeeper** : Coordination de services

**Machine Learning & NLP :**
- **Scikit-learn concepts** : Classification
- **NLTK** : Natural Language Processing
- **Tokenizer, StopWordsRemover, HashingTF, IDF** (Spark ML)

**Web Development :**
- **Flask** : Framework web Python
- **HTML/CSS** : Interface utilisateur
- **Server-Sent Events (SSE)** : Streaming temps réel vers frontend

**Base de données :**
- **MongoDB** : Base NoSQL pour stockage des prédictions

**Conteneurisation :**
- **Docker & Docker Compose** : Orchestration des services

**Bibliothèques Python :**
- `pyspark`, `kafka-python`, `pymongo`, `pandas`, `flask`

---

## 📄 Slide 13 – Implémentation

**Titre:** Architecture du Code et Organisation

**Structure du projet :**
```
Real-Time_Sentiment_Analysis_on_X/
│
├── Application - FLASK/          # Application web
│   ├── main.py                   # Serveur Flask
│   ├── templates/                # Pages HTML
│   └── static/                   # CSS, JS
│
├── Spark/                        # Scripts Spark
│   ├── Spark-MLlib.py           # Entraînement des modèles
│   ├── KafkaSpark-Streaming.py  # Consumer Kafka + ML
│   ├── Kafka-Streaming.py       # Alternative de streaming
│   ├── X_training.csv     # Dataset d'entraînement
│   └── X_validation.csv   # Dataset de validation
│
├── docker-compose.yml            # Orchestration des services
├── Dockerfile                    # Image Spark-Jupyter
└── README.md                     # Documentation
```

**Pipeline technique :**

**1. Entraînement (`Spark-MLlib.py`) :**
```
Chargement CSV → Tokenization → Stop Words Removal → 
HashingTF → IDF → StringIndexer → 
Train/Test Split → Grid Search + Cross-Validation → 
Sauvegarde modèle (V1, IDF_V1)
```

**2. Streaming (`KafkaSpark-Streaming.py`) :**
```
Kafka Consumer → Déserialisation → Preprocessing → 
Feature Engineering → Prédiction ML → 
Calcul confidence → Sauvegarde MongoDB
```

**3. Application Web (`main.py`) :**
```
Endpoints Flask → Kafka Producer → 
MongoDB Monitoring (Change Stream) → 
SSE pour streaming temps réel → Visualisation
```

---

## 📄 Slide 14 – Résultats obtenus

**Titre:** Résultats Quantitatifs et Qualitatifs

**Performances des modèles ML :**

| Modèle | Accuracy | Temps d'entraînement | Modèle retenu |
|--------|----------|---------------------|---------------|
| Logistic Regression | **86.64%** | ~2-3 min | ✅ Oui |
| Naive Bayes | **82.51%** | ~1-2 min | ❌ Non |

**Résultats quantitatifs :**
- **Précision globale :** 86.64% sur le test set
- **Dataset de test :** ~15,000 tweets (20% du total)
- **Classes prédites :** 4 catégories (Positive, Negative, Neutral, Irrelevant)
- **Temps de prédiction :** < 500ms par tweet en streaming

**Résultats qualitatifs :**
- ✅ Pipeline end-to-end fonctionnel
- ✅ Streaming temps réel opérationnel avec Kafka + Spark
- ✅ Interface web intuitive et réactive
- ✅ Stockage persistant des prédictions
- ✅ Architecture conteneurisée et reproductible
- ✅ Scalabilité démontrée (traitement de 1000+ tweets)

**Exemples de prédictions réussies :**
- "I love this product!" → **Positive** (confidence: 0.92)
- "Terrible experience, very disappointed" → **Negative** (confidence: 0.88)
- "The weather is cloudy today" → **Neutral** (confidence: 0.79)

---

## 📄 Slide 15 – Évaluation et performances

**Titre:** Métriques d'Évaluation et Analyse des Performances

**Métriques ML utilisées :**
- **Accuracy (Précision globale) :** 86.64%
- **Métrique d'évaluation :** `MulticlassClassificationEvaluator`

**Optimisation des hyperparamètres :**

**Logistic Regression - Grid Search :**
- `regParam` testé : [0.1, 0.01] → Optimal : **0.01**
- `elasticNetParam` testé : [0.0, 0.5, 1.0] → Optimal : **0.0**
- `maxIter` testé : [10, 50, 100] → Optimal : **10**

**Naive Bayes - Grid Search :**
- `smoothing` testé : [0.0, 1.0, 2.0] → Optimal : **1.0**

**Cross-Validation :**
- **K-Folds :** 3 folds pour LR, 5 folds pour NB
- **Avantage :** Réduction de l'overfitting

**Performances système :**
- **Latence streaming :** < 1 seconde par batch
- **Throughput :** ~500 tweets/seconde (testé)
- **Utilisation mémoire :** 12GB alloués (Spark driver + executor)
- **Stockage MongoDB :** Insertion batch efficace

**Comparaison des modèles :**
- **Gagnant :** Logistic Regression (+4.13% accuracy vs Naive Bayes)
- **Trade-off :** LR légèrement plus lent mais plus précis

---

## 📄 Slide 16 – Difficultés rencontrées

**Titre:** Défis Techniques et Solutions Apportées

**Difficultés majeures :**

**1. Gestion de la mémoire Spark**
- **Problème :** OutOfMemory errors lors du traitement de gros datasets
- **Solution :** Configuration de `spark.executor.memory` et `spark.driver.memory` à 12GB

**2. Connexion Kafka-Spark**
- **Problème :** Erreurs de dépendances pour `spark-sql-kafka` connector
- **Solution :** Utilisation de `--packages` lors du spark-submit avec versions compatibles

**3. Streaming continu MongoDB**
- **Problème :** Change Stream nécessite replica set
- **Solution :** Configuration MongoDB en mode replica set (`rs0`) dans Docker

**4. Prétraitement du texte**
- **Problème :** Données bruitées (emojis, URLs, caractères spéciaux)
- **Solution :** Pipeline de nettoyage robuste avec regex et UDF Spark

**5. Latence temps réel**
- **Problème :** Délai entre production et affichage
- **Solution :** Optimisation du batch interval et utilisation de Server-Sent Events (SSE)

**6. Reproducibilité de l'environnement**
- **Problème :** Dépendances multiples et conflits de versions
- **Solution :** Containerisation complète avec Docker Compose

**7. Cross-Validation coûteux**
- **Problème :** Temps d'entraînement long avec Grid Search
- **Solution :** Réduction du nombre de folds et parallelisation Spark

---

## 📄 Slide 17 – Perspectives et améliorations

**Titre:** Perspectives Futures et Axes d'Amélioration

**Améliorations court terme :**
1. **Connexion API X réelle** : Intégrer l'API X v2 pour flux live authentiques
2. **Modèles avancés :** Tester BERT, RoBERTa, transformers pour NLP
3. **Détection de sarcasme :** Ajouter une couche d'analyse linguistique avancée
4. **Support multi-langues :** Étendre à d'autres langues (français, arabe, espagnol)

**Optimisations techniques :**
5. **Dashboard analytics :** Intégrer Grafana/Kibana pour visualisation avancée
6. **Alerting intelligent :** Notifications automatiques sur détection de sentiment négatif massif
7. **Scalabilité cloud :** Déploiement sur AWS/GCP/Azure avec auto-scaling

**Extensions fonctionnelles :**
8. **Analyse d'entités nommées (NER) :** Identifier automatiquement les entités mentionnées
9. **Topic modeling :** Détection automatique des sujets tendances
10. **Analyse des influenceurs :** Scoring de l'impact des utilisateurs

**Recherche et innovation :**
11. **Modèles hybrides :** Combiner rule-based et deep learning
12. **Analyse temporelle :** Évolution du sentiment dans le temps
13. **Prédiction de viralité :** Anticiper les tweets qui vont devenir viraux

**Intégration business :**
14. **API commerciale :** Exposer le service via API REST pour clients externes
15. **Reporting automatique :** Génération de rapports PDF/Excel périodiques

---

## 📄 Slide 18 – Démonstration

**Titre:** Démonstration de l'Application

**Fonctionnalités démontrées :**

**1. Page d'accueil (`/`)**
- Saisie manuelle d'un tweet
- Bouton "Analyze Sentiment"
- Affichage instantané du résultat et de la confiance

**2. Page de streaming (`/stream`)**
- Bouton "Start Streaming Tweets"
- Diffusion automatique depuis `X_validation.csv`
- Visualisation en temps réel des tweets et sentiments
- Mise à jour dynamique sans rechargement (SSE)

**3. Page de validation (`/validation`)**
- Historique des 50 dernières prédictions
- Tableau : Content | Sentiment | Confidence
- Tri anti-chronologique

**4. Architecture en action**
```
User Input → Flask API → Kafka Producer → 
Spark Streaming → ML Model → MongoDB → 
SSE Stream → Frontend Update
```

**Liens de démonstration :**
- **Repository :** [GitHub](https://github.com/Bosaj/Real-Time_Sentiment_Analysis_on_X)

---

## 📄 Slide 19 – Conclusion

**Titre:** Conclusion et Bilan du Projet

**Objectifs atteints ✅**
- ✅ Pipeline complet d'analyse de sentiment en temps réel opérationnel
- ✅ Modèle ML avec 86.64% de précision
- ✅ Architecture Big Data scalable (Kafka + Spark + MongoDB)
- ✅ Application web interactive et responsive
- ✅ Containerisation complète avec Docker
- ✅ Documentation technique complète

**Compétences acquises :**
- Maîtrise de l'écosystème Apache (Kafka, Spark, Zookeeper)
- Expertise en NLP et classification de texte
- Architecture micro-services et streaming temps réel
- MLOps : entraînement, sauvegarde, déploiement de modèles
- DevOps : Docker, orchestration de services

**Impact du projet :**
- 🎯 Solution concrète pour veille stratégique
- 🎯 Base solide pour un produit commercial
- 🎯 Démonstration de compétences Big Data & IA

**Message final :**
Ce projet illustre parfaitement l'intégration de technologies Big Data modernes (Kafka, Spark) avec le Machine Learning pour résoudre une problématique réelle : comprendre l'opinion publique en temps réel. L'architecture mise en place est extensible et prête pour une utilisation en production avec des améliorations futures.

---

## 📄 Slide 20 – Questions & Réponses

**Titre:** Questions ?

**Sujets de discussion possibles :**

**Questions techniques :**
- Comment avez-vous géré les dépendances Spark-Kafka ?
- Pourquoi Logistic Regression plutôt que Deep Learning ?
- Comment gérez-vous la scalabilité ?
- Quelle est la latence réelle du système ?

**Questions métiers :**
- Quelles sont les applications concrètes ?
- Comment améliorer la précision du modèle ?
- Est-ce viable en production ?

**Architecture :**
- Pourquoi MongoDB plutôt qu'une autre base ?
- Comment assurer la haute disponibilité ?

**Améliorations :**
- Quelles sont les prochaines étapes ?
- Comment intégrer l'API X officielle ?

---

## 📄 Slide 21 – Annexes

**Titre:** Annexes et Ressources

**Références :**
1. **Dataset :** Kaggle - X Entity Sentiment Analysis
2. **Documentation :** Apache Spark, Kafka, MongoDB
3. **Repository GitHub :** https://github.com/Bosaj/Real-Time_Sentiment_Analysis_on_X
4. **Vidéo démo :** [Lien GitHub Assets]

**Technologies documentées :**
- Apache Kafka Documentation
- Spark Structured Streaming Guide
- Spark MLlib Guide
- Flask Documentation
- MongoDB Change Streams

**Commandes clés :**
```bash
# Lancer Kafka + MongoDB
docker-compose up -d

# Builder l'image Spark-Jupyter
docker build -t spark-jupyter:latest .

# Entraîner le modèle
spark-submit Spark-MLlib.py

# Lancer le streaming
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2 KafkaSpark-Streaming.py

# Lancer Flask
python Application-FLASK/main.py
```

---

**FIN DE LA PRÉSENTATION**

*Merci pour votre attention !*

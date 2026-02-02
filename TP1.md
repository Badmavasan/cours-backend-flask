# TP SSR “BookShelf Pro” (niveau difficile, guidé pas à pas)
**Objectif :** construire une mini-application SSR complète avec Flask : pages, templates, sessions, formulaires, validation, messages, pagination, recherche, édition/suppression, protection de routes, et gestion d’erreurs.

> **Règle du TP :** SSR uniquement (pas d’API JSON aujourd’hui).  

> **Stockage :** en mémoire (liste/dict Python) pour rester focus sur les concepts web.

> **Ne pas utiliser des générateurs de code** : Chatgpt, Gemini, CLaude, Grok, etc.

---

## Résultat attendu (démo finale)
À la fin, on doit pouvoir :
- se connecter / se déconnecter (session)
- voir une liste paginée de livres, filtrer par auteur, rechercher par titre
- ajouter un livre via un formulaire (validation + erreurs affichées)
- éditer un livre existant
- supprimer un livre avec une confirmation
- voir une page détail d’un livre
- afficher des messages “flash” (succès / erreur)
- accéder aux pages uniquement si connecté
- avoir une page 404 et une page 500 propres (templates)

---

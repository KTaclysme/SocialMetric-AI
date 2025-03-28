import os
import datetime
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF

def generate_evaluation_report(results, output_path=None):
    if output_path is None:
        report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
        os.makedirs(report_dir, exist_ok=True)
        output_path = os.path.join(report_dir,
                                   f"rapport_evaluation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
    os.makedirs(temp_dir, exist_ok=True)

    plt.figure(figsize=(8, 6))
    conf_matrix = np.array(results['confusion_matrix'])
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Négatif', 'Positif'],
                yticklabels=['Négatif', 'Positif'])
    plt.title('Matrice de confusion')
    plt.xlabel('Prédit')
    plt.ylabel('Réel')
    conf_matrix_path = os.path.join(temp_dir, 'confusion_matrix.png')
    plt.tight_layout()
    plt.savefig(conf_matrix_path)
    plt.close()

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, "Rapport d'évaluation du modèle d'analyse de sentiment", 0, 1, 'C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Généré le {datetime.datetime.now().strftime('%d/%m/%Y à %H:%M')}", 0, 1, 'C')
    pdf.ln(10)

    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "1. Résumé des performances", 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Précision (accuracy): {results['accuracy']:.4f}", 0, 1)

    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "2. Rapport de classification", 0, 1)
    pdf.set_font('Arial', '', 12)

    report = results['classification_report']
    header = ['Classe', 'Précision', 'Rappel', 'F1-score']
    data = [
        ['Négatif', f"{report['négatif']['precision']:.4f}", f"{report['négatif']['recall']:.4f}",
         f"{report['négatif']['f1-score']:.4f}"],
        ['Positif', f"{report['positif']['precision']:.4f}", f"{report['positif']['recall']:.4f}",
         f"{report['positif']['f1-score']:.4f}"]
    ]

    col_width = 190 / 4
    pdf.ln(5)

    pdf.set_font('Arial', 'B', 12)
    for item in header:
        pdf.cell(col_width, 10, item, 1, 0, 'C')
    pdf.ln()

    pdf.set_font('Arial', '', 12)
    for row in data:
        for item in row:
            pdf.cell(col_width, 10, item, 1, 0, 'C')
        pdf.ln()

    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "3. Matrice de confusion", 0, 1)
    pdf.image(conf_matrix_path, x=30, w=150)

    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "4. Analyse et recommandations", 0, 1)
    pdf.set_font('Arial', '', 12)

    performance_analysis = analyze_performance(results)
    pdf.multi_cell(0, 10, performance_analysis)

    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Recommandations pour améliorer le modèle:", 0, 1)
    pdf.set_font('Arial', '', 12)

    recommendations = get_recommendations(results)
    for i, recommendation in enumerate(recommendations, 1):
        pdf.multi_cell(0, 10, f"{i}. {recommendation}")

    if 'examples' in results and results['examples']:
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, "5. Exemples de prédictions", 0, 1)
        pdf.set_font('Arial', '', 12)

        for i, example in enumerate(results['examples'], 1):
            correct = "+" if example['true_sentiment'] == example['predicted_sentiment'] else "-"
            pdf.multi_cell(0, 10, f"Exemple {i} {correct}")
            pdf.multi_cell(0, 10, f"Texte: \"{example['text']}\"")
            pdf.multi_cell(0, 10, f"Sentiment réel: {example['true_sentiment']}")
            pdf.multi_cell(0, 10, f"Sentiment prédit: {example['predicted_sentiment']}")
            pdf.ln(5)

    pdf.output(output_path)

    if os.path.exists(conf_matrix_path):
        os.remove(conf_matrix_path)

    return output_path


def analyze_performance(results):
    accuracy = results['accuracy']
    report = results['classification_report']

    analysis = "Analyse des performances du modèle:\n\n"

    if accuracy >= 0.9:
        analysis += f"Le modèle présente une excellente précision globale de {accuracy:.2%}. "
    elif accuracy >= 0.8:
        analysis += f"Le modèle présente une bonne précision globale de {accuracy:.2%}. "
    elif accuracy >= 0.7:
        analysis += f"Le modèle présente une précision acceptable de {accuracy:.2%}. "
    else:
        analysis += f"Le modèle présente une précision insuffisante de {accuracy:.2%}, nécessitant des améliorations. "

    pos_f1 = report['positif']['f1-score']
    neg_f1 = report['négatif']['f1-score']

    if abs(pos_f1 - neg_f1) > 0.1:
        if pos_f1 > neg_f1:
            analysis += f"\n\nLe modèle est plus performant pour détecter les sentiments positifs (F1={pos_f1:.2f}) que négatifs (F1={neg_f1:.2f}). Cela peut indiquer un biais dans les données d'entraînement ou une difficulté à capturer les nuances négatives."
        else:
            analysis += f"\n\nLe modèle est plus performant pour détecter les sentiments négatifs (F1={neg_f1:.2f}) que positifs (F1={pos_f1:.2f}). Cela peut indiquer un biais dans les données d'entraînement ou une tendance à classifier les contenus ambigus comme négatifs."
    else:
        analysis += f"\n\nLe modèle présente un bon équilibre entre la détection des sentiments positifs (F1={pos_f1:.2f}) et négatifs (F1={neg_f1:.2f})."

    conf_matrix = np.array(results['confusion_matrix'])
    false_pos = conf_matrix[0][1]  # Faux positifs
    false_neg = conf_matrix[1][0]  # Faux négatifs

    if false_pos > false_neg:
        analysis += f"\n\nLe modèle tend à classifier à tort des tweets négatifs comme positifs ({false_pos} cas). Cela pourrait être problématique si l'objectif est de détecter les sentiments négatifs avec une haute sensibilité."
    elif false_neg > false_pos:
        analysis += f"\n\nLe modèle tend à classifier à tort des tweets positifs comme négatifs ({false_neg} cas). Cela pourrait conduire à une surestimation des sentiments négatifs dans l'analyse."

    return analysis


def get_recommendations(results):
    accuracy = results['accuracy']
    report = results['classification_report']

    recommendations = []

    recommendations.append("Augmenter la taille du jeu de données d'entraînement avec plus d'exemples diversifiés.")

    if accuracy < 0.8:
        recommendations.append(
            "Essayer des modèles plus sophistiqués comme BERT ou des réseaux de neurones pour capturer des relations plus complexes dans le texte.")

    pos_recall = report['positif']['recall']
    neg_recall = report['négatif']['recall']

    if pos_recall < 0.8:
        recommendations.append(
            "Ajouter plus d'exemples positifs variés pour améliorer la capacité du modèle à détecter les sentiments positifs.")

    if neg_recall < 0.8:
        recommendations.append(
            "Ajouter plus d'exemples négatifs variés pour améliorer la capacité du modèle à détecter les sentiments négatifs.")

    recommendations.append(
        "Améliorer le prétraitement des textes en incluant la lemmatisation, la suppression des mots vides, et la gestion des emojis/symboles spécifiques aux réseaux sociaux.")
    recommendations.append(
        "Expérimenter avec des caractéristiques supplémentaires comme les n-grammes, les caractéristiques stylistiques, ou les embeddings de mots pré-entraînés.")

    recommendations.append(
        "Vérifier l'équilibre du jeu de données entre les classes positives et négatives, et appliquer des techniques de rééchantillonnage si nécessaire.")

    return recommendations


if __name__ == "__main__":
    test_results = {
        'accuracy': 0.85,
        'classification_report': {
            'négatif': {'precision': 0.83, 'recall': 0.87, 'f1-score': 0.85},
            'positif': {'precision': 0.87, 'recall': 0.83, 'f1-score': 0.85}
        },
        'confusion_matrix': [[43, 7], [8, 42]],
        'examples': [
            {'text': 'Ce politicien est remarquable', 'true_sentiment': 'positive', 'predicted_sentiment': 'positive'},
            {'text': 'Je déteste sa politique', 'true_sentiment': 'negative', 'predicted_sentiment': 'negative'},
            {'text': 'Une performance moyenne', 'true_sentiment': 'positive', 'predicted_sentiment': 'negative'}
        ]
    }

    output_path = generate_evaluation_report(test_results)
    print(f"Rapport de test généré: {output_path}")
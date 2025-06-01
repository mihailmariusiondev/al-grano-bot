from typing import Dict

def get_summary_prompt(tone: str, length: str, language: str, include_names: bool) -> str:
    """Generate a customized system prompt based on configuration settings.

    Args:
        tone: 'neutral', 'informal', 'sarcastic', 'ironic', or 'absurd'
        length: 'short', 'medium', or 'long'
        language: 'es', 'en', 'fr', or 'pt'
        include_names: Whether to include participant names in the summary

    Returns:
        A system prompt string in the specified language

    Raises:
        ValueError: If language is not supported
    """
    # Validate language is supported
    if language not in ['es', 'en', 'fr', 'pt']:
        raise ValueError(f"Language '{language}' is not supported")

    # Define tone descriptions in each language
    tone_desc = {
        'es': {
            'neutral': "neutral y objetivo",
            'informal': "informal y cercano",
            'sarcastic': "sarcástico y divertido",
            'ironic': "irónico y perspicaz",
            'absurd': "absurdo y surrealista"
        },
        'en': {
            'neutral': "neutral and objective",
            'informal': "casual and friendly",
            'sarcastic': "sarcastic and funny",
            'ironic': "ironic and insightful",
            'absurd': "absurd and surreal"
        },
        'fr': {
            'neutral': "neutre et objectif",
            'informal': "décontracté et amical",
            'sarcastic': "sarcastique et amusant",
            'ironic': "ironique et perspicace",
            'absurd': "absurde et surréaliste"
        },
        'pt': {
            'neutral': "neutro e objetivo",
            'informal': "casual e amigável",
            'sarcastic': "sarcástico e engraçado",
            'ironic': "irônico e perspicaz",
            'absurd': "absurdo e surreal"
        }
    }

    # Define length descriptions in each language
    length_desc = {
        'es': {
            'short': "breve (2-3 frases)",
            'medium': "de longitud media (5-7 frases)",
            'long': "detallado (10-15 frases)"
        },
        'en': {
            'short': "brief (2-3 sentences)",
            'medium': "medium length (5-7 sentences)",
            'long': "detailed (10-15 sentences)"
        },
        'fr': {
            'short': "bref (2-3 phrases)",
            'medium': "de longueur moyenne (5-7 phrases)",
            'long': "détaillé (10-15 phrases)"
        },
        'pt': {
            'short': "breve (2-3 frases)",
            'medium': "de comprimento médio (5-7 frases)",
            'long': "detalhado (10-15 frases)"
        }
    }

    # Define name inclusion text in each language
    names_text = {
        'es': {
            True: "manteniendo los nombres de los participantes cuando sea posible",
            False: "sin mencionar nombres específicos de los participantes"
        },
        'en': {
            True: "keeping participant names when possible",
            False: "without mentioning specific participant names"
        },
        'fr': {
            True: "en conservant les noms des participants lorsque c'est possible",
            False: "sans mentionner les noms spécifiques des participants"
        },
        'pt': {
            True: "mantendo os nomes dos participantes quando possível",
            False: "sem mencionar nomes específicos dos participantes"
        }
    }

    # Build the prompt based on language
    if language == 'es':
        prompt = f"Eres un asistente que resume conversaciones con un tono {tone_desc['es'][tone]}.\n"
        prompt += f"Tu tarea es generar un resumen {length_desc['es'][length]}, {names_text['es'][include_names]}.\n"
        prompt += "Mantén toda la respuesta en español.\n"

        if tone == 'sarcastic':
            prompt += "Destaca lo absurdo o gracioso y presenta los puntos clave de forma clara pero irónica.\n"
        elif tone == 'ironic':
            prompt += "Usa ironía sutil para señalar contradicciones o aspectos curiosos de la conversación.\n"
        elif tone == 'absurd':
            prompt += "Incluye metáforas extrañas o comparaciones surrealistas que sorprendan al lector.\n"

    elif language == 'en':
        prompt = f"You are an assistant that summarizes conversations with a {tone_desc['en'][tone]} tone.\n"
        prompt += f"Your task is to generate a {length_desc['en'][length]} summary, {names_text['en'][include_names]}.\n"
        prompt += "Keep the entire response in English.\n"

        if tone == 'sarcastic':
            prompt += "Highlight the absurd or funny aspects and present key points clearly but ironically.\n"
        elif tone == 'ironic':
            prompt += "Use subtle irony to point out contradictions or curious aspects of the conversation.\n"
        elif tone == 'absurd':
            prompt += "Include strange metaphors or surreal comparisons that surprise the reader.\n"

    elif language == 'fr':
        prompt = f"Vous êtes un assistant qui résume les conversations avec un ton {tone_desc['fr'][tone]}.\n"
        prompt += f"Votre tâche est de générer un résumé {length_desc['fr'][length]}, {names_text['fr'][include_names]}.\n"
        prompt += "Gardez toute la réponse en français.\n"

        if tone == 'sarcastic':
            prompt += "Mettez en évidence les aspects absurdes ou drôles et présentez les points clés de manière claire mais ironique.\n"
        elif tone == 'ironic':
            prompt += "Utilisez une ironie subtile pour souligner les contradictions ou les aspects curieux de la conversation.\n"
        elif tone == 'absurd':
            prompt += "Incluez des métaphores étranges ou des comparaisons surréalistes qui surprennent le lecteur.\n"

    elif language == 'pt':
        prompt = f"Você é um assistente que resume conversas com um tom {tone_desc['pt'][tone]}.\n"
        prompt += f"Sua tarefa é gerar um resumo {length_desc['pt'][length]}, {names_text['pt'][include_names]}.\n"
        prompt += "Mantenha toda a resposta em português.\n"

        if tone == 'sarcastic':
            prompt += "Destaque os aspectos absurdos ou engraçados e apresente os pontos-chave de forma clara, mas irônica.\n"
        elif tone == 'ironic':
            prompt += "Use ironia sutil para apontar contradições ou aspectos curiosos da conversa.\n"
        elif tone == 'absurd':
            prompt += "Inclua metáforas estranhas ou comparações surreais que surpreendam o leitor.\n"

    # Add common formatting instructions for all languages
    if language == 'es':
        prompt += "\nFormato del resumen:\n"
        prompt += "- Usa emojis apropiados para hacer el resumen más visual\n"
        prompt += "- Estructura la información de manera clara y organizada\n"
        prompt += "- NUNCA hagas referencia a IDs de mensajes (ej. #360)\n"
    elif language == 'en':
        prompt += "\nSummary format:\n"
        prompt += "- Use appropriate emojis to make the summary more visual\n"
        prompt += "- Structure the information clearly and organized\n"
        prompt += "- NEVER reference message IDs (e.g., #360)\n"
    elif language == 'fr':
        prompt += "\nFormat du résumé:\n"
        prompt += "- Utilisez des emojis appropriés pour rendre le résumé plus visuel\n"
        prompt += "- Structurez l'information de manière claire et organisée\n"
        prompt += "- NE jamais faire référence aux IDs de messages (ex. #360)\n"
    elif language == 'pt':
        prompt += "\nFormato do resumo:\n"
        prompt += "- Use emojis apropriados para tornar o resumo mais visual\n"
        prompt += "- Estruture a informação de forma clara e organizada\n"
        prompt += "- NUNCA faça referência a IDs de mensagens (ex. #360)\n"

    return prompt
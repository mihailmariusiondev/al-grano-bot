# bot/prompts/prompt_modifiers.py
from typing import Dict

def generate_tone_modifier(tone: str) -> str:
    """Generates the tone instruction string."""
    tones = {
        "neutral": (
            "The summary must have a neutral and objective tone.\n"
            "Examples:\n"
            "- The report presents facts without bias.\n"
            "- Opinions are omitted, focusing only on what happened.\n"
            "- Events are described objectively."
        ),
        "informal": (
            "The summary must have a casual and friendly tone.\n"
            "Examples:\n"
            "- Hey! Here's the gist of the chat.\n"
            "- No fancy words, just straight talk.\n"
            "- Let's keep it casual and clear."
        ),
        "sarcastic": (
            "The summary must have a sarcastic and witty tone, subtly mocking the conversation's absurdities.\n"
            "Examples:\n"
            "- Sure, because that idea worked great last time.\n"
            "- Wow, everyone definitely stayed on topic, right?\n"
            "- Yeah, absolutely zero drama here."
        ),
        "colega": (
            "Summarize like you're that sarcastic friend who read everything and is telling someone who's late to the chat what happened. Exaggerate just enough, throw in some playful jabs, ironize with wit, and don't hold back from pointing out stupid stuff. Don't be neutral: be sharp, but fun. Keep the tone ruthless but friendly, like that colleague who tells you the office gossip.\n"
            "Examples:\n"
            "- Tío, te resumo rapidito lo que pasó.\n"
            "- Estos se lían a hablar y ni te imaginas.\n"
            "- Pues nada, te cuento lo jugoso sin filtros."
        ),
        "ironic": (
            "The summary must have a clever, ironic tone, pointing out contradictions or hidden meanings.\n"
            "Examples:\n"
            "- Qué sorpresa que todo saliera al revés.\n"
            "- Sí, porque obviamente todos sabían lo que hacían.\n"
            "- Claramente era la mejor estrategia… o no."
        ),
        "absurd": (
            "The summary must have a surreal and absurd tone, using strange metaphors or comparisons.\n"
            "Examples:\n"
            "- Imagina un perro volando y narrando la escena.\n"
            "- Las ideas se mezclan como sopa de marcianos.\n"
            "- Nada tiene sentido, pero ahí está lo divertido."
        ),
        "macarra": (
            "Usa un tono macarra, directo y callejero.\n"
            "Examples:\n"
            "- The Bull dice que esta a tope natural pero lleva mas quimica que un laboratorio de Breaking Bad.\n"
            "- Pepe y Carlos debaten piernas como si fueran ingenieros y acaban con biceps de pasatiempo.\n"
            "- MoroBugas llora porque no hay maquina femoral y parece que le quitan la tele."
        ),
        "cunao": (
            "Usa el tono cuñao de bar, sabelotodo y exagerado.\n"
            "Examples:\n"
            "- Eso del oro es de pardillos yo con el SP500 me hago rico antes de que un okupa toque mi puerta.\n"
            "- Natural es quien no mea fuera de la cazadora todo lo demas es postureo.\n"
            "- Sexo importante dice en mis tiempos un polvo era un polvo y punto."
        ),
        "hijoputesco": (
            "Un tono hijoputesco, lleno de mala leche y humor negro.\n"
            "Examples:\n"
            "- Jorge sigue sin enterarse de nada y su cerebro se lo agradece.\n"
            "- Pepe se casa entre maquinas de gym y su novia va a flipar con su romanticismo de polilla.\n"
            "- Barbarroja reparte consejos criminales como quien vende churros en la puerta de un cole."
        ),
        "misantropo": (
            "Tono misántropo existencial, desencantado con la humanidad.\n"
            "Examples:\n"
            "- Discuten finanzas mientras el mundo se quema a sus pies.\n"
            "- Se creen expertos en nutricion por veinte gramos de almendras.\n"
            "- Esperan que el sexo anal cure el vacio existencial."
        ),
        "cruel": (
            "Tono brutalmente honesto, sin piedad.\n"
            "Examples:\n"
            "- The Bull no es natural ni borracho de Aquarius.\n"
            "- Pepe y Carlos jamas veran un cuadriceps en su vida.\n"
            "- Rafael es pobre en suenos y rico en juicios."
        ),
        "chismoso": (
            "Tono chismoso hijoputa, siempre metiendo cizaña.\n"
            "Examples:\n"
            "- Pepe anuncia boda y sube selfie de gym mas filtrada que un grifo oxidado.\n"
            "- The Bull presume de off con clomid y miente mejor que un politico.\n"
            "- MoroBugas suplica maquina femoral como quien ruega por wifi gratis."
        ),
        "sitcom": (
            "Narrador de sitcom cutre, todo suena a episodio barato.\n"
            "Examples:\n"
            "- Episodio fitness Pepe y Carlos planifican asalto al aductor.\n"
            "- Capitulo romance Pepe pide matrimonio en medio del pasillo del gym.\n"
            "- Sketch criminal Barbarroja intentando colar anabolicos en la maleta."
        ),
        "cinico": (
            "Tono cínico y quemado, lleno de desdén.\n"
            "Examples:\n"
            "- Debaten macro y micro mientras su cuenta bancaria es micro y su ego es macro.\n"
            "- Se creen Rambo con spray y ni en TikTok los ven.\n"
            "- Hacen fitness de instagram sin sudar una gota en la vida real."
        ),
        "observador": (
            "Cabronazo observador, señalando hipocresías.\n"
            "Examples:\n"
            "- Alex predica macros pero su nevera esta vacia.\n"
            "- Pepe quiere boda pero no encuentra pareja ni en Tinder.\n"
            "- MoroBugas busca femoral sentado y no sabe sentarse sin drama."
        ),
        "illuminati": (
            "Cuñao illuminati, obsesionado con conspiraciones.\n"
            "Examples:\n"
            "- El SP500 es tapadera de pufo global de bancos.\n"
            "- La proteina es experimento masivo para controlar cerebros.\n"
            "- Sexo anal es complot demografico siniestro."
        ),
        "sociopata": (
            "Sociopata con gracia, humor retorcido y frio.\n"
            "Examples:\n"
            "- Galahad llora por burnout y el grupo le regala mas drama.\n"
            "- Marius sermonea como monje loco en karaoke.\n"
            "- Alex discute sexo como tratado militar."
        ),
        "psicologo": (
            "Psicologo desquiciado, analiza todo con locura.\n"
            "Examples:\n"
            "- La adiccion de Pepe al gym oculta su apocalipsis interno.\n"
            "- The Bull sufre disonancia cognitiva a cada pinchazo.\n"
            "- Rafael padece delirios de grandeza sin base real."
        ),
        "dios": (
            "Habla como una deidad que da y quita.\n"
            "Examples:\n"
            "- Jorge no se entera hace semanas y su karma le sonríe con indiferencia.\n"
            "- Pepe decide casarse y el universo dicta ironia infinita.\n"
            "- Barbarroja da consejos ilegales y el caos se lo agradece."
        ),
        "roast": (
            "Roast máximo, burla directa y agresiva.\n"
            "Examples:\n"
            "- The Bull es tan natural como donut relleno de clomid.\n"
            "- Pepe tiene mas filtros que cafe de Starbucks.\n"
            "- Rafael construye imperios de plastico y vive en Monopoly sin fichas."
        ),
        "cigala": (
            "Imita el estilo de El Cigala, con duende flamenco.\n"
            "Examples:\n"
            "- Ay mare mia compadre esto es mu fuerte mu fuerte.\n"
            "- Primo tu con esos cuadriceps pareces un jamon de pata negra.\n"
            "- Esto no se puede aguantar cantaor."
        ),
        "kiko": (
            "Habla como Kiko Rivera, callejero y fiestero.\n"
            "Examples:\n"
            "- Yo soy real bro el que me conoce lo sabe.\n"
            "- Tienes mas postureo que una influencer de maquillaje.\n"
            "- No me vengas con mierdas que yo vengo de la tele."
        ),
        "dioni": (
            "Usa el tono pícaro de El Dioni.\n"
            "Examples:\n"
            "- A mi no me pillaron por listo me pillaron por confiado.\n"
            "- Me fui a Brasil con el furgon y el grupo ni se entera.\n"
            "- Los demas roban chicles yo robaria protagonismo."
        ),
        "risitas": (
            "Tono de El Risitas, siempre riendo.\n"
            "Examples:\n"
            "- Cuñaaaooo que me quede sin femoral sentaooo jajajajaj.\n"
            "- Y entonces se me cayo la mancuerna en el pie jajajajaja.\n"
            "- Marius me conto su ikigai y me meoo."
        ),
        "mairena": (
            "Habla como Carmen de Mairena, exagerado y provocador.\n"
            "Examples:\n"
            "- Ay maricon que calentoon tengo.\n"
            "- Metete esa prensa hack por donde te quepa.\n"
            "- Yo soy diva y tu eres un don nadie."
        ),
        "beni": (
            "Tono gaditano de El Beni de Cádiz.\n"
            "Examples:\n"
            "- No es lo mismo toser que tener ganas de vomitar picha.\n"
            "- Esto va al ritmo de mi palmas y tu no sabes ni aplaudir.\n"
            "- Tu dieta es mas triste que una copla rota."
        ),
        "quico": (
            "Imita a Quico de Los Morancos, expresivo y andaluz.\n"
            "Examples:\n"
            "- Mari tu has visto esto que me va a dar un parraque.\n"
            "- Esto es un escandalo mayusculo.\n"
            "- Te lo digo en sevillano si hace falta."
        ),
        "ignatius": (
            "Estilo gritado de Ignatius Farray.\n"
            "Examples:\n"
            "- MIERDAAAA PERO LA VERDAD ES ESTA.\n"
            "- SOY UN POETA DEL CAOS EN ESTE GRUPO.\n"
            "- NO ESCUCHAS NADA PORQUE ESTAS MUERTO POR DENTRO."
        ),
        "broncano": (
            "Habla con el humor seco de David Broncano.\n"
            "Examples:\n"
            "- Bueno bueno a ver que me estas contando animal.\n"
            "- Esto suena a mierdologia pura y dura.\n"
            "- Me da todo igual pero lo voy a comentar."
        ),
        "veneno": (
            "Estilo de La Veneno, directo y descarado.\n"
            "Examples:\n"
            "- Yo soy famosa guapo y tu eres un mierda.\n"
            "- Te lo digo bien clarito maricon.\n"
            "- Tienes mas pedigrí tu abuela que tu puta vida."
        ),
        "gitano": (
            "Tono de gitano vacilón, lleno de arte.\n"
            "Examples:\n"
            "- Tu lo que tienes es falta de hierro de verdad compadre.\n"
            "- Bendito el tapeo que no te cura ni mil sentadillas.\n"
            "- Esto suena a copla mal interpretada."
        ),
        "choni": (
            "Tono choni canela fina, desafiante y colorido.\n"
            "Examples:\n"
            "- No soy toxica cariño soy intensa aprende la diferencia.\n"
            "- Mis uñas valen mas que tu puto gimnasio.\n"
            "- Me lo pones dificil pero me da igual."
        ),
        "cani": (
            "Habla como un cani de polígono.\n"
            "Examples:\n"
            "- Yo por los mios mato entiendes.\n"
            "- Esto es mas rapido que un Renault Twingo.\n"
            "- Me flipa tu ego de supermercado chinos."
        ),
        "camello": (
            "Tono del camello de confianza, vendedor persuasivo.\n"
            "Examples:\n"
            "- Esto es bueno de farmacia sin cortar.\n"
            "- Te lo puedes pinchar en Navidad y no se te caen ni los huevos.\n"
            "- Mi producto es cien por cien garantizado."
        ),
        "payo": (
            "Payo flipao, mezcla de orgullo y chulería.\n"
            "Examples:\n"
            "- Yo soy gitano de corazon hermano mi abuela se llamaba Dolores.\n"
            "- Me flipo con tus excusas de supervivencia.\n"
            "- No tienes arte ni pa un drama."
        ),
        "viejuna": (
            "Tono de la viejuna del bar, quejica y nostálgico.\n"
            "Examples:\n"
            "- Tanto gimnasio y tanta polla y no sabeis ni hacer lentejas.\n"
            "- Antes todo era mejor hasta el pan sabia a pan.\n"
            "- Os criareis a golpe de movil y nadie sabe silenciar."
        ),
        "yonki": (
            "El yonki zen del parque, filosofía callejera.\n"
            "Examples:\n"
            "- El universo conspira hermano pero a veces tambien te da un navajazo.\n"
            "- Mis porros me curan el alma y tu ego me enferma.\n"
            "- Aqui meditamos en el banco y tu no te enteras."
        ),
        "chulo": (
            "Tono chulo de barrio, desafiante y seguro.\n"
            "Examples:\n"
            "- Yo no hablo yo actuo si sabes sabes.\n"
            "- Lo que tu llames biceps yo lo llamo mariconeria.\n"
            "- Esto es mi territorio y tu no pintas nada."
        ),
    }
    return tones.get(tone, tones["neutral"])

def generate_length_modifier(length: str) -> str:
    """Generates the length instruction string."""
    lengths = {
        "short": "The summary should be very concise, limited to 2-3 sentences.",
        "medium": "The summary should be of medium length, around 5-7 sentences.",
        "long": "The summary should be detailed and comprehensive, around 10-15 sentences."
    }
    return lengths.get(length, lengths["medium"])

def generate_names_modifier(include_names: bool) -> str:
    """Generates the participant name instruction string."""
    if include_names:
        return "You must include the names of the participants when attributing points or statements."
    else:
        return "You must not mention any specific participant names; keep the summary anonymous."

def generate_chat_modifiers(config: Dict) -> str:
    """
    Assembles all relevant modifiers for a chat summary based on the config.
    """
    tone = config.get('tone', 'neutral')
    length = config.get('length', 'medium')
    include_names = config.get('include_names', True)

    modifiers = [
        "\n--- Additional Instructions ---",
        generate_tone_modifier(tone),
        generate_length_modifier(length),
        generate_names_modifier(include_names),
        "Use appropriate emojis to make the summary more visual and engaging.",
        "Structure the information clearly, using bullet points or short paragraphs for readability.",
        "NEVER reference message IDs (e.g., #360)."
    ]
    return "\n".join(modifiers)

#***************************************************************#
#                  .                        *                *  #
#                *          MADE BY            .                #
#        *           _____,    _..-=-=-=-=-====--,  *   .       #
#       _         _.'a   /  .-',___,..=--=--==-'`               #
#      ((        ( _     \ /  //___/-=---=----'                 #
#       `         ` `\    /  //---/--==----=-'                  #
#             ,-.    | / \_//-_.'==-==---='       *             #
#      *     (.-.`\  | |'../-'=-=-=-=--'                   .    #
#      .      (' `\`\| //_|-\.`;-~````~,        _               #
#                   \ | \_,_,_\.'        \     .'_`\            #
#     *             `\            ,    , \    || `\\            #
#                 .   \    /   _.--\    \ '._.'/  / |         * #
#                     /  /`---'   \ \   |`'---'   \/            #
#          *         / /'          \ ;-. \                      #
#                 __/ /      *    __) \ ) `|            *       #
#    .           ((='--;)      .  (,___/(,_/                    #
#                *                                        .   . #
#       *                David Mojica S.E                       #
#          GitHub: https://github.com/DavidMojicaDev            #
#     .         Gmail : davidmojicav@gmail.com                  #
#---------------------------------------------------------------#
#            Release version: 1.0 - 25/08/23 (friday)           #
#***************************************************************#

#------------------------------------------------------------------------------------
#Imports
#------------------------------------------------------------------------------------
#Sys - Python libs
import asyncio
import random
import json
import os
import io
#Program libs 
import essentials
from c_player import Player

#------------------------------------------------------------------------------------
#Global variables 
#------------------------------------------------------------------------------------
tiempo_partida   = 180
tiempo_aviso     = 15  #Cada tiempo se le recordarán a los jugadores las letras que pueden usar y el tiempo que les queda.
tiempo_acabando  = 12
tiempo_contador  = None
file             = ""
config           = ""
consonants       = ""
vocals           = ""
q_consonants     = {"min_consonants": 6, "max_consonants": 12} #Siempre tiene que haber una  diferencia de 6 
q_vocals         = {"min_vocals": 1, "max_vocals": 5}          #Siempre tiene que haber una diferencia de 4

#Probabilities 
pesos_consonants   = [0.2, 0.3, 0.3, 0.1, 0.06, 0.03, 0.01]      #Siempre tiene que haber 6 pesos
pesos_vocals       = [0.12,0.40,0.38,0.07,0.03]                  #Cantidad de vocales: 1: 12% 2: 48% 3: 30% 4: 7% 5: 3%
pesos_duplicados   = [0.1, 0.20, 0.20, 0.20, 0.20, 0.1]          # Probabilidades para 0 duplicados, 1 duplicado 2 duplicados, 3dup, 4 dup y 5dup
pesos_puntos_extra = [0.35, 0.25, 0.20, 0.15, 0.1, 0.05]         #puntos extra: 0->  35%, 1->25%, 2-> 20%, 3-> 15%, 4-> 10%, 5-> 5%

#Messages
msg_menu       = "--------JUMBLE---------\n\nWelcome to jumble!\nPlease select your languaje:\n1: English\n2: Español\n\n---> "
top_palabras   = 20

#Emojis
emoji_numbers = ["0️⃣","1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣"]

#Match variables
chars_listos       = {}
chars_display      = []
palabras_posibles  = []
palabras_dichas    = 0
palabras_repetidas = set()

#players
player = Player()

#------------------------------------------------------------------------------------
#Main
#------------------------------------------------------------------------------------
def main():
    #------------------------------------------------------------------------------------
    #Menu principal - Elección de idioma y de archivos
    #------------------------------------------------------------------------------------
    ban = True
    while(ban):
        lang = input(msg_menu)
        if(lang == "1"):
            file   = "EN/package_EN.json"
            config = "EN/config_EN.json"
            ban  = False
        elif(lang == "2"):
            file   = "ES/package_ES.json"
            config = "ES/config_ES.json"
            ban  = False
        else:
            pass
        
    #------------------------------------------------------------------------------------
    #CARGA - archivos externos
    #------------------------------------------------------------------------------------
    try:
        #Intentamos llamar al archivo config
        if os.path.exists(config):
            with io.open(config, encoding="utf-8") as c:
                config     = json.load(c)
                #seleccionamos la cantidad de letras y de duplicados de la partida 
                numero_consonants = random.choices(range(q_consonants["min_consonants"], q_consonants["max_consonants"] + 1), weights=pesos_consonants)[0]
                numero_vocals     = random.choices(range(q_vocals["min_vocals"], q_vocals["max_vocals"] + 1), weights=pesos_vocals)[0]
                numero_duplicados = random.choices(range(6), weights=pesos_duplicados)[0]
                
                consonants = random.sample(config["consonants"], numero_consonants)
                vocals     = random.sample(config["vocals"], numero_vocals)              
                chars      = consonants + vocals
                
                
                #Duplicar letras si hay que duplicarlas
                for _ in range (numero_duplicados):
                    chars.append(random.choice(chars))
                chars      = random.sample(chars, len(chars))   #Desordenar aleatoriamente el orden de los elementos del array
                
                #Comprueba si el archivo de palabras existe.
                if os.path.exists(file):
                    with io.open(file, encoding="utf-8") as f:
                        jfile = json.load(f)
                        cant_validas, lista_validas = essentials.compatibilidad(chars,jfile)
                        #Cargar la lista global de palabras posibles
                        global palabras_posibles
                        palabras_posibles = lista_validas
                    
                    #Otorgar puntuación a cada letra
                    puntos_extras_asignados = {}
                    
                    for char in chars:
                        if char in puntos_extras_asignados:
                            # Reutilizar puntos extras para letras repetidas
                            puntos_extra = puntos_extras_asignados[char]
                        else:
                            # Asignar nuevos puntos extras a letras no repetidas
                            puntos_extra = random.choices(range(1, 7), weights=pesos_puntos_extra)[0]
                            puntos_extras_asignados[char] = puntos_extra
                        pair = {}
                        pair[char] = puntos_extra
                        chars_display.append(pair)
                        chars_listos[char] = puntos_extra
                    
                    #Empezar el juego
                    asyncio.run(__startgame__(cant_validas, config, chars_listos))
                
        #Si el archivo config no existe, creamos uno limpio
        else:
            with open(file,'w', encoding='utf-8') as f:
                json.dump("", f, ensure_ascii=False)       
                
    except(Exception) as error:
        print(f"{error} en primer try")


#------------------------------------------------------------------------------------
#Match - Partida
#------------------------------------------------------------------------------------
async def __startgame__(cant_validas, config, chars):
    """Inicia el juego y maneja la ejecución y el flujo de mensajes.

    Args:
        cant_validas (int): Cantidad de palabras válidas disponibles para el juego.
        config (dict)     : Diccionario de configuración del juego.
        chars (dict)      : Diccionario de caracteres y sus valores asociados.
    """
    #Match load data
    msg_game_start   = random.choice(config["startgame"])
    msg_game_start2  = random.choice(config["startgame_2"])
    msg_game_over    = random.choice(config["gameover"])
    msg_game_over2   = random.choice(config["gameover_larger_words"])
    msg_tiempo_res   = random.choice(config["time_left"])
    
    #Match Welcome print
    print(f'{msg_game_start}\n {msg_tiempo_res} { num_to_emoji(tiempo_partida) } s')
    print_chars(msg_game_start2, num_to_emoji(cant_validas))
    
    #Match Execution
    try:
        #Partida
        await asyncio.wait_for(get_inputs(config["correct"], config["incorrect"], config["repeated"], config["hurry"], config["remember"], config["time_left"], chars, msg_game_start2, cant_validas), timeout=tiempo_partida)
        
    except asyncio.TimeoutError:
        #---endgame y mostrar puntuaciones---#
        print(msg_game_over)
        print(f'-----Puntuaciones-----')
        print(f"Points: { num_to_emoji(player.points) }\nPalabras totales: { num_to_emoji(player.words) }")
        palabras_mas_largas = essentials.seleccionar_palabras_mas_largas(palabras_posibles, top_palabras)
        print(f"{msg_game_over2}")
        if not palabras_mas_largas:
            print("Oops! Too unlucky ://")
        else:
            for palabra in palabras_mas_largas:
                total_points = calcular_puntos(palabra)
                print(f"{palabra} - { num_to_emoji(total_points) }  points")
        
        
async def contador_asincronico(hurry, remember, time_left, msg_gamestart_2, cant_validas):
    """
    Esta función simula un contador asincrónico con avisos y mensajes durante una partida.

    Parámetros:
    hurry (list): Lista de mensajes de prisa.
    remember (list): Lista de mensajes de recordatorio.
    time_left (list): Lista de mensajes sobre el tiempo restante.
    chars (str): Caracteres válidos.
    msg_gamestart_2 (str): Mensaje de inicio de partida.
    cant_validas (int): Cantidad de palabras válidas.
    """
    #tiempo
    global tiempo_partida
    global tiempo_aviso
    tiempo_aviso_copia = tiempo_aviso
    
    while tiempo_partida > 0:
        await asyncio.sleep(1)
        tiempo_partida     -= 1
        tiempo_aviso_copia -= 1
        
        #Tiempo agotándose
        if tiempo_partida == tiempo_acabando:
            print(f"{random.choice(hurry)} {random.choice(time_left)} { num_to_emoji(tiempo_partida) } s")
            
        #Aviso cada cierto tiempo
        if tiempo_aviso_copia == 0:
            print(f"{random.choice(remember)} ")
            print_chars(msg_gamestart_2, num_to_emoji(cant_validas - palabras_dichas))
            print(f"{random.choice(time_left)}: { num_to_emoji(tiempo_partida) } s")
            
            tiempo_aviso_copia = tiempo_aviso
     
async def get_inputs(correct, incorrect, repeated, hurry, remember, time_left, chars, msg_gamestart_2, cant_validas):
    """ Obtiene entradas del usuario de manera asíncrona y realiza el procesamiento de puntos y mensajes.

    Args:
        correct (list)  : Lista de mensajes de respuesta correcta.
        incorrect (list): Lista de mensajes de respuesta incorrecta.
        repeated (list) : Lista de mensajes de respuesta para palabra repetida.
    """
    while True:
        total_points = 0
        ban          = 0
        lop          = asyncio.get_event_loop()
        global tiempo_contador
        
        if tiempo_contador is None or tiempo_contador.done():
            lop             = asyncio.get_event_loop()
            tiempo_contador = lop.create_task(contador_asincronico(hurry, remember, time_left,msg_gamestart_2, cant_validas))
        
        try:
            user_word = await asyncio.wait_for(get_input(), timeout= tiempo_partida)
            #Contamos las palabras en la frase. Si sólo se trata de 1 palabra hacemos el proceso, sino lo ignoramos.
            if len(user_word.split()) == 1:
                
                #Eliminar espacios, tildes y mayusculas de la frase
                user_word = essentials.sanitizar_frase(user_word)
                
                # Verificar si la palabra es válida y procesarla.
                if palabras_posibles.__contains__(user_word):
                    if user_word not in palabras_repetidas:
                        total_points = calcular_puntos(user_word)
                        palabras_repetidas.add(user_word)
                        global palabras_dichas 
                        palabras_dichas += 1
                    else:
                        ban = 2
                else:
                    ban = 1
                
            #Outputs para cada caso de        
            if ban == 0:
                print(f'{random.choice(correct)} + {num_to_emoji(total_points)} points')
                player.__addpoints__(total_points)
            elif ban == 1:
                print(f"{random.choice(incorrect)}")
            elif ban == 2:
                print(f"{random.choice(repeated)}")
                
        except asyncio.TimeoutError:
            break
    
async def get_input():
    """
    Obtiene una entrada del usuario de manera asíncrona.

    Utiliza el bucle de eventos asyncio para ejecutar la función de entrada (input()) en un
    executor en segundo plano, lo que permite que la operación de entrada no bloquee el bucle
    de eventos principal.

    Returns:
        str: La cadena de entrada proporcionada por el usuario.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, "")

#------------------------------------------------------------------------------------
#Miscelanea
#------------------------------------------------------------------------------------
def print_chars(msg, cant_validas):
    """ 
    Imprime los caracteres y sus puntos extras en forma de lista de diccionarios.

    Esta función toma como entrada un mensaje (msg) y la cantidad de palabras válidas (cant_validas) que el usuario puede encontrar.
    Luego recorre la lista de diccionarios chars_display, que contiene los caracteres y sus respectivos puntos extras,
    y los imprime en un formato legible.

    Args:
        msg (str): Mensaje que se imprimirá junto a la cantidad de palabras válidas.
        cant_validas (int): Cantidad de palabras válidas que el usuario puede encontrar.

    Returns:
        None: Esta función no devuelve ningún valor; simplemente imprime la información formateada.
    """
    for dicts in chars_display:
        for char, puntos in dicts.items():
            print(f"{char} - {emoji_numbers[puntos]}")
    print(f'{msg} {cant_validas}')
    
def num_to_emoji(num):
    """
    Convierte un numero a carácteres emoji

    Args:
        num (int): el numero a ser transformado

    Returns:
        emoji: El numero en emoji
    """
    return ' '.join(emoji_numbers[int(n)] for n in str(num))

def calcular_puntos(palabra):
    """
    Calcula los puntos de la palabra de acuerdo a la puntuación vigente.

    Args:
        palabra (str): Palabra a puntuar

    Returns:
        int : puntuación
    """
    total_points = 0
    chars_palabra = [char for char in palabra]
    for char in chars_palabra:
        total_points += chars_listos.get(char, 0)
    return total_points
    
#------------------------------------------------------------------------------------
#Inicio del programa
#------------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
import telebot
import random
from telebot import types

# Usa sempre il tuo token
bot = telebot.TeleBot('7450076372:AAF3lltHr1X4g0svFaqvBwMXcrTkr4CYr4g')

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Ciao! Benvenuto nel bot dei dadi. Scegli quanti dadi e quale tipo lanciare:")
    send_dice_choice(message)

def send_dice_choice(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    dice_types = ['1d6', '1d8', '1d10', '1d12', '1d20', '1d100']
    dice_buttons = [types.InlineKeyboardButton(text=dice, callback_data=dice) for dice in dice_types]
    markup.add(*dice_buttons)
    bot.send_message(message.chat.id, "Scegli il tipo di dado:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ['1d6', '1d8', '1d10', '1d12', '1d20', '1d100'])
def handle_dice_type(call):
    try:
        bot.answer_callback_query(call.id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Errore durante l'answer_callback_query: {e}")
        return
    
    dice_type = call.data
    bot.send_message(call.message.chat.id, f"Hai scelto di lanciare {dice_type}!")

    # Creiamo una tastiera inline per selezionare il numero di dadi
    markup = types.InlineKeyboardMarkup(row_width=3)
    dice_counts = [1, 2, 3, 4, 5]
    dice_buttons = [types.InlineKeyboardButton(text=str(count), callback_data=f"{dice_type}_{count}") for count in dice_counts]
    markup.add(*dice_buttons)
    bot.send_message(call.message.chat.id, "Scegli quanti dadi lanciare:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: '_' in call.data and call.data.split('_')[0] in ['1d6', '1d8', '1d10', '1d12', '1d20', '1d100'])
def handle_dice_count(call):
    try:
        # Rispondi subito al callback query per evitare che scada
        bot.answer_callback_query(call.id)

        dice_type, count = call.data.split('_')
        count = int(count)
        
        # Genera i risultati del lancio dei dadi
        results = [random.randint(1, int(dice_type[2:])) for _ in range(count)]
        total_sum = sum(results)
        
        # Costruisce il messaggio con i dettagli del lancio
        results_text = ", ".join(map(str, results))
        response = f"Hai lanciato {count} dadi {dice_type}: [{results_text}]\nLa somma dei risultati è: {total_sum}"
        
        # Aggiungi il messaggio di successo o fallimento critico se è un singolo lancio di 1d20
        if dice_type == '1d20' and count == 1:
            if results[0] == 20:
                response += "\n**Successo critico!** 🎉"
            elif results[0] == 1:
                response += "\n**Fallimento critico!** 💀"
        
        # Invia il messaggio usando la modalità Markdown per abilitare il grassetto
        bot.send_message(call.message.chat.id, response, parse_mode='Markdown')

        # Dopo aver mostrato il risultato, ripropone la scelta del dado
        bot.send_message(call.message.chat.id, "Vuoi lanciare di nuovo? Scegli il tipo di dado:")
        send_dice_choice(call.message)

    except telebot.apihelper.ApiTelegramException as e:
        print(f"Errore durante l'answer_callback_query: {e}")
        bot.send_message(call.message.chat.id, "Ops! Qualcosa è andato storto. Prova di nuovo.")

# Gestisci messaggi non validi
@bot.message_handler(func=lambda message: True)
def handle_invalid(message):
    bot.reply_to(message, "Per favore, usa i pulsanti per scegliere il tipo di dado e il numero di dadi. I messaggi di testo non sono supportati.")

bot.polling()

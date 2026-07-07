import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from deep_translator import GoogleTranslator

# ============ CONFIGURATION ============
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============ LANGUAGE DATA ============
POPULAR_LANGUAGES = {
    'en': '🇬🇧 English',
    'es': '🇪🇸 Spanish',
    'fr': '🇫🇷 French',
    'de': '🇩🇪 German',
    'it': '🇮🇹 Italian',
    'pt': '🇵🇹 Portuguese',
    'ru': '🇷🇺 Russian',
    'ja': '🇯🇵 Japanese',
    'ko': '🇰🇷 Korean',
    'zh-CN': '🇨🇳 Chinese (Simplified)',
    'ar': '🇸🇦 Arabic',
    'hi': '🇮🇳 Hindi',
    'bn': '🇧🇩 Bengali',
    'ur': '🇵🇰 Urdu',
    'id': '🇮🇩 Indonesian',
    'ms': '🇲🇾 Malay',
    'tl': '🇵🇭 Filipino',
    'vi': '🇻🇳 Vietnamese',
    'th': '🇹🇭 Thai',
    'sw': '🇰🇪 Swahili'
}

# Language codes for deep-translator
LANGUAGE_CODES = {
    'en': 'english',
    'es': 'spanish',
    'fr': 'french',
    'de': 'german',
    'it': 'italian',
    'pt': 'portuguese',
    'ru': 'russian',
    'ja': 'japanese',
    'ko': 'korean',
    'zh-CN': 'chinese (simplified)',
    'ar': 'arabic',
    'hi': 'hindi',
    'bn': 'bengali',
    'ur': 'urdu',
    'id': 'indonesian',
    'ms': 'malay',
    'tl': 'filipino',
    'vi': 'vietnamese',
    'th': 'thai',
    'sw': 'swahili'
}

# ============ COMMAND HANDLERS ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    current_lang = context.user_data.get('target_lang', 'en')
    current_name = POPULAR_LANGUAGES.get(current_lang, 'English')
    
    welcome_text = (
        f"👋 *Hello {user.first_name}!*\n\n"
        "🌍 *Welcome to Language Translator Bot*\n\n"
        "I can translate text between 100+ languages instantly!\n\n"
        "📌 *Quick Commands:*\n"
        "• `/lang` - Change translation language\n"
        "• `/detect` - Detect text language\n"
        "• `/languages` - See all supported languages\n"
        "• `/help` - Get detailed help\n\n"
        "💡 *Just send me any text* and I'll translate it!\n"
        f"📍 Current target language: *{current_name}*"
    )
    
    keyboard = [
        [InlineKeyboardButton("🌐 Change Language", callback_data='change_lang')],
        [InlineKeyboardButton("🔍 Detect Language", callback_data='detect_lang')],
        [InlineKeyboardButton("📖 View Languages", callback_data='list_lang')],
        [InlineKeyboardButton("❓ Help", callback_data='help_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "🆘 *Help Guide*\n\n"
        "📝 *How to Translate:*\n"
        "Simply send any text message and I'll translate it.\n\n"
        "🌐 *Change Target Language:*\n"
        "Use `/lang` or click the 'Change Language' button.\n\n"
        "🔍 *Detect Language:*\n"
        "Use `/detect` to identify the language of any text.\n\n"
        "📋 *View All Languages:*\n"
        "Use `/languages` to see all supported languages.\n\n"
        "⚡ *Quick Tips:*\n"
        "• I auto-detect the source language\n"
        "• Your language preference is saved\n"
        "• Maximum 500 characters per translation\n\n"
        "⚠️ *Note:* This bot uses Google Translate's free API."
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /lang command"""
    keyboard = []
    row = []
    
    for code, name in POPULAR_LANGUAGES.items():
        row.append(InlineKeyboardButton(name, callback_data=f'lang_{code}'))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("📖 All Languages", callback_data='list_lang')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    current_lang = context.user_data.get('target_lang', 'en')
    current_name = POPULAR_LANGUAGES.get(current_lang, 'English')
    
    await update.message.reply_text(
        f"🌐 *Select Target Language*\n\n"
        f"Current: *{current_name}*\n\n"
        "Choose a language to translate into:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def detect_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /detect command"""
    context.user_data['detect_mode'] = True
    await update.message.reply_text(
        "🔍 *Language Detector Mode*\n\n"
        "Send me any text and I'll detect its language.\n"
        "Type /cancel to exit detection mode."
    )

async def list_languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /languages command"""
    lang_list = []
    for code, name in POPULAR_LANGUAGES.items():
        lang_list.append(f"• {name} (`{code}`)")
    
    await update.message.reply_text(
        f"📖 *Popular Languages ({len(POPULAR_LANGUAGES)})*\n\n{chr(10).join(lang_list)}",
        parse_mode='Markdown'
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command"""
    if context.user_data.get('detect_mode'):
        context.user_data['detect_mode'] = False
        await update.message.reply_text("✅ Detection mode cancelled.")
    else:
        await update.message.reply_text("ℹ️ Nothing to cancel.")

# ============ CALLBACK HANDLERS ============

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button presses"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == 'change_lang':
        keyboard = []
        row = []
        for code, name in POPULAR_LANGUAGES.items():
            row.append(InlineKeyboardButton(name, callback_data=f'lang_{code}'))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("📖 All Languages", callback_data='list_lang')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🌐 *Select Target Language*\n\nChoose a language:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif data == 'detect_lang':
        context.user_data['detect_mode'] = True
        await query.edit_message_text(
            "🔍 *Language Detector Mode*\n\n"
            "Send me any text and I'll detect its language."
        )
    
    elif data == 'list_lang':
        lang_list = []
        for code, name in list(POPULAR_LANGUAGES.items())[:20]:
            lang_list.append(f"• {name} (`{code}`)")
        lang_list.append("\n...and more languages available via /languages")
        
        await query.edit_message_text(
            f"📖 *Popular Languages*\n\n{chr(10).join(lang_list)}",
            parse_mode='Markdown'
        )
    
    elif data == 'help_menu':
        help_text = (
            "🆘 *Help Guide*\n\n"
            "📝 *How to Translate:* Send any text\n"
            "🌐 *Change Language:* Use /lang\n"
            "🔍 *Detect Language:* Use /detect\n"
            "📋 *View Languages:* Use /languages\n\n"
            "Your language preference is saved for future translations!"
        )
        await query.edit_message_text(help_text, parse_mode='Markdown')
    
    elif data.startswith('lang_'):
        lang_code = data.replace('lang_', '')
        context.user_data['target_lang'] = lang_code
        lang_name = POPULAR_LANGUAGES.get(lang_code, lang_code)
        
        await query.edit_message_text(
            f"✅ *Language Updated!*\n\n"
            f"Now translating to: *{lang_name}*\n\n"
            f"📍 Send me any text to translate.\n"
            f"You can change it anytime using /lang."
        )

# ============ MESSAGE HANDLERS ============

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages"""
    text = update.message.text
    
    # ===== DETECTION MODE =====
    if context.user_data.get('detect_mode'):
        try:
            # Use deep-translator's built-in detection
            detector = GoogleTranslator(source='auto', target='en')
            detected = detector.detect(text)
            
            lang_name = POPULAR_LANGUAGES.get(detected, detected)
            
            sample = text[:200] + ('...' if len(text) > 200 else '')
            
            await update.message.reply_text(
                f"🔍 *Detection Result*\n\n"
                f"📝 Language: *{lang_name}*\n"
                f"🔖 Code: `{detected}`\n\n"
                f"📄 Text:\n\"{sample}\""
            )
            context.user_data['detect_mode'] = False
        except Exception as e:
            await update.message.reply_text(f"❌ Error detecting language: {str(e)}")
            context.user_data['detect_mode'] = False
        return
    
    # ===== TRANSLATION MODE =====
    target_lang = context.user_data.get('target_lang', 'en')
    
    try:
        # Show typing indicator
        await update.message.chat.send_action(action="typing")
        
        # Translate using deep-translator
        translator = GoogleTranslator(source='auto', target=target_lang)
        translated = translator.translate(text)
        
        # Get language name for display
        target_name = POPULAR_LANGUAGES.get(target_lang, target_lang)
        
        # Prepare response
        original = text[:500] + ('...' if len(text) > 500 else '')
        translated_text = translated[:500]
        
        response = (
            f"🌍 *Translation Complete*\n\n"
            f"📝 *Original:*\n{original}\n\n"
            f"✅ *Translated* ({target_name}):\n{translated_text}"
        )
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        await update.message.reply_text(
            "❌ *Translation Failed*\n\n"
            "Sorry, I couldn't translate that text. Please try again.",
            parse_mode='Markdown'
        )

# ============ ERROR HANDLER ============

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error: {context.error}")

# ============ MAIN FUNCTION ============

def main():
    """Start the bot"""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN environment variable not set!")
        return
    
    logger.info("🚀 Starting Language Translator Bot...")
    
    application = Application.builder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("lang", set_language))
    application.add_handler(CommandHandler("detect", detect_language))
    application.add_handler(CommandHandler("languages", list_languages))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.add_error_handler(error_handler)
    
    logger.info("✅ Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

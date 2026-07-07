import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from googletrans import Translator, LANGUAGES

# ============ CONFIGURATION ============
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize translator
translator = Translator()

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
    'zh-cn': '🇨🇳 Chinese (Simplified)',
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

# ============ COMMAND HANDLERS ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - Show welcome message"""
    user = update.effective_user
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
        f"📍 Current target language: *{get_language_name(context)}*"
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
    """Handle /lang command - Show language selection"""
    keyboard = []
    row = []
    
    for code, name in POPULAR_LANGUAGES.items():
        row.append(InlineKeyboardButton(name, callback_data=f'lang_{code}'))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    # Add a button to see all languages
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
    # Get all languages from googletrans
    all_langs = []
    for code, name in LANGUAGES.items():
        all_langs.append(f"• `{code}` - {name.title()}")
    
    # Split into chunks
    chunks = []
    chunk = []
    for lang in all_langs:
        chunk.append(lang)
        if len(chunk) >= 25:
            chunks.append('\n'.join(chunk))
            chunk = []
    if chunk:
        chunks.append('\n'.join(chunk))
    
    await update.message.reply_text(
        f"📖 *Supported Languages ({len(LANGUAGES)})*\n\n{chunks[0]}",
        parse_mode='Markdown'
    )
    
    # Send remaining chunks
    for chunk in chunks[1:]:
        await update.message.reply_text(chunk, parse_mode='Markdown')

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command"""
    if context.user_data.get('detect_mode'):
        context.user_data['detect_mode'] = False
        await update.message.reply_text("✅ Detection mode cancelled.")
    else:
        await update.message.reply_text("ℹ️ Nothing to cancel.")

# ============ HELPER FUNCTIONS ============

def get_language_name(context: ContextTypes.DEFAULT_TYPE) -> str:
    """Get the name of the user's current target language"""
    lang_code = context.user_data.get('target_lang', 'en')
    return POPULAR_LANGUAGES.get(lang_code, 'English')

# ============ CALLBACK HANDLERS ============

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button presses"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    # ===== CHANGE LANGUAGE =====
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
    
    # ===== DETECT LANGUAGE =====
    elif data == 'detect_lang':
        context.user_data['detect_mode'] = True
        await query.edit_message_text(
            "🔍 *Language Detector Mode*\n\n"
            "Send me any text and I'll detect its language."
        )
    
    # ===== LIST LANGUAGES =====
    elif data == 'list_lang':
        lang_list = []
        # Show popular languages first
        for code, name in list(POPULAR_LANGUAGES.items())[:20]:
            lang_list.append(f"• {name} (`{code}`)")
        lang_list.append("\n...and 80+ more languages!")
        
        await query.edit_message_text(
            f"📖 *Popular Languages*\n\n{chr(10).join(lang_list)}\n\n"
            "Use /languages to see the complete list.",
            parse_mode='Markdown'
        )
    
    # ===== HELP MENU =====
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
    
    # ===== SET LANGUAGE =====
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
    user_id = update.effective_user.id
    text = update.message.text
    
    # ===== DETECTION MODE =====
    if context.user_data.get('detect_mode'):
        try:
            detection = translator.detect(text)
            confidence = detection.confidence * 100
            lang_name = LANGUAGES.get(detection.lang, detection.lang).title()
            
            # Get a sample of the text
            sample = text[:200] + ('...' if len(text) > 200 else '')
            
            await update.message.reply_text(
                f"🔍 *Detection Result*\n\n"
                f"📝 Language: *{lang_name}*\n"
                f"🔖 Code: `{detection.lang}`\n"
                f"📊 Confidence: {confidence:.1f}%\n\n"
                f"📄 Text:\n\"{sample}\""
            )
            context.user_data['detect_mode'] = False
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
            context.user_data['detect_mode'] = False
        return
    
    # ===== TRANSLATION MODE =====
    target_lang = context.user_data.get('target_lang', 'en')
    
    try:
        # Show typing indicator
        await update.message.chat.send_action(action="typing")
        
        # Translate
        translation = translator.translate(text, dest=target_lang)
        
        # Get language names
        src_name = LANGUAGES.get(translation.src, translation.src).title()
        tgt_name = LANGUAGES.get(target_lang, target_lang).title()
        
        # Prepare response (limited to 4096 characters)
        original = text[:500] + ('...' if len(text) > 500 else '')
        translated = translation.text[:500]
        
        response = (
            f"🌍 *Translation Complete*\n\n"
            f"📝 *Original* ({src_name}):\n{original}\n\n"
            f"✅ *Translated* ({tgt_name}):\n{translated}"
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
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ Something went wrong. Please try again later."
        )

# ============ MAIN FUNCTION ============

def main():
    """Start the bot"""
    # Get token from environment
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN environment variable not set!")
        logger.error("Please add it in Railway dashboard → Variables tab")
        return
    
    logger.info("🚀 Starting Language Translator Bot...")
    
    # Build application
    application = Application.builder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("lang", set_language))
    application.add_handler(CommandHandler("detect", detect_language))
    application.add_handler(CommandHandler("languages", list_languages))
    application.add_handler(CommandHandler("cancel", cancel))
    
    # Add callback handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add message handler (catch all text messages)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start bot with polling
    logger.info("✅ Bot is running and waiting for messages...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

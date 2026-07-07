# 🌍 Language Translator Bot

A Telegram bot that translates text between 100+ languages using Google Translate.

## 🚀 Features

- Translate text to 20+ popular languages
- Auto-detect source language
- Change target language anytime
- Language detection mode
- Inline keyboard navigation

## 📋 Commands

- `/start` - Welcome message
- `/help` - Help guide
- `/lang` - Change target language
- `/detect` - Detect text language
- `/languages` - View all supported languages
- `/cancel` - Cancel detection mode

## 🛠️ Deployment

This bot is designed for deployment on Railway with GitHub.

### Environment Variables

- `TELEGRAM_BOT_TOKEN` - Your bot token from @BotFather

## 📦 Dependencies

- python-telegram-bot==20.3
- googletrans==4.0.0-rc1

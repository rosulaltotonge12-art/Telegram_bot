# حوّل الصور إلى PDF واحد
    images = [Image.open(p["path"]).convert("RGB") for p in st["photos"]]
    pdf_dir = UPLOADS_DIR / chat_id
    pdf_dir.mkdir(exist_ok=True, parents=True)
    pdf_path = pdf_dir / f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    if len(images) == 1:
        images[0].save(pdf_path, save_all=True)
    else:
        images[0].save(pdf_path, save_all=True, append_images=images[1:])

    # خزّن سجل التسليم
    db["submissions"][chat_id] = {
        "student_id": chat_id,
        "exam": exam_title,
        "submitted_at": submitted_at,
        "photo_count": len(st["photos"]),
        "pdf": pdf_path.as_posix(),
        "graded": False,
    }
    save_db(db)

    await update.message.reply_text(
        f"✅ تم تسليم ورقتك.\nالامتحان: {exam_title}\nعدد الصور: {len(st['photos'])}\nسيتم تحويلها للمصحّح."
    )

    # ارسل الـPDF للمصحح
    target = CORRECTOR_ID_INT or update.effective_chat.id
    caption = (
        f"📥 تسليم جديد للتصحيح\n"
        f"الطالب: {chat_id}\n"
        f"الامتحان: {exam_title}\n"
        f"وقت التسليم: {submitted_at}\n\n"
        f"لإرسال النتيجة للطالب:\n"
        f"/grade {chat_id}  (الدرجة)  (ملاحظة اختيارية)"
    )
    await context.bot.send_document(chat_id=target, document=InputFile(pdf_path.as_posix()), caption=caption)

# ====== أوامر المصحح ======
async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"ID مالتك: {update.effective_user.id}")

# /grade <student_id> <score> [note...]
async def grade_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("الصيغة: /grade <student_id> <الدرجة> [ملاحظة]")
        return
    student_id = args[0]
    score = args[1]
    note = " ".join(args[2:]) if len(args) > 2 else ""

    db = load_db()
    sub = db["submissions"].get(student_id)
    if not sub:
        await update.message.reply_text("ماكو تسليم لهذا الطالب.")
        return

    sub["graded"] = True
    sub["grade"] = score
    sub["note"] = note
    sub["corrector_name"] = CORRECTOR_NAME
    sub["graded_at"] = now_str()
    save_db(db)

    # رسالة للطالب
    txt = (
        "✅ تم تصحيح ورقتك!\n"
        f"📅 تاريخ الامتحان: {sub['submitted_at'].split(' ')[0]}\n"
        f"📊 درجة الامتحان اليومي (فيزياء): {score}\n"
        f"👩‍🏫 اسم المصحّح: {CORRECTOR_NAME}\n"
    )
    if note:
        txt += f"📝 ملاحظة: {note}\n"
    await context.bot.send_message(chat_id=int(student_id), text=txt)

    await update.message.reply_text("تم إرسال النتيجة للطالب ✅")

# ====== تشغيل البوت ======
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("exam", exam_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("finish", finish_cmd))
    app.add_handler(CommandHandler("whoami", whoami))
    app.add_handler(CommandHandler("grade", grade_cmd))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    print("🤖 Bot is running ...")
    app.run_polling()

if name == "main":
    main()

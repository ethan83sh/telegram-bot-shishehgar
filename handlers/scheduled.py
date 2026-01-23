from datetime import datetime
from handlers.live_post import DEFAULT_TEXT

async def show_scheduled_lives(update, context):
    query = update.callback_query
    await query.answer()

    jobs = context.job_queue.jobs()

    if not jobs:
        await query.message.reply_text("هیچ لایوی در صف نیست.")
        return

    # فقط job های مربوط به لایو
    live_jobs = []
    for job in jobs:
        if job.data and "title" in job.data:
            live_jobs.append(job)

    if not live_jobs:
        await query.message.reply_text("هیچ لایوی در صف نیست.")
        return

    # سورت بر اساس زمان
    live_jobs.sort(key=lambda j: j.next_t)

    messages = []
    for job in live_jobs:
        data = job.data
        send_time = job.next_t.strftime("%Y-%m-%d %H:%M")

        text = DEFAULT_TEXT.format(
            title=data["title"],
            link=data["link"]
        )

        block = f"⏰ {send_time}\n\n{text}"
        messages.append(block)

    # اگر زیاد بود، تکی بفرست
    for msg in messages:
        await query.message.reply_text(msg)
